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
static constexpr EventBits_t    BIT_CONNEXION           = (1u << 0);
static constexpr EventBits_t    BIT_BLE                 = (1u << 1);
static constexpr EventBits_t    BIT_WIFI                = (1u << 2);
static constexpr EventBits_t    BIT_RUN                 = (1u << 3);



//----------------------------------------------------------------------------------
// HANDLES & CONTEXTE
//----------------------------------------------------------------------------------
static ble_provisioner*         g_ble                   = nullptr;
static wifi_provisioner*        g_wifi                  = nullptr;
static motor_controller*        g_motor                 = nullptr;
static battery_controller*      g_battery               = nullptr;
static camera_controller*       g_camera                = nullptr;

static EventGroupHandle_t       g_evt                   = nullptr;
static TaskHandle_t             h_task_connector        = nullptr;
static TaskHandle_t             h_task_monitor          = nullptr;
static TaskHandle_t             h_task_hardware         = nullptr;
static TaskHandle_t             h_task_video            = nullptr;



//----------------------------------------------------------------------------------
// STRUCTURES
//----------------------------------------------------------------------------------
struct task_params {
  EventGroupHandle_t    evt;
  EventBits_t           gate_bit;
  uint32_t              period_ms;     // 0 = pas de sleep automatique
  void                  (*on_setup)(void* ctx);      // peut être nullptr
  void                  (*on_loop)(void* ctx);       // doit faire 1 "itération"; peut bloquer si besoin
  void                  (*on_teardown)(void* ctx);   // peut être nullptr
  void*                 ctx;           // contexte optionnel
};


//----------------------------------------------------------------------------------
// PROTOTYPES TÂCHES
//----------------------------------------------------------------------------------
static void                     task_connector(void*);  // attend BLE + creds, connecte Wi-Fi, arme RUN et réveille monitor
static void                     task_monitor(void*);    // surveille BLE/Wi-Fi; sur perte -> coupe RUN, réveille connector, se suspend
static void                     task_hardware(void*);   // réaliser toutes interactions avec le hardware
static void                     task_video(void*);      // serveur MJPEG sur port 81



