#ifndef BLE_PROVISIONER_H
#define BLE_PROVISIONER_H



//----------------------------------------------------------------------------------
//- INCLUDES
#include <ble_defs.h>



//----------------------------------------------------------------------------------
//- Classe
class ble_provisioner {
public:
    ble_provisioner();

    void                init(String device_id);
    void                start();
    void                stop();

    String              get_ssid() const { return ssid_.get(); }
    String              get_pass() const { return pass_.get(); }
    String              get_status() const { return status_.get(); }
    String              get_device_id() const { return device_id_.get(); }
    int8_t              get_x_direction() const { return x_direction_.get(); }
    int8_t              get_y_direction() const { return y_direction_.get(); }
    int8_t              get_speed_direction() const { return speed_direction_.get(); }
    int8_t              get_decay_mode() const { return decay_mode_.get(); }

    void                set_battery_level(uint8_t percent) { battery_.set(percent); battery_.publish(); } 

    bool                wifi_credentials_available() const { return apply_wifi_credentials_.get(); }
    void                consume_wifi_credentiels(String& ssid, String& pass);
    bool                is_connected() const { return is_connected_; }

private:
    NimBLEServer*       server_                         = nullptr;
    NimBLEService*      service_                        = nullptr;
    NimBLEAdvertising*  adv_                            = nullptr;

    gatt_slot<String>   ssid_                           { CHAR_SSID_UUID        , {""} };
    gatt_slot<String>   pass_                           { CHAR_PASS_UUID        , {""} };
    gatt_slot<bool>     apply_wifi_credentials_         { CHAR_APPLY_UUID       , {false} };
    gatt_slot<String>   status_                         { CHAR_STATUS_UUID      , {"idle"} };
    gatt_slot<String>   device_id_                      { CHAR_DEVID_UUID       , {""} };
    gatt_slot<uint8_t>  battery_                        { CHAR_BATTERY_UUID     , {100, 0, 100} };

    gatt_slot<int8_t>   x_direction_                    { CHAR_DIR_X_UUID       , {0, -100, 100} };
    gatt_slot<int8_t>   y_direction_                    { CHAR_DIR_Y_UUID       , {0, -100, 100} };
    gatt_slot<int8_t>   speed_direction_                { CHAR_DIR_SPEED_UUID   , {0, 0, 100} };
    gatt_slot<int8_t>   decay_mode_                     { CHAR_DECAY_MODE_UUID  , {0, 0, 1} };

    bool                is_connected_                   = false;
};

#endif // BLE_PROVISIONER_H