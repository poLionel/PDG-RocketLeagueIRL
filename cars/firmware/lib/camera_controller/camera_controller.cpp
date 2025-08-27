//----------------------------------------------------------------------------------
//- INCLUDES
//----------------------------------------------------------------------------------
#include "camera_controller.h"



//----------------------------------------------------------------------------------
//- CONSTRUCTEURS / DESCTRUCTEURS
//----------------------------------------------------------------------------------
camera_controller::camera_controller(camera_controller_config cfg) : 
    cfg_(cfg) {}



//----------------------------------------------------------------------------------
//- MÉTHODES MEMBRES
//----------------------------------------------------------------------------------
bool camera_controller::init() {
    camera_config_t c = {};
    c.ledc_channel = LEDC_CHANNEL_0;
    c.ledc_timer   = LEDC_TIMER_0;
    
    c.pin_pwdn     = cfg_.pins.pwdn;
    c.pin_reset    = cfg_.pins.reset;
    c.pin_xclk     = cfg_.pins.xclk;
    c.pin_sscb_sda = cfg_.pins.sccb_sda;
    c.pin_sscb_scl = cfg_.pins.sccb_scl;
    c.pin_d0       = cfg_.pins.y2;
    c.pin_d1       = cfg_.pins.y3;
    c.pin_d2       = cfg_.pins.y4;
    c.pin_d3       = cfg_.pins.y5;
    c.pin_d4       = cfg_.pins.y6;
    c.pin_d5       = cfg_.pins.y7;
    c.pin_d6       = cfg_.pins.y8;
    c.pin_d7       = cfg_.pins.y9;
    c.pin_vsync    = cfg_.pins.vsync;
    c.pin_href     = cfg_.pins.href;
    c.pin_pclk     = cfg_.pins.pclk;

    c.xclk_freq_hz = cfg_.settings.xclk_freq_hz;
    c.pixel_format = cfg_.settings.pixel_format;
    c.frame_size   = cfg_.settings.frame_size;
    c.jpeg_quality = cfg_.settings.jpeg_quality;
    c.fb_count     = cfg_.settings.fb_count;

    c.grab_mode    = CAMERA_GRAB_WHEN_EMPTY; // bon défaut

    esp_err_t err = esp_camera_init(&c);
    if (err != ESP_OK) return false;

    // Réglages par défaut (miroir/flip souvent nécessaires sur XIAO Sense)
    if (sensor_t* s = esp_camera_sensor_get()) {
        s->set_hmirror(s, 1);
        s->set_vflip  (s, 1);
    }

    return true;
}

// Capture/relâche immédiate (sans transport) — utile pour tester la cam
bool camera_controller::read() {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) return false;
    esp_camera_fb_return(fb);
    return true;
}
bool camera_controller::get_image(std::vector<uint8_t>& out_jpeg,
                                  uint16_t* width,
                                  uint16_t* height) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) return false;

    // Copie dans le buffer utilisateur (sûre et simple à consommer)
    out_jpeg.assign(fb->buf, fb->buf + fb->len);

    if (width)  *width  = fb->width;
    if (height) *height = fb->height;

    esp_camera_fb_return(fb);
    return true;
}
camera_fb_t* camera_controller::capture_frame() {
    return esp_camera_fb_get();
}
void camera_controller::release_frame(camera_fb_t* fb) {
    if (fb) esp_camera_fb_return(fb);
}