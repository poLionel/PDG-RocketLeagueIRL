#ifndef BATTERY_CONTROLLER_H
#define BATTERY_CONTROLLER_H



//----------------------------------------------------------------------------------
//- INCLUDES
//----------------------------------------------------------------------------------
#include <Arduino.h>



//----------------------------------------------------------------------------------
//- STRUCTURES
//----------------------------------------------------------------------------------
struct battery_component { 
    const char*                 description; 
    float                       nominal_voltage; 
    float                       minimum_voltage; 
    float                       maximum_voltage; 
    float                       capacity_mAh; 
};
struct battery_pins {
    uint8_t                     adc;
};
struct battery_settings {
    float                       r_battery_side;
    float                       r_ground_side;
    uint8_t                     samples;
};
struct battery_controller_config {
    // Hardware
    battery_pins                pins;
    battery_settings            settings;
    battery_component           component;
};



//----------------------------------------------------------------------------------
//- Class
//----------------------------------------------------------------------------------
class battery_controller {
public:
    battery_controller(battery_controller_config cfg);

    void                        init();
    
    void                        read();

    float                       get_volt_value() const { return battery_value_volt; };
    float                       get_percent_value() const { return battery_value_percent; };
    const battery_component     get_component() const { return cfg_.component; }
private:
    battery_controller_config   cfg_;
    float                       battery_value_volt        = 0.0f;
    float                       battery_value_percent     = 0.0f;
};



#endif //BATTERY_CONTROLLER_H