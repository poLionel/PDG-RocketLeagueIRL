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

static EventGroupHandle_t       g_evt                   = nullptr;
static TaskHandle_t             h_task_connector        = nullptr;
static TaskHandle_t             h_task_monitor          = nullptr;
static TaskHandle_t             h_task_hardware         = nullptr;
//
static TaskHandle_t             h_task_worker           = nullptr;



//----------------------------------------------------------------------------------
// PROTOTYPES TÂCHES
//----------------------------------------------------------------------------------
static void                     task_connector(void*);  // attend BLE + creds, connecte Wi-Fi, arme RUN et réveille monitor
static void                     task_monitor(void*);    // surveille BLE/Wi-Fi; sur perte -> coupe RUN, réveille connector, se suspend
static void                     task_hardware(void*);   // réaliser toutes interactions avec le hardware
//
static void                     task_worker(void*);     // fait le job tant que RUN est set



//----------------------------------------------------------------------------------
// API
//----------------------------------------------------------------------------------
void core_init(ble_provisioner* ble, wifi_provisioner* wifi, motor_controller* motor, battery_monitor* battery) {
  g_ble       = ble;
  g_wifi      = wifi;
  g_motor     = motor;
  g_battery   = battery;
  g_evt       = xEventGroupCreate();
}
void core_start() {
  // Création des tâches (pinnées sur core 1 — ajuste si besoin)
  xTaskCreatePinnedToCore(task_connector  ,"TASK_CON"       ,4096   ,nullptr    ,4  , &h_task_connector   ,1);
  xTaskCreatePinnedToCore(task_monitor    ,"TASK_MON"       ,4096   ,nullptr    ,3  , &h_task_monitor     ,1);
  xTaskCreatePinnedToCore(task_hardware   ,"TASK_HW"        ,4096   ,nullptr    ,2  , &h_task_hardware    ,1);
  xTaskCreatePinnedToCore(task_worker     ,"TASK_WK"        ,4096   ,nullptr    ,1  , &h_task_worker      ,1);

  // Au départ, seul le connector doit travailler
  vTaskSuspend(h_task_monitor);   // monitor attendra la première connexion
  // Le worker attendra BIT_RUN automatiquement
}



//----------------------------------------------------------------------------------
// FONCTION LOCALES
//----------------------------------------------------------------------------------
static void fake_task_tick() {
  static uint32_t t0 = 0;
  if (millis() - t0 >= 1000) {
    t0 = millis();
    Serial.println("[WORKER] doing something...");
  }
}



//----------------------------------------------------------------------------------
// TÂCHES
//----------------------------------------------------------------------------------
// 1) CONNECTOR — attend BLE + credentials, connecte Wi-Fi, arme le RUN, réveille monitor, se suspend
static void task_connector(void*) {
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
  for (;;) {
    Serial.println("[MON] actif (surveillance)...");
    for (;;) {
      bool ble_ok  = g_ble->is_connected();
      bool wifi_ok = g_wifi->is_connected();

      if (!ble_ok || !wifi_ok) {
        Serial.printf("[MON] perte détectée: BLE=%d WIFI=%d\n", ble_ok, wifi_ok);

        if (!ble_ok)  xEventGroupClearBits(g_evt, BIT_BLE);
        if (!wifi_ok) xEventGroupClearBits(g_evt, BIT_WIFI);
        xEventGroupClearBits(g_evt, BIT_RUN);       // le worker s'arrêtera tout seul

        // Option : repartir propre côté Wi-Fi
        // g_wifi->disconnect(false);

        // Réveiller le connector et se suspendre
        xTaskNotifyGive(h_task_connector);
        Serial.println("[MON] suspend → attente reconnection");
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
    // Attendre l'autorisation
    xEventGroupWaitBits(g_evt, BIT_RUN, pdFALSE, pdTRUE, portMAX_DELAY);
    Serial.printf("[%s] START\n", name);

    // Tant que RUN reste set, on travaille
    for(;;){
      EventBits_t bits = xEventGroupGetBits(g_evt);
      if ((bits != BIT_RUN) == 0) {
        Serial.printf("[%s] STOP\n", name);
        break;
      }

      // Récupérer l'état de la batterie
      g_battery->read();
      float battery_level_percent = g_battery->get_percent_value();
      float battery_level_volt = g_battery->get_volt_value();
      float max_value_of_duty_cycle = 3 / battery_level_volt;

      g_ble->set_battery_level(battery_level_percent);

      vTaskDelay(pdMS_TO_TICKS(100));
    }
  }
}

// 3) WORKER — tourne quand BIT_RUN est set; s'arrête quand il est clear
static void task_worker(void*) {
  const char* name = pcTaskGetName(NULL);
  for(;;){
    // Attendre l'autorisation
    xEventGroupWaitBits(g_evt, BIT_RUN, pdFALSE, pdTRUE, portMAX_DELAY);
    Serial.printf("[%s] START\n", name);

    // Tant que RUN reste set, on travaille
    for(;;){
      EventBits_t bits = xEventGroupGetBits(g_evt);
      if ((bits & BIT_RUN) == 0) {
        Serial.println("[WORKER] STOP (RUN cleared)");
        break;
      }
      fake_task_tick();              // -> remplace par ta logique
      vTaskDelay(pdMS_TO_TICKS(50));
    }
  }
}
