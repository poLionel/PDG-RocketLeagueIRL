//----------------------------------------------------------------------------------
//- INCLUDES
#include "motor_controller.h"



//----------------------------------------------------------------------------------
//- CONSTRUCTEURS / DESCTRUCTEURS
motor_controller::motor_controller(motor_controller_config cfg) : 
    cfg_(cfg), drv(cfg.ain1, cfg.ain2, cfg.bin1, cfg.bin2, cfg.slp_pin) {}



//----------------------------------------------------------------------------------
//- MÉTHODES MEMBRES
void motor_controller::init() {
    // Configure le driver et réveille le DRV8833
    drv.setup();      // initialise les ponts + SLP en sortie + wake()
    drv.stopAll();    // sécurité au boot
}
void motor_controller::start() {
    // Réveille le driver et (re)lance si besoin
    drv.wake();
    drv.startAll();
}
void motor_controller::stop() {
    // Arrête les moteurs et met en veille le DRV8833
    drv.stopAll();
    drv.sleep();
}
void motor_controller::drive(float x, motor::Direction direction, float speed) {
    // x: -1.0..+1.0 (gauche/droite)
    // speed: 0.0..1.0 (vitesse max)
    if (x < -1.f) x = -1.f;
    if (x >  1.f) x =  1.f;
    if (speed < 0.f) speed = 0.f;
    if (speed > 1.f) speed = 1.f;

    // Mixage différentiel (B = gauche, A = droite)
    // x>0 => tourne à droite (ralentit gauche), x<0 => tourne à gauche (ralentit droite)
    float left_speed  = speed * (1.0f - x);  // pont B
    float right_speed = speed * (1.0f + x);  // pont A

    // Applique vitesses + sens
    drv.getBridgeB().setSpeed(left_speed,  direction); // gauche
    drv.getBridgeA().setSpeed(right_speed, direction); // droite
}