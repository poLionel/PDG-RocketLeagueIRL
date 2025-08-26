//----------------------------------------------------------------------------------
//- INCLUDES
#include "motor_controller.h"



//----------------------------------------------------------------------------------
//- CONSTRUCTEURS / DESCTRUCTEURS
motor_controller::motor_controller(motor_controller_config cfg) : 
    cfg_(cfg), decay_mode_(motor_decay_mode::fast) {}



//----------------------------------------------------------------------------------
//- MÉTHODES MEMBRES
void motor_controller::init() {
    pinMode(cfg_.ain1, OUTPUT);
    pinMode(cfg_.ain2, OUTPUT);
    pinMode(cfg_.bin1, OUTPUT);
    pinMode(cfg_.bin2, OUTPUT);
    pinMode(cfg_.slp_pin, OUTPUT);
}
void motor_controller::start() {
    // Réveille le driver et (re)lance si besoin
    digitalWrite(cfg_.slp_pin, HIGH);
}
void motor_controller::stop() {
    // Arrête les moteurs et met en veille le DRV8833
    digitalWrite(cfg_.slp_pin, LOW);
}
void motor_controller::drive(float x, motor_direction direction, float speed) {
    // x: -1.0..+1.0 (gauche/droite)
    // speed: 0.0..1.0 (vitesse max)
    if (x < -1.f) x = -1.f; if (x > 1.f) x = 1.f;
    if (speed < 0.f) speed = 0.f; if (speed > 1.f) speed = 1.f;

    // Mixage différentiel (B = gauche, A = droite)
    // x>0 => tourne à droite (ralentit gauche), x<0 => tourne à gauche (ralentit droite)
    float denom = 1.0f + fabsf(x);
    float ls = speed * (1.0f + x) / denom; // gauche
    float rs = speed * (1.0f - x) / denom; // droite
    // micro-clamp anti flottants (optionnel)
    if (ls < 0.f) ls = 0.f; if (ls > 1.f) ls = 1.f;
    if (rs < 0.f) rs = 0.f; if (rs > 1.f) rs = 1.f;


    // Applique vitesses + sens
    Serial.printf(  "d : %s /dm : %s\n -> ls : %.2f - ld : %d / rs : %.2f - rd : %d\n", 
                    (direction ==  motor_direction::forward ? "forward" : "backward"),
                    (decay_mode_ == motor_decay_mode::fast ? "fast" : "slow"), 
                    ls, (int)(255.0f * ls),
                    rs, (int)(255.0f * rs));

    drive_b(decay_mode_, direction, ls);
    drive_a(decay_mode_, direction, rs);
}
void motor_controller::drive_a(motor_decay_mode mode, motor_direction direction, float speed) {
  if (speed < 0.f) speed = 0.f; if (speed > 1.f) speed = 1.f;

  if (mode == motor_decay_mode::slow) {
    // slow decay: tenir une entrée HIGH, PWM l'autre (duty inversé)
    int duty = (int)(255.0f * (1.0f - speed));
    if (direction == motor_direction::forward) {
      analogWrite(cfg_.ain1, 255);           // tenu HAUT
      analogWrite(cfg_.ain2, duty);            // PWM inversé
    } else { // Backward
      analogWrite(cfg_.ain2, 255);
      analogWrite(cfg_.ain1, duty);
    }
  } else { // motor_decay_mode::fast
    // fast decay: tenir l'autre entrée LOW, PWM l'entrée “drive” (duty direct)
    int duty = (int)(255.0f * speed);
    if (direction == motor_direction::forward) {
      analogWrite(cfg_.ain2, 0);            // tenu BAS
      analogWrite(cfg_.ain1, duty);            // PWM direct
    } else { // Backward
      analogWrite(cfg_.ain1, 0);
      analogWrite(cfg_.ain2, duty);
    }
  }
}

void motor_controller::drive_b(motor_decay_mode mode, motor_direction direction, float speed) {
  if (speed < 0.f) speed = 0.f; if (speed > 1.f) speed = 1.f;

  if (mode == motor_decay_mode::slow) {
    // slow decay: tenir une entrée HIGH, PWM l'autre (duty inversé)
    int duty = (int)(255.0f * (1.0f - speed));
    if (direction == motor_direction::forward) {
      analogWrite(cfg_.bin1, 255);           // tenu HAUT
      analogWrite(cfg_.bin2, duty);            // PWM inversé
    } else { // Backward
      analogWrite(cfg_.bin2, 255);
      analogWrite(cfg_.bin1, duty);
    }
  } else { // motor_decay_mode::fast
    // fast decay: tenir l'autre entrée LOW, PWM l'entrée “drive” (duty direct)
    int duty = (int)(255.0f * speed);
    if (direction == motor_direction::forward) {
      analogWrite(cfg_.bin2, 0);            // tenu BAS
      analogWrite(cfg_.bin1, duty);            // PWM direct
    } else { // Backward
      analogWrite(cfg_.bin1, 0);
      analogWrite(cfg_.bin2, duty);
    }
  }
}
