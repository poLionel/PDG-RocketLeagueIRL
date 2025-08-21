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
struct motor_controller_config {
    uint8_t         ain1;
    uint8_t         ain2;
    uint8_t         bin1;
    uint8_t         bin2;
    uint8_t         slp_pin;
};



//----------------------------------------------------------------------------------
//- Classe
//----------------------------------------------------------------------------------
class motor_controller {
public:
    motor_controller(motor_controller_config cfg)
        : drv(cfg.ain1, cfg.ain2, cfg.bin1, cfg.bin2, cfg.slp_pin) {}

    void        init();
    void        start();
    void        stop();

    void        drive(float x, motor::Direction direction, float speed = 0.7f);

private:
    motor::DRV8833 drv;   // instance du driver
};



#endif //MOTOR_CONTROLLER_H