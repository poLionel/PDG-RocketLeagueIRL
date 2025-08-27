#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H



//----------------------------------------------------------------------------------
//- INCLUDES
//----------------------------------------------------------------------------------
#include <Arduino.h>



//----------------------------------------------------------------------------------
//- STRUCTURES
//----------------------------------------------------------------------------------
enum class motor_decay_mode {
    slow, fast
};
enum class motor_direction{
    forward, backward,
};
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
                
    void                        drive(float x, motor_direction direction, float speed = 0.7f);

    const motor_component       get_component() const { return cfg_.component; }
    void                        set_decay_mode(motor_decay_mode mode) { decay_mode_ = mode; }
private:
    motor_controller_config     cfg_;
    motor_decay_mode            decay_mode_;

    void                        drive_a(motor_decay_mode mode, motor_direction direction, float speed);
    void                        drive_b(motor_decay_mode mode, motor_direction direction, float speed);
};



#endif //MOTOR_CONTROLLER_H