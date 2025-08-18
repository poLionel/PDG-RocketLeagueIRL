//----------------------------------------------------------------------------------
//- INCLUDES
#include "ble_provisioner.h"



//----------------------------------------------------------------------------------
//- CALLBACKS
class write_cb : public NimBLECharacteristicCallbacks {
public:
    write_cb(String* target, const char* label) : target_(target), label_(label) {}
    void onWrite(NimBLECharacteristic* c) override {
        std::string v = c->getValue();
        *target_ = String(v.c_str());
    }
private:
    String* target_;
    const char* label_;
};
class apply_cb : public NimBLECharacteristicCallbacks {
public:
    apply_cb(String* ssid, String* pass) : ssid_(ssid), pass_(pass) {}
    void onWrite(NimBLECharacteristic* c) override {
        NimBLECharacteristic* st = c->getService()->getCharacteristic(CHAR_STATUS_UUID);
        if (ssid_->length() && pass_->length()) {
            st->setValue("ok");
            st->notify();
        } else {
            st->setValue("missing");
            st->notify();
        }
    }
private:
    String* ssid_;
    String* pass_;
};
class server_cb : public NimBLEServerCallbacks {
public:
    server_cb(bool* is_connected) : is_connected_(is_connected) {}
    void onConnect(NimBLEServer* pServer) override {
        *is_connected_ = true;
    }
    void onDisconnect(NimBLEServer* pServer) override {
        *is_connected_ = false;
    }
private:
    bool* is_connected_;
};



//----------------------------------------------------------------------------------
//- CONSTRUCTEURS / DESCTRUCTEURS
ble_provisioner::ble_provisioner() : ssid_(""), pass_("") {

}



//----------------------------------------------------------------------------------
//- MÉTHODES MEMBRES
void ble_provisioner::init(){
    // Nom dynamique basé sur l’adresse MAC
    NimBLEDevice::init(prefix_of_name); // init d'abord
    String name = String(prefix_of_name) + NimBLEDevice::getAddress().toString().c_str();
    NimBLEDevice::setDeviceName(name.c_str());   // met vraiment le nom d’advertising
    NimBLEDevice::setPower(ESP_PWR_LVL_P9, ESP_BLE_PWR_TYPE_DEFAULT);

    // Création du servuer et service
    server_ = NimBLEDevice::createServer();
    server_->setCallbacks(new server_cb(&is_connected_));
    service_ = server_->createService(SERVICE_UUID);

    // Caractéristiques
    // Device ID
    NimBLECharacteristic* ch_dev_id = service_->createCharacteristic(
        CHAR_DEVID_UUID, NIMBLE_PROPERTY::READ);
    ch_dev_id->setValue(name.c_str());
    // Status
    NimBLECharacteristic* ch_status = service_->createCharacteristic(
        CHAR_STATUS_UUID, NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::NOTIFY);
    ch_status->setValue("idle");
    // SSID
    NimBLECharacteristic* ch_ssid = service_->createCharacteristic(
        CHAR_SSID_UUID, NIMBLE_PROPERTY::WRITE);
    ch_ssid->setCallbacks(new write_cb(&ssid_, "SSID"));
    // Password
    NimBLECharacteristic* ch_pass = service_->createCharacteristic(
        CHAR_PASS_UUID, NIMBLE_PROPERTY::WRITE);
    ch_pass->setCallbacks(new write_cb(&pass_, "PASS"));
    // Apply
    NimBLECharacteristic* ch_apply = service_->createCharacteristic(
        CHAR_APPLY_UUID, NIMBLE_PROPERTY::WRITE);
    ch_apply->setCallbacks(new apply_cb(&ssid_, &pass_));
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