//----------------------------------------------------------------------------------
// TÂCHES
//----------------------------------------------------------------------------------
////////////////////////////////////////////////////////////////////////////////////
// 0) 
static void gated_task(void* pv) {
  task_params* p = static_cast<task_params*>(pv);
  const char* name = pcTaskGetName(NULL);

  for (;;) {
    // Gate & START
    xEventGroupWaitBits(p->evt, p->gate_bit, pdFALSE, pdTRUE, portMAX_DELAY);
    Serial.printf("[%s] START\n", name);

    // Setup
    if (p->on_setup) p->on_setup(p->ctx);

    // Boucle tant que le bit gate reste levé
    while (xEventGroupGetBits(p->evt) & p->gate_bit) {
      if (p->on_loop) p->on_loop(p->ctx);
      if (p->period_ms > 0) vTaskDelay(pdMS_TO_TICKS(p->period_ms));
    }

    // Teardown & STOP
    if (p->on_teardown) p->on_teardown(p->ctx);
    Serial.printf("[%s] STOP\n", name);
  }
}
////////////////////////////////////////////////////////////////////////////////////
// 1) CONNECTOR — attend BLE + credentials, connecte Wi-Fi, arme le RUN, réveille monitor, se suspend
static void connector_setup(void* ctx) {
  // Nouveau cycle de (re)connexion → nettoyer états
  xEventGroupClearBits(g_evt, BIT_BLE | BIT_WIFI | BIT_RUN);
  Serial.printf("[TASK_CON] setup: états nettoyés\n");
}
static void connector_loop(void* ctx) {
  // a) Attendre BLE connecté
  if (!(xEventGroupGetBits(g_evt) & BIT_BLE)) {
    Serial.printf("[TASK_CON] attente BLE…\n");
    while (!(xEventGroupGetBits(g_evt) & BIT_BLE) &&
           (xEventGroupGetBits(g_evt) & BIT_CONNEXION)) {
      if (g_ble->is_connected()) xEventGroupSetBits(g_evt, BIT_BLE);
      vTaskDelay(pdMS_TO_TICKS(100));
    }
    if (!(xEventGroupGetBits(g_evt) & BIT_CONNEXION)) return; // gate tombé
    Serial.printf("[TASK_CON] BLE : connecté\n");
  }

  // b) Attendre credentials
  Serial.printf("[TASK_CON] attente credentials…\n");
  while (!g_ble->wifi_credentials_available() &&
         (xEventGroupGetBits(g_evt) & BIT_CONNEXION)) {
    if (!g_ble->is_connected()) xEventGroupClearBits(g_evt, BIT_BLE);
    vTaskDelay(pdMS_TO_TICKS(100));
  }
  if (!(xEventGroupGetBits(g_evt) & BIT_CONNEXION)) return;
  if (!g_ble->is_connected()) return; // relancera au tour suivant

  String ssid, pass;
  g_ble->consume_wifi_credentiels(ssid, pass);
  Serial.printf("[TASK_CON] credentials : SSID='%s' PASS='%s'\n", ssid.c_str(), pass.c_str());

  // c) Connexion Wi-Fi (non bloquante) + attente résultat/timeout
  const uint32_t WIFI_TIMEOUT_MS = 15000;
  Serial.printf("[TASK_CON] attente Wi-Fi…\n");
  g_wifi->connect(ssid, pass, 0);
  {
    uint32_t t0 = millis();
    while (!g_wifi->is_connected() &&
           (millis() - t0) < WIFI_TIMEOUT_MS &&
           (xEventGroupGetBits(g_evt) & BIT_CONNEXION)) {
      if (!g_ble->is_connected()) { xEventGroupClearBits(g_evt, BIT_BLE); break; }
      vTaskDelay(pdMS_TO_TICKS(100));
    }
  }
  if (!(xEventGroupGetBits(g_evt) & BIT_CONNEXION)) return;
  if (!g_wifi->is_connected()) {
    Serial.printf("[TASK_CON] Wi-Fi : échec/timeout → retry\n");
    return; // on réessaiera au prochain tour
  }

  // d) Succès → lever états, autoriser RUN, baisser CONNEXION (réveil monitor/hard/video)
  Serial.printf("[TASK_CON] Wi-Fi OK → IP=%s RSSI=%d dBm\n", g_wifi->ip().c_str(), g_wifi->rssi());
  xEventGroupSetBits(g_evt, BIT_WIFI);
  xEventGroupSetBits(g_evt, BIT_RUN);
  xEventGroupClearBits(g_evt, BIT_CONNEXION); // force sortie de la boucle générique
}
static void connector_teardown(void* ctx) {
  Serial.printf("[TASK_CON] veille (attente perte)\n");
}
////////////////////////////////////////////////////////////////////////////////////
// 2) MONITOR — surveille; sur perte, coupe RUN, réveille connector, se suspend
static void monitor_setup(void* ctx) {
  // Rien de spécial
}
static void monitor_loop(void* ctx) {
  bool ble_ok  = g_ble->is_connected();
  bool wifi_ok = g_wifi->is_connected();
  if (!ble_ok || !wifi_ok) {
    Serial.printf("[TASK_MON] perte détectée: BLE=%d WIFI=%d\n", ble_ok, wifi_ok);
    if (!ble_ok)  xEventGroupClearBits(g_evt, BIT_BLE);
    if (!wifi_ok) xEventGroupClearBits(g_evt, BIT_WIFI);

    // stoppe les workers, relance le connecteur
    xEventGroupClearBits(g_evt, BIT_RUN);
    xEventGroupSetBits  (g_evt, BIT_CONNEXION);
    // la boucle générique sortira (gate RUN tombé)
  }
}
static void monitor_teardown(void* ctx) {
  Serial.printf("[TASK_MON] attente reconnexion\n");
}
////////////////////////////////////////////////////////////////////////////////////
// 4) // HARDWARE - réaliser toutes interactions avec le hardware
static void hardware_setup(void* ctx) {
  g_motor->start();
}
static void hardware_loop(void* ctx) {
  // Mesures
  g_battery->read();
  float percent = g_battery->get_percent_value();
  float v_batt  = g_battery->get_volt_value();
  float v_nom   = g_motor->get_component().nominal_voltage;

  // Calculs bornés
  float ratio = (v_nom > 0.0f) ? (v_batt / v_nom) : 0.0f;
  if (ratio < 0.0f) ratio = 0.0f;
  if (ratio > 1.0f) ratio = 1.0f;

  float x_dir = (float)g_ble->get_x_direction() / 100.0f;
  motor_direction y_dir = (g_ble->get_y_direction() == 100 ? motor_direction::forward : motor_direction::backward);
  float speed = ratio * ((float)g_ble->get_speed_direction() / 100.0f);

  // Feedback + action
  g_ble->set_battery_level(percent);
  g_motor->set_decay_mode(g_ble->get_decay_mode() == 0 ? motor_decay_mode::fast : motor_decay_mode::slow);
  g_motor->drive(x_dir, y_dir, speed);

  Serial.printf("Battery: %.2fV (%.0f%%) / y: %.2f / x: %.2f / s: %.2f / dm: %d\n",
                v_batt, percent, ((float)g_ble->get_y_direction()/100.0f), x_dir, speed, g_ble->get_decay_mode());
}
static void hardware_teardown(void* ctx) {
  g_motor->stop();
}
////////////////////////////////////////////////////////////////////////////////////
// 5) // Tâche vidéo: serveur MJPEG sur port 81 ---
struct VideoCtx {
  uint16_t       port = 81;
  WiFiServer*    server = nullptr;
  WiFiClient     client;
};
static VideoCtx g_video_ctx; // contexte partagé
static void video_setup(void* ctxv) {
  auto* ctx = static_cast<VideoCtx*>(ctxv);
  if (!ctx->server) ctx->server = new WiFiServer(ctx->port);
  ctx->server->begin();
  if (g_wifi && g_wifi->is_connected()) {
    Serial.printf("[TASK_VID] MJPEG: http://%s:%u/stream\n", g_wifi->ip().c_str(), ctx->port);
  }
}
static void video_loop(void* ctxv) {
  auto* ctx = static_cast<VideoCtx*>(ctxv);

  // Si pas de client, en accepter un
  if (!ctx->client || !ctx->client.connected()) {
    ctx->client.stop();
    ctx->client = ctx->server->available();
    if (!ctx->client) return; // réessaiera au prochain tour
    ctx->client.setTimeout(2000);
    ctx->client.print(
      "HTTP/1.1 200 OK\r\n"
      "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n"
      "Cache-Control: no-cache\r\n"
      "Connection: close\r\n\r\n");
  }

  // Envoyer UNE frame par itération (période fixe → FPS stable)
  camera_fb_t* fb = g_camera ? g_camera->capture_frame() : nullptr;
  if (!fb) return;

  ctx->client.printf(
    "--frame\r\n"
    "Content-Type: image/jpeg\r\n"
    "Content-Length: %u\r\n\r\n", fb->len);
  size_t written = ctx->client.write(fb->buf, fb->len);
  ctx->client.print("\r\n");
  g_camera->release_frame(fb);

  if (written == 0 || !g_wifi->is_connected()) {
    ctx->client.stop(); // client lent / coupé
  }
}
static void video_teardown(void* ctxv) {
  auto* ctx = static_cast<VideoCtx*>(ctxv);
  if (ctx->server) ctx->server->stop();
  if (ctx->client) ctx->client.stop();
  Serial.printf("[TASK_VID] serveur arrêté\n");
}



