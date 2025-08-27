//----------------------------------------------------------------------------------
// INCLUDES
//----------------------------------------------------------------------------------
#include "core.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"



//----------------------------------------------------------------------------------
// BITS D'ETAT (internes au module)
//----------------------------------------------------------------------------------
static constexpr EventBits_t    BIT_BLE                 = (1u << 0);
static constexpr EventBits_t    BIT_WIFI                = (1u << 1);
static constexpr EventBits_t    BIT_RUN                 = (1u << 2); // autorisation du worker



//----------------------------------------------------------------------------------
// HANDLES & CONTEXTE
//----------------------------------------------------------------------------------
static ble_provisioner*         g_ble                   = nullptr;
static wifi_provisioner*        g_wifi                  = nullptr;
static motor_controller*        g_motor                 = nullptr;
static battery_monitor*         g_battery               = nullptr;
static camera_controller*       g_camera                = nullptr;

static EventGroupHandle_t       g_evt                   = nullptr;
static TaskHandle_t             h_task_connector        = nullptr;
static TaskHandle_t             h_task_monitor          = nullptr;
static TaskHandle_t             h_task_hardware         = nullptr;
static TaskHandle_t             h_task_video            = nullptr;



//----------------------------------------------------------------------------------
// PROTOTYPES TÂCHES
//----------------------------------------------------------------------------------
static void                     task_connector(void*);  // attend BLE + creds, connecte Wi-Fi, arme RUN et réveille monitor
static void                     task_monitor(void*);    // surveille BLE/Wi-Fi; sur perte -> coupe RUN, réveille connector, se suspend
static void                     task_hardware(void*);   // réaliser toutes interactions avec le hardware
static void                     task_video(void*);      // serveur MJPEG sur port 81



//----------------------------------------------------------------------------------
// API
//----------------------------------------------------------------------------------
void core_init(ble_provisioner* ble, wifi_provisioner* wifi, motor_controller* motor, battery_monitor* battery, camera_controller* camera) {
  g_ble       = ble;
  g_wifi      = wifi;
  g_motor     = motor;
  g_battery   = battery;
  g_camera    = camera;
  g_evt       = xEventGroupCreate();
}
void core_start() {
  // Création des tâches (pinnées sur core 1 — ajuste si besoin)
  xTaskCreatePinnedToCore(task_connector  ,"TASK_CON"       ,4096   ,nullptr    ,5  , &h_task_connector   ,1);
  xTaskCreatePinnedToCore(task_monitor    ,"TASK_MON"       ,4096   ,nullptr    ,4  , &h_task_monitor     ,1);
  xTaskCreatePinnedToCore(task_video      ,"TASK_VID"       ,6144   ,nullptr    ,3  , &h_task_video       ,1);
  xTaskCreatePinnedToCore(task_hardware   ,"TASK_HW"        ,4096   ,nullptr    ,2  , &h_task_hardware    ,1);

  // Au départ, seul le connector doit travailler
  vTaskSuspend(h_task_monitor);   // monitor attendra la première connexion
  // Le worker attendra BIT_RUN automatiquement
}



//----------------------------------------------------------------------------------
// TÂCHES
//----------------------------------------------------------------------------------
// 1) CONNECTOR — attend BLE + credentials, connecte Wi-Fi, arme le RUN, réveille monitor, se suspend
static void task_connector(void*) {
  const char* name = pcTaskGetName(NULL);
  const uint32_t WIFI_TIMEOUT_MS = 15000;

  for (;;) {
    // a) Attendre qu'un client BLE soit connecté
    Serial.println("[CONN] attente connexion BLE…");
    while (!g_ble->is_connected()) vTaskDelay(pdMS_TO_TICKS(100));
    xEventGroupSetBits(g_evt, BIT_BLE);
    Serial.println("[CONN] BLE connecté");

    // b) Attendre des credentials
    Serial.println("[CONN] attente credentials via BLE…");
    while (!g_ble->wifi_credentials_available()) {
      if (!g_ble->is_connected()) {                 // BLE retombe ? on repart
        xEventGroupClearBits(g_evt, BIT_BLE);
      }
      vTaskDelay(pdMS_TO_TICKS(100));
    }
    if(!g_ble->is_connected()) continue;

    String ssid, pass;
    // NOTE: si ta méthode s'appelle encore consume_wifi_credentiels(), renomme ici.
    g_ble->consume_wifi_credentiels(ssid, pass);
    Serial.printf("[CONN] creds: SSID='%s' PASS='%s'\n", ssid.c_str(), pass.c_str());

    // c) Lancer la connexion Wi-Fi (non bloquante) + attendre résultat ou timeout
    g_wifi->connect(ssid, pass, 0);  // 0 = non bloquant
    Serial.println("[CONN] tentative Wi-Fi…");
    {
      uint32_t t0 = millis();
      while (!g_wifi->is_connected() && (millis() - t0) < WIFI_TIMEOUT_MS) {
        if (!g_ble->is_connected()) {               // si BLE perdue pendant la tentative
          xEventGroupClearBits(g_evt, BIT_BLE);
          break;
        }
        vTaskDelay(pdMS_TO_TICKS(100));
      }
    }
    if (!g_wifi->is_connected()) {
      Serial.println("[CONN] Wi-Fi: échec/timeout → retry");
      continue;                                      // relancer le cycle
    }

    // d) Succès -> signaler états, autoriser le worker, réveiller le monitor
    xEventGroupSetBits(g_evt, BIT_WIFI);
    Serial.printf("[CONN] Wi-Fi OK → IP=%s RSSI=%d dBm\n", g_wifi->ip().c_str(), g_wifi->rssi());
    xEventGroupSetBits(g_evt, BIT_RUN);             // le worker peut tourner
    vTaskResume(h_task_monitor);                    // le monitor commence sa surveillance

    // e) Se suspendre jusqu'à notification du monitor (perte détectée)
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    Serial.println("[CONN] réveillé (perte détectée) → reprise du cycle");

    vTaskDelay(pdMS_TO_TICKS(100));
  }
}

