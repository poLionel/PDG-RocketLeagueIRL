//----------------------------------------------------------------------------------
//- INCLUDES
//----------------------------------------------------------------------------------
#include "battery_monitor.h"



//----------------------------------------------------------------------------------
//- CONSTRUCTEURS / DESCTRUCTEURS
//----------------------------------------------------------------------------------
battery_monitor::battery_monitor(battery_monitor_config cfg) : 
    cfg_(cfg) {}



//----------------------------------------------------------------------------------
//- MÉTHODES MEMBRES
//----------------------------------------------------------------------------------
void battery_monitor::init() {
    pinMode(cfg_.pins.adc, INPUT);
    gpio_pullup_dis((gpio_num_t)cfg_.pins.adc);
    gpio_pulldown_dis((gpio_num_t)cfg_.pins.adc);
    analogReadResolution(12);
#if defined(ESP32)
    analogSetPinAttenuation(cfg_.pins.adc, ADC_11db);
#endif
}
void battery_monitor::read() {
    uint32_t acc_mV = 0;
    for (uint8_t i = 0; i < cfg_.settings.samples; ++i) {
        acc_mV += analogReadMilliVolts(cfg_.pins.adc);  // <-- calibré eFuse
        delayMicroseconds(150);
    }
    const float v_meas = (acc_mV / float(cfg_.settings.samples)) / 1000.0f; // Volts au milieu du pont
    battery_value_volt = v_meas * ((cfg_.settings.r_battery_side + cfg_.settings.r_ground_side) / cfg_.settings.r_ground_side);
    if (battery_value_volt <= cfg_.component.minimum_voltage) {
        battery_value_percent = 0.0f;
    } else if (battery_value_volt >= cfg_.component.maximum_voltage) {
        battery_value_percent = 100.0f;
    } else {
        const float t = (battery_value_volt - cfg_.component.minimum_voltage) / (cfg_.component.maximum_voltage - cfg_.component.minimum_voltage);
        battery_value_percent = t * 100.0f;
    }
}