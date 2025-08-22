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

    void                set_battery_level(uint8_t percent) { battery_.set(percent); battery_.publish(); } 

    bool                wifi_credentials_available() const { return apply_wifi_credentials_.get(); }
    void                consume_wifi_credentiels(String& ssid, String& pass);
    bool                is_connected() const { return is_connected_; }

private:
    NimBLEServer*       server_                         = nullptr;
    NimBLEService*      service_                        = nullptr;
    NimBLEAdvertising*  adv_                            = nullptr;

    gatt_slot<String>   ssid_                           { CHAR_SSID_UUID        , ""};
    gatt_slot<String>   pass_                           { CHAR_PASS_UUID        , ""};
    gatt_slot<bool>     apply_wifi_credentials_         { CHAR_APPLY_UUID       , false };
    gatt_slot<String>   status_                         { CHAR_STATUS_UUID      , "idle" };
    gatt_slot<String>   device_id_                      { CHAR_DEVID_UUID       , "" };
    gatt_slot<uint8_t>  battery_                        { CHAR_BATTERY_UUID     , 100};

    bool                is_connected_                   = false;
};

#endif // BLE_PROVISIONER_H