#ifndef BLE_PROVISIONER_H
#define BLE_PROVISIONER_H



//----------------------------------------------------------------------------------
//- INCLUDES
#include <Arduino.h>
#include <NimBLEDevice.h>



//----------------------------------------------------------------------------------
//- VARIABLES GLOBALES
// Configurations
static const char* prefix_of_name          = "RL-CAR-";
// UUIDs du service et des caractéristiques
static const NimBLEUUID SERVICE_UUID       ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f0");
static const NimBLEUUID CHAR_SSID_UUID     ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f1");
static const NimBLEUUID CHAR_PASS_UUID     ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f2");
static const NimBLEUUID CHAR_DEVID_UUID    ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f9");
static const NimBLEUUID CHAR_STATUS_UUID   ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f4");
static const NimBLEUUID CHAR_APPLY_UUID    ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f3");



//----------------------------------------------------------------------------------
//- Classe
class ble_provisioner {
public:
    ble_provisioner();

    void                init();     // crée serveur/service/caractéristiques (mais ne lance pas l’advertising)
    void                start();    // démarre service + advertising
    void                stop();     // stop advertising (+ stop service)

    String              get_ssid() const { return ssid_; }
    String              get_pass() const { return pass_; }
    bool                is_connected() const { return is_connected_; }

private:
    NimBLEServer*       server_         = nullptr;
    NimBLEService*      service_        = nullptr;
    NimBLEAdvertising*  adv_            = nullptr;

    String              ssid_;
    String              pass_;
    bool                is_connected_   = false;
};

#endif // BLE_PROVISIONER_H