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
    static bool ble_last_state = false;
    static bool wifi_last_state = false;
    static String last_ssid;
    static String last_pass;

    // Vérifie l’état de connexion
    bool ble_connected = ble_prov.is_connected();
    if (ble_connected != ble_last_state) {
        Serial.printf("[MAIN] [BLE] Connexion %s\n", ble_connected ? "établie" : "perdue");
        ble_last_state = ble_connected;
    }
    bool wifi_connected = wifi_prov.is_connected();
    if(wifi_connected != wifi_last_state){
        Serial.printf("[MAIN] [WFi] Connexion %s\n", wifi_connected ? "établie" : "perdue");
        if (wifi_connected) Serial.printf("[MAIN] [WFi] IP=%s  RSSI=%d dBm\n", wifi_prov.ip().c_str(), wifi_prov.rssi());
        wifi_last_state = wifi_connected;
    }

    // Vérifie si un SSID/PASS ont été reçus et différents de la dernière fois
    if(ble_prov.wifi_credentials_available()){
      String ssid, pass;
      ble_prov.consume_wifi_credentiels(ssid, pass);
      Serial.printf("[MAIN] [BLE] Identifiants reçus → SSID: '%s' | PASS: '%s'\n", ssid.c_str(), pass.c_str());
      Serial.printf("[MAIN] [WFi] Connexion %s\n", wifi_prov.connect(ssid, pass, 15000) ? "établie" : "perdue");
    }
    delay(500);
}
