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
    analogReadResolution(12);
#if defined(ESP32)
    analogSetPinAttenuation(cfg_.adc_pin, ADC_11db);
#endif
}
void battery_monitor::read() {
    uint32_t acc = 0;
    for (uint8_t i = 0; i < cfg_.samples; ++i) acc += analogRead(cfg_.adc_pin);
    const float raw = float(acc) / float(cfg_.samples);
    const float v_meas = (raw / float(cfg_.adc_max)) * cfg_.vref;

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