// 2) MONITOR — surveille; sur perte, coupe RUN, réveille connector, se suspend
static void task_monitor(void*) {
  const char* name = pcTaskGetName(NULL);
  for (;;) {
    Serial.printf("[%s] START\n", name);
    for (;;) {
      bool ble_ok  = g_ble->is_connected();
      bool wifi_ok = g_wifi->is_connected();

      if (!ble_ok || !wifi_ok) {
        Serial.printf("[%s] perte détectée: BLE=%d WIFI=%d\n", name, ble_ok, wifi_ok);

        if (!ble_ok)  xEventGroupClearBits(g_evt, BIT_BLE);
        if (!wifi_ok) xEventGroupClearBits(g_evt, BIT_WIFI);
        xEventGroupClearBits(g_evt, BIT_RUN);       // le worker s'arrêtera tout seul

        // Option : repartir propre côté Wi-Fi
        // g_wifi->disconnect(false);

        // Réveiller le connector et se suspendre
        xTaskNotifyGive(h_task_connector);
        Serial.printf("[%s] suspend → attente reconnection\n", name);
        vTaskSuspend(NULL);
        break; // sort de la boucle interne; on sera relancé par vTaskResume()
      }

      vTaskDelay(pdMS_TO_TICKS(200));
    }
  }
}

// 4) // HARDWARE - réaliser toutes interactions avec le hardware
static void task_hardware(void*) {
  const char* name = pcTaskGetName(NULL);
  for(;;){
    g_motor->stop();

    // Attendre l'autorisation
    xEventGroupWaitBits(g_evt, BIT_RUN, pdFALSE, pdTRUE, portMAX_DELAY);
    Serial.printf("[%s] START\n", name);

    // Tant que RUN reste set, on travaille
    g_motor->start();
    for(;;){
      EventBits_t bits = xEventGroupGetBits(g_evt);
      if ((bits & BIT_RUN) == 0) {
        Serial.printf("[%s] STOP\n", name);
        break;
      }

      // Récupérer es données
      g_battery->read();
      float battery_level_percent = g_battery->get_percent_value();

      // Conversion / Calcul des données
      float max_speed = g_motor->get_component().nominal_voltage / g_battery->get_volt_value();
      float x_direction = (float)g_ble->get_x_direction() / 100.0f;
      motor_direction y_direction = (g_ble->get_y_direction() == 100 ? motor_direction::forward : motor_direction::backward);
      float speed = max_speed * ((float)g_ble->get_speed_direction() / 100.0f);

      // Envoie des données
      g_ble->set_battery_level(battery_level_percent);

      // Maj HW
      g_motor->set_decay_mode(g_ble->get_decay_mode() == 0 ? motor_decay_mode::fast : motor_decay_mode::slow);
      g_motor->drive(x_direction, y_direction, speed);
      Serial.printf("Battery : %.2f / y : %.2f / x : %.2f / s : %.2f / dm : %d\n", 
                    g_battery->get_volt_value(), ((float)g_ble->get_y_direction() / 100.0f), x_direction, speed, g_ble->get_decay_mode());
      

      vTaskDelay(pdMS_TO_TICKS(500));
    }
  }
}

// 5) // Tâche vidéo: serveur MJPEG sur port 81 ---
static void task_video(void*) {              // <-- AJOUT
  const char* name = pcTaskGetName(NULL);
  for(;;){
    // Attendre l'autorisation
    xEventGroupWaitBits(g_evt, BIT_RUN, pdFALSE, pdTRUE, portMAX_DELAY);
    Serial.printf("[%s] START\n", name);

    for(;;){
      EventBits_t bits = xEventGroupGetBits(g_evt);
      if ((bits & BIT_RUN) == 0) {
        Serial.printf("[%s] STOP\n", name);
        break;
      }
      
      Serial.printf("[%s] RUNNING\n", name);
      vTaskDelay(pdMS_TO_TICKS(500));
    }
  }
}