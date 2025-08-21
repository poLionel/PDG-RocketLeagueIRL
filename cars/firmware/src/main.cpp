//----------------------------------------------------------------------------------
// INCLUDES
#include <core.h>
#include "car_pins.h"



//----------------------------------------------------------------------------------
// OBJETS GLOBAUX
ble_provisioner             ble_prov;
wifi_provisioner            wifi_prov;
motor_controller            motor_ctrl({
  GPIO_MOT_A_DIR, GPIO_MOT_A_DIR_PWM, GPIO_MOT_B_DIR, GPIO_MOT_B_DIR_PWM, GPIO_MOT_SLP
});
battery_monitor             battery_mon({
  GPIO_BAT_SENSE, 100000, 100000, 3.3f, 4095, 8, 4.2f, 3.3f
});



//----------------------------------------------------------------------------------
// SETUP
void setup() {
  Serial.begin(115200);
  Serial.println("\n[MAIN] Boot...");
  delay(8000);

  //--------
  //--INIT--
  Serial.println("[MAIN] [MOT] motors controller init");
  motor_ctrl.init();

  Serial.println("[MAIN] [BAT] battery monitor init");
  battery_mon.init();
  battery_mon.read();

  Serial.println("[MAIN] [BLE] provisioner init");
  ble_prov.init();
  ble_prov.start();

  Serial.println("[MAIN] [WIFI] provisioner init");
  wifi_prov.init(ble_prov.get_device_id().c_str());
  
  Serial.printf("[MAIN] device_id = %s\n", wifi_prov.get_device_id().c_str());
  Serial.printf("[MAIN] battery = %f / %f\n", battery_mon.get_volt_value(), battery_mon.get_percent_value());


  //--------
  //--CORE--
  Serial.println("[MAIN] [CORE] core init and start");
  core_init(&ble_prov, &wifi_prov, &motor_ctrl, &battery_mon);
  core_start();
}

//----------------------------------------------------------------------------------
// LOOP (vide)
void loop() {
  vTaskDelay(pdMS_TO_TICKS(1000));
}