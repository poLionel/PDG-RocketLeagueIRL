#ifndef CAR_PINS_H
#define CAR_PINS_H



//----------------------------------------------------------------------------------
// DEFINES (PINS)
//----------------------------------------------------------------------------------
// DRIVER MOTEURS
#define     GPIO_MOT_A_DIR           3   // AIN1
#define     GPIO_MOT_A_DIR_PWM       4   // AIN2 (PWM)
#define     GPIO_MOT_B_DIR           1   // BIN1
#define     GPIO_MOT_B_DIR_PWM       2   // BIN2 (PWM)
#define     GPIO_MOT_SLP             44  // SLP (enable)
// MODULE ACCELEROMETRE
#define     GPIO_ACC_SDA             5
#define     GPIO_ACC_SCL             6
// MESURE BATTERY
#define     GPIO_BAT_SENSE           7
// CAMERA
#define     GPIO_CAM_PWDN           -1   // Pas de power-down hardware
#define     GPIO_CAM_RESET          -1   // Pas de reset hardware
#define     GPIO_CAM_XCLK           10   // Horloge XCLK
#define     GPIO_CAM_SIOD           40   // SDA (I2C du capteur)
#define     GPIO_CAM_SIOC           39   // SCL (I2C du capteur)
#define     GPIO_CAM_Y9             48
#define     GPIO_CAM_Y8             11
#define     GPIO_CAM_Y7             12
#define     GPIO_CAM_Y6             14
#define     GPIO_CAM_Y5             16
#define     GPIO_CAM_Y4             18
#define     GPIO_CAM_Y3             17
#define     GPIO_CAM_Y2             15
#define     GPIO_CAM_VSYNC          38
#define     GPIO_CAM_HREF           47
#define     GPIO_CAM_PCLK           13



#endif //CAR_PINS_H