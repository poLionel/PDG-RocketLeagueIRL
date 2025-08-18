//----------------------------------------------------------------------------------
//- INCLUDES
#include <Arduino.h>
#include "ble_provisioner.h"
#include "wifi_provisioner.h"

//----------------------------------------------------------------------------------
//- OBJET GLOBAL
ble_provisioner   ble_prov;
wifi_provisioner  wifi_prov;

//----------------------------------------------------------------------------------
//- SETUP
void setup() {
  Serial.begin(115200);
  Serial.println("\n");
  Serial.println("[MAIN] Boot...");

  delay(5000);

  Serial.println("[MAIN] [BLE] provisioner initialisé!");
  ble_prov.init();
  Serial.println("[MAIN] [BLE] provisioner en attente de connexion...");
  ble_prov.start();

  Serial.println("[MAIN] [WFi] provisioner initialisé!");
  wifi_prov.init(ble_prov.get_device_id().c_str());
  Serial.println("[MAIN] [WFi] provisioner en attente de connexion de credentials...");

  Serial.printf("[MAIN] device_id = %s\n", wifi_prov.get_device_id().c_str());
}

//----------------------------------------------------------------------------------
//- LOOP
void loop() {
    static bool last_state = false;
    static String last_ssid;
    static String last_pass;

    // Vérifie l’état de connexion
    bool connected = ble_prov.is_connected();
    if (connected != last_state) {
        Serial.printf("[MAIN] [BLE] Connexion %s\n", connected ? "établie" : "perdue");
        last_state = connected;
    }

    // Vérifie si un SSID/PASS ont été reçus et différents de la dernière fois
    String ssid = ble_prov.get_ssid();
    String pass = ble_prov.get_pass();
    if (ssid.length() > 0 && pass.length() > 0) {
        if (ssid != last_ssid || pass != last_pass) {
            Serial.printf("[MAIN] [BLE] Identifiants reçus → SSID: '%s' | PASS: '%s'\n", ssid.c_str(), pass.c_str());

            bool ok = wifi_prov.connect(ssid, pass, 15000);
            Serial.printf("[MAIN] [WFi] Connexion %s\n", ok ? "établie" : "perdue");
            if (ok) Serial.printf("[MAIN] [WFi] IP=%s  RSSI=%d dBm\n", wifi_prov.ip().c_str(), wifi_prov.rssi());

            last_ssid = ssid;
            last_pass = pass;
        }
    }

    delay(500);
}