//----------------------------------------------------------------------------------
// API
//----------------------------------------------------------------------------------
void core_init(ble_provisioner* ble, wifi_provisioner* wifi, motor_controller* motor, battery_controller* battery, camera_controller* camera) {
  g_ble       = ble;
  g_wifi      = wifi;
  g_motor     = motor;
  g_battery   = battery;
  g_camera    = camera;
  g_evt       = xEventGroupCreate();
}
void core_start() {
  // État initial: tout bas, sauf mode CONNEXION
  xEventGroupClearBits(g_evt, BIT_BLE | BIT_WIFI | BIT_RUN);
  xEventGroupSetBits  (g_evt, BIT_CONNEXION);

  // Paramètres des tâches (statiques pour durée de vie sûre)
  static task_params connector_params {
    .evt        = g_evt,
    .gate_bit   = BIT_CONNEXION,
    .period_ms  = 100,
    .on_setup   = connector_setup,
    .on_loop    = connector_loop,
    .on_teardown= connector_teardown,
    .ctx        = nullptr
  };
  static task_params monitor_params {
    .evt        = g_evt,
    .gate_bit   = BIT_RUN,
    .period_ms  = 100,
    .on_setup   = monitor_setup,
    .on_loop    = monitor_loop,
    .on_teardown= monitor_teardown,
    .ctx        = nullptr
  };
  static task_params hardware_params {
    .evt        = g_evt,
    .gate_bit   = BIT_RUN,
    .period_ms  = 500,
    .on_setup   = hardware_setup,
    .on_loop    = hardware_loop,
    .on_teardown= hardware_teardown,
    .ctx        = nullptr
  };
  static task_params video_params {
    .evt        = g_evt,
    .gate_bit   = BIT_RUN,
    .period_ms  = 66,              // ~15 fps
    .on_setup   = video_setup,
    .on_loop    = video_loop,
    .on_teardown= video_teardown,
    .ctx        = &g_video_ctx
  };

  // Création des tâches (pinnées sur core 1 — ajuste si besoin)
  xTaskCreatePinnedToCore(gated_task, "TASK_CON", 4096, &connector_params, 5, &h_task_connector, 1);
  xTaskCreatePinnedToCore(gated_task, "TASK_MON", 4096, &monitor_params  , 4, &h_task_monitor  , 1);
  xTaskCreatePinnedToCore(gated_task, "TASK_HAW", 4096, &hardware_params , 3, &h_task_hardware , 1);
  xTaskCreatePinnedToCore(gated_task, "TASK_VID", 6144, &video_params    , 2, &h_task_video    , 1);

  // Lancer la tâche "d'entrée"
  xEventGroupSetBits(g_evt, BIT_CONNEXION);
}