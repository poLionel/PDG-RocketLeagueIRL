//----------------------------------------------------------------------------------
//- INCLUDES
//----------------------------------------------------------------------------------
#include "battery_monitor.h"



//----------------------------------------------------------------------------------
//- CONSTRUCTEURS / DESCTRUCTEURS
//----------------------------------------------------------------------------------
battery_monitor::battery_monitor(battery_monitor_config cfg) : cfg_(cfg) {}



//----------------------------------------------------------------------------------
//- MÉTHODES MEMBRES
//----------------------------------------------------------------------------------
void battery_monitor::init() {
    pinMode(cfg_.adc_pin, INPUT);
    gpio_pullup_dis((gpio_num_t)cfg_.adc_pin);
    gpio_pulldown_dis((gpio_num_t)cfg_.adc_pin);
    analogReadResolution(12);
#if defined(ESP32)
    analogSetPinAttenuation(cfg_.adc_pin, ADC_11db);
#endif
}
void battery_monitor::read() {
    uint32_t acc_mV = 0;
    for (uint8_t i = 0; i < cfg_.samples; ++i) {
        acc_mV += analogReadMilliVolts(cfg_.adc_pin);  // <-- calibré eFuse
        delayMicroseconds(150);
    }
    const float v_meas = (acc_mV / float(cfg_.samples)) / 1000.0f; // Volts au milieu du pont
    battery_value_volt = v_meas * ((cfg_.r_battery_side + cfg_.r_ground_side) / cfg_.r_ground_side);
    if (battery_value_volt <= cfg_.vempty) {
        battery_value_percent = 0.0f;
    } else if (battery_value_volt >= cfg_.vfull) {
        battery_value_percent = 100.0f;
    } else {
        const float t = (battery_value_volt - cfg_.vempty) / (cfg_.vfull - cfg_.vempty);
        battery_value_percent = t * 100.0f;
    }
}