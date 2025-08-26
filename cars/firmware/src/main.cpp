//----------------------------------------------------------------------------------
// INCLUDES
#include <core.h>
#include "car_pins.h"
#include "car_defines.h"



//----------------------------------------------------------------------------------
// COMPOSANTS
battery_component battery_comp{
  "LP803040 LiPo",
  3.7f,
  3.3f,
  4.2f,
  1000.0f
};
motor_component motor_comp{
  "Micro-moteur N20",
  3.0f,
  0.2f,
  100.0f
};
//----------------------------------------------------------------------------------
// OBJETS GLOBAUX
ble_provisioner             ble_prov;
wifi_provisioner            wifi_prov;
motor_controller            motor_ctrl({
  GPIO_MOT_A_DIR, GPIO_MOT_A_DIR_PWM, GPIO_MOT_B_DIR, GPIO_MOT_B_DIR_PWM, GPIO_MOT_SLP, motor_comp
});
battery_monitor             battery_mon({
  GPIO_BAT_SENSE, 100000, 100000, 8, battery_comp
});



//----------------------------------------------------------------------------------
// FONCTIONS LOCALES
String make_device_id(){
  uint64_t chip_id = ESP.getEfuseMac();
  char buf[17];
  snprintf(buf, sizeof(buf), "%012llX", (unsigned long long)chip_id);
  return (String(DEVICE_ID_PREFIX) + String(buf));
}



//----------------------------------------------------------------------------------
// SETUP
void setup() {
  Serial.begin(115200);
  Serial.println("\n[MAIN] Boot...");
  delay(8000);
  String device_id = make_device_id();


  //--------
  //--INIT--
  Serial.println("[MAIN] [MOT] motors controller init");
  motor_ctrl.init();

  Serial.println("[MAIN] [BAT] battery monitor init");
  battery_mon.init();
  battery_mon.read();

  Serial.println("[MAIN] [BLE] provisioner init");
  ble_prov.init(device_id);
  ble_prov.start();
  ble_prov.set_battery_level(battery_mon.get_percent_value());

  Serial.println("[MAIN] [WIFI] provisioner init");
  wifi_prov.init(device_id);
  
  Serial.printf("[MAIN] device_id = %s\n", device_id.c_str());
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