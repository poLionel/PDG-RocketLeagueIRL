//----------------------------------------------------------------------------------
// INCLUDES
#include <core.h>



//----------------------------------------------------------------------------------
// OBJETS GLOBAUX
ble_provisioner             ble_prov;
wifi_provisioner            wifi_prov;



//----------------------------------------------------------------------------------
// SETUP
void setup() {
  Serial.begin(115200);
  Serial.println("\n[MAIN] Boot...");
  delay(8000);

  Serial.println("[MAIN] [BLE] provisioner init");
  ble_prov.init();
  ble_prov.start();

  Serial.println("[MAIN] [WIFI] provisioner init");
  wifi_prov.init(ble_prov.get_device_id().c_str());
  Serial.printf("[MAIN] device_id = %s\n", wifi_prov.get_device_id().c_str());

  core_init(&ble_prov, &wifi_prov);
  core_start();
}

//----------------------------------------------------------------------------------
// LOOP (vide)
void loop() {
  vTaskDelay(pdMS_TO_TICKS(1000));
}