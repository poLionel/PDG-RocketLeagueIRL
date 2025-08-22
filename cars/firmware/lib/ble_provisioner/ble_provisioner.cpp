//----------------------------------------------------------------------------------
//- INCLUDES
#include "ble_provisioner.h"



//----------------------------------------------------------------------------------
//- CALLBACKS
class server_cb : public NimBLEServerCallbacks {
public:
    server_cb(bool* is_connected) : is_connected_(is_connected) {}
    void onConnect(NimBLEServer* pServer) override {
        *is_connected_ = true;
    }
    void onDisconnect(NimBLEServer* pServer) override {
        *is_connected_ = false;
        NimBLEDevice::getAdvertising()->start();
    }
private:
    bool* is_connected_;
};



//----------------------------------------------------------------------------------
//- CONSTRUCTEURS / DESCTRUCTEURS
ble_provisioner::ble_provisioner() {
    ssid_.set_callback(
        new cb_write_ssid(&ssid_, &status_));
    pass_.set_callback(
        new cb_write_pass(&pass_, &status_));
    apply_wifi_credentials_.set_callback(
        new cb_apply_wifi_credentials(&apply_wifi_credentials_, &ssid_, &pass_, &status_));
    status_.set_callback(
        nullptr);
    device_id_.set_callback(
        nullptr);
    battery_.set_callback(
        nullptr);
    x_direction_.set_callback(
        new cb_write_direction(&x_direction_, &status_));
    y_direction_.set_callback(
        new cb_write_direction(&y_direction_, &status_));
    speed_direction_.set_callback(
        new cb_write_direction(&speed_direction_, &status_));
}



//----------------------------------------------------------------------------------
//- MÉTHODES MEMBRES
void ble_provisioner::init(String device_id) {
    // Nom dynamique basé sur l’adresse MAC
    NimBLEDevice::init(device_id.c_str()); // init d'abord
    NimBLEDevice::setDeviceName(device_id.c_str());   // met vraiment le nom d’advertising
    NimBLEDevice::setPower(ESP_PWR_LVL_P9, ESP_BLE_PWR_TYPE_DEFAULT);


    // Création du servuer et service
    server_ = NimBLEDevice::createServer();
    server_->setCallbacks(new server_cb(&is_connected_));
    service_ = server_->createService(SERVICE_UUID);

    // Caractéristiques (creéation)
    ssid_.create(service_, NIMBLE_PROPERTY::WRITE, true);
    pass_.create(service_, NIMBLE_PROPERTY::WRITE, true);
    apply_wifi_credentials_.create(service_, NIMBLE_PROPERTY::WRITE, true);

    device_id_.create(service_, NIMBLE_PROPERTY::READ, true);
    status_.create(service_, NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::NOTIFY, true);
    battery_.create(service_, NIMBLE_PROPERTY::READ, true);
    x_direction_.create(service_, NIMBLE_PROPERTY::WRITE, true);
    y_direction_.create(service_, NIMBLE_PROPERTY::WRITE, true);
    speed_direction_.create(service_, NIMBLE_PROPERTY::WRITE, true);

    // Caractéristiques (autres)
    device_id_.set(device_id);
}
void ble_provisioner::start(){
    if (!service_) return;
    service_->start();

    adv_ = NimBLEDevice::getAdvertising();
    adv_->addServiceUUID(SERVICE_UUID);
    adv_->setScanResponse(true);
    adv_->start();
}
void ble_provisioner::stop() {
    // Arrête proprement l’advertising et le service.
    if (adv_) adv_->stop();
}
void ble_provisioner::consume_wifi_credentiels(String& ssid, String& pass){
    if(apply_wifi_credentials_.get()){
        ssid = ssid_.get();
        pass = pass_.get();
        apply_wifi_credentials_.set(false);
    }
}