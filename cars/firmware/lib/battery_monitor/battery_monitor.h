#ifndef BATTERY_MONITOR_H
#define BATTERY_MONITOR_H



//----------------------------------------------------------------------------------
//- INCLUDES
//----------------------------------------------------------------------------------
#include <Arduino.h>



//----------------------------------------------------------------------------------
//- STRUCTURES
//----------------------------------------------------------------------------------
struct battery_monitor_config {
    // Hardware
    int         adc_pin;
    float       r_battery_side;
    float       r_ground_side;
    uint8_t     samples;
    float       vfull;
    float       vempty;
};



//----------------------------------------------------------------------------------
//- Class
//----------------------------------------------------------------------------------
class battery_monitor {
public:
    battery_monitor(battery_monitor_config cfg);

    void          init();
    void          read();

    float         get_volt_value() const { return battery_value_volt; };
    float         get_percent_value() const { return battery_value_percent; };

private:
    battery_monitor_config  cfg_;
    float                   battery_value_volt        = 0.0f;
    float                   battery_value_percent     = 0.0f;
};



#endif //BATTERY_MONITOR_H