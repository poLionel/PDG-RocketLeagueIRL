//----------------------------------------------------------------------------------
//- INCLUDES
#include <Arduino.h>
#include "ble_provisioner.h"

//----------------------------------------------------------------------------------
//- OBJET GLOBAL
ble_provisioner prov;

//----------------------------------------------------------------------------------
//- SETUP
void setup() {
  Serial.begin(115200);
  Serial.println("\n");
  Serial.println("[MAIN] Boot...");
  delay(5000);

  Serial.println("[MAIN] BLE provisioner initialisé!");
  prov.init();
  Serial.println("[MAIN] BLE provisioner en attente de connexion...");
  prov.start();
}

//----------------------------------------------------------------------------------
//- LOOP
void loop() {
    static bool last_state = false;
    static String last_ssid;
    static String last_pass;

    // Vérifie l’état de connexion
    bool connected = prov.is_connected();
    if (connected != last_state) {
        Serial.printf("[MAIN] Connexion BLE %s\n", connected ? "établie" : "perdue");
        last_state = connected;
    }

    // Vérifie si un SSID/PASS ont été reçus et différents de la dernière fois
    String ssid = prov.get_ssid();
    String pass = prov.get_pass();
    if (ssid.length() > 0 && pass.length() > 0) {
        if (ssid != last_ssid || pass != last_pass) {
            Serial.printf("[MAIN] Identifiants reçus → SSID: '%s' | PASS: '%s'\n", ssid.c_str(), pass.c_str());
            last_ssid = ssid;
            last_pass = pass;
        }
    }

    delay(500);
}
