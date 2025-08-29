//----------------------------------------------------------------------------------
// INCLUDES
//----------------------------------------------------------------------------------
#include "core.h"
#include "core_task.h"




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



//----------------------------------------------------------------------------------
// TÂCHES
//----------------------------------------------------------------------------------
////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////
// 1) CONNECTOR — attend BLE + credentials, connecte Wi-Fi, arme le RUN, réveille monitor, se suspend
static void connector_setup(void* ) {
  // Nouveau cycle de (re)connexion → nettoyer états
  xEventGroupClearBits(g_evt, BIT_BLE | BIT_WIFI | BIT_RUN);
  Serial.printf("[TASK_CON] setup: états nettoyés\n");
}
static void connector_loop(void* ) {
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
static void connector_teardown(void* ) {
  Serial.printf("[TASK_CON] veille (attente perte)\n");
}
////////////////////////////////////////////////////////////////////////////////////
// 2) MONITOR — surveille; sur perte, coupe RUN, réveille connector, se suspend
static void monitor_setup(void* ) { 
  /* rien */ 
}
static void monitor_loop(void* ) {
  bool ble_ok  = g_ble->is_connected();
  bool wifi_ok = g_wifi->is_connected();
  if (!ble_ok || !wifi_ok) {
    Serial.printf("[TASK_MON] perte détectée: BLE=%d WIFI=%d\n", ble_ok, wifi_ok);
    if (!ble_ok)  xEventGroupClearBits(g_evt, BIT_BLE);
    if (!wifi_ok) xEventGroupClearBits(g_evt, BIT_WIFI);

    // stoppe les workers, relance le connecteur
    xEventGroupClearBits(g_evt, BIT_RUN);
    xEventGroupSetBits  (g_evt, BIT_CONNEXION);
  }
}
static void monitor_teardown(void* ) {
  Serial.printf("[TASK_MON] attente reconnexion\n");
}
////////////////////////////////////////////////////////////////////////////////////
// 4) // HARDWARE - réaliser toutes interactions avec le hardware
static void hardware_setup(void* ) {
  g_motor->start();
}
static void hardware_loop(void* ) {
  // Récupérer es données
  g_battery->read();
  float battery_level_percent = g_battery->get_percent_value();

  // Conversion / Calcul des données
  float max_speed = (battery_level_percent < 1.0f ? 0.0f : (g_motor->get_component().nominal_voltage / g_battery->get_volt_value()));
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
}
static void hardware_teardown(void* ) {
  g_motor->stop();
}
////////////////////////////////////////////////////////////////////////////////////
// 5) // Tâche vidéo: serveur MJPEG sur port 81 ---
struct VideoCtx {
  uint16_t       port = 81;
  WiFiServer*    server = nullptr;
  WiFiClient     client;
};
static VideoCtx g_video_ctx;

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
////////////////////////////////////////////////////////////////////////////////////
// 6) // ...



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

  // ---- Instanciation via core_task (settings + component) ----
  static task_settings  set_con { "TASK_CON", 5, 4096, 1, g_evt, BIT_CONNEXION, 100 };
  static task_component cmp_con { connector_setup, connector_loop, connector_teardown, nullptr };
  static core_task      t_con   ( core_task_config{ set_con, cmp_con } );

  static task_settings  set_mon { "TASK_MON", 4, 4096, 1, g_evt, BIT_RUN, 100 };
  static task_component cmp_mon { monitor_setup, monitor_loop, monitor_teardown, nullptr };
  static core_task      t_mon   ( core_task_config{ set_mon, cmp_mon } );

  static task_settings  set_haw { "TASK_HAW", 3, 4096, 1, g_evt, BIT_RUN, 500 };
  static task_component cmp_haw { hardware_setup, hardware_loop, hardware_teardown, nullptr };
  static core_task      t_haw   ( core_task_config{ set_haw, cmp_haw } );

  static task_settings  set_vid { "TASK_VID", 2, 6144, 1, g_evt, BIT_RUN, 66 }; // ~15fps
  static task_component cmp_vid { video_setup, video_loop, video_teardown, &g_video_ctx };
  static core_task      t_vid   ( core_task_config{ set_vid, cmp_vid } );

  // Lancer les tâches
  t_con.start();
  t_mon.start();
  t_haw.start();
  t_vid.start();

  // Déclencher la séquence d'entrée
  xEventGroupSetBits(g_evt, BIT_CONNEXION);
}