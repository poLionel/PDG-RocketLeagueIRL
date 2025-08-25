#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H



//----------------------------------------------------------------------------------
//- INCLUDES
//----------------------------------------------------------------------------------
#include <Arduino.h>
#include <DRV8833.h>  // lib installée via PlatformIO



//----------------------------------------------------------------------------------
//- STRUCTURES
//----------------------------------------------------------------------------------
struct motor_component {
    const char*                 description;
    float                       nominal_voltage;
    float                       no_load_current;
    float                       no_load_speed_rpm;
};
struct motor_controller_config {
    uint8_t                     ain1;
    uint8_t                     ain2;
    uint8_t                     bin1;
    uint8_t                     bin2;
    uint8_t                     slp_pin;
    motor_component             component;
};



//----------------------------------------------------------------------------------
//- Classe
//----------------------------------------------------------------------------------
class motor_controller {
public:
    motor_controller(motor_controller_config cfg);

    void                        init();
    void                        start();
    void                        stop();
                
    void                        drive(float x, motor::Direction direction, float speed = 0.7f);

private:
    motor_controller_config     cfg_;
    motor::DRV8833              drv;
};



#endif //MOTOR_CONTROLLER_H