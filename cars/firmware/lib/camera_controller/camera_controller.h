#ifndef CAMERA_CONTROLLER_H
#define CAMERA_CONTROLLER_H



//----------------------------------------------------------------------------------
//- INCLUDES
//----------------------------------------------------------------------------------
#include <Arduino.h>
#include <esp_camera.h>



//----------------------------------------------------------------------------------
//- STRUCTURES
//----------------------------------------------------------------------------------
struct camera_component { 
    const char*                 description;
};
struct camera_controller_config {
    // --- Hardware pins ---
    int8_t                      pwdn;     // Power down (souvent -1)
    int8_t                      reset;    // Reset (souvent -1)
    int8_t                      xclk;     // Horloge XCLK
    int8_t                      sccb_sda; // I2C SDA du capteur
    int8_t                      sccb_scl; // I2C SCL du capteur
    int8_t                      y2;       // DVP Y2..Y9
    int8_t                      y3;
    int8_t                      y4;
    int8_t                      y5;
    int8_t                      y6;
    int8_t                      y7;
    int8_t                      y8;
    int8_t                      y9;
    int8_t                      vsync;
    int8_t                      href;
    int8_t                      pclk;
    // --- Paramètres image ---
    pixformat_t                 pixel_format;   // ex: PIXFORMAT_JPEG
    framesize_t                 frame_size;     // ex: FRAMESIZE_QVGA, VGA…
    int                         jpeg_quality;   // 10..20 (plus petit = meilleure qualité)
    int                         fb_count;       // nb de frame buffers (2 si PSRAM dispo)
    int                         xclk_freq_hz;   // ex: 20000000
    // --- Composant ---
    camera_component            component;
};



//----------------------------------------------------------------------------------
//- Class
//----------------------------------------------------------------------------------
class camera_controller {
public:
    camera_controller(camera_controller_config cfg);

    bool                        init();
    
    bool                        read();

    bool                        get_image(std::vector<uint8_t>& out_jpeg, uint16_t* width = nullptr, uint16_t* height = nullptr);
    const camera_component      get_component() const { return cfg_.component; }

    camera_fb_t*                capture_frame();
    void                        release_frame(camera_fb_t* fb);
private:
    camera_controller_config    cfg_;
};



#endif //CAMERA_CONTROLLER_H