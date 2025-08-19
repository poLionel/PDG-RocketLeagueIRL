//----------------------------------------------------------------------------------
//- INCLUDES
#include "ble_provisioner.h"



//----------------------------------------------------------------------------------
//- CALLBACKS
class write_cb : public NimBLECharacteristicCallbacks {
public:
    write_cb(gatt_slot<String>* slot, gatt_slot<String>* status)
    : slot_(slot), status_(status) {}
    void onWrite(NimBLECharacteristic* c) override {
        std::string v = c->getValue();
        slot_->value = String(v.c_str());         // MAJ cache local
    }
private:
    gatt_slot<String>* slot_;
    gatt_slot<String>* status_;
};
class apply_cb : public NimBLECharacteristicCallbacks {
public:
    apply_cb(gatt_slot<bool>* apply, gatt_slot<String>* ssid, gatt_slot<String>* pass, gatt_slot<String>* status)
    : apply_(apply), ssid_(ssid), pass_(pass), status_(status) {}
    void onWrite(NimBLECharacteristic*) override {
        if (!ssid_->get().isEmpty() && !pass_->get().isEmpty()){
            apply_->set(true); // on mémorise le trigger côté app
            status_->set("configured", true);
        }
        else {
            status_->set("idle", true);
        }
    }
private:
    gatt_slot<bool>*   apply_;
    gatt_slot<String>* ssid_;
    gatt_slot<String>* pass_;
    gatt_slot<String>* status_;
};
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

}



//----------------------------------------------------------------------------------
//- MÉTHODES MEMBRES
void ble_provisioner::init(const char* device_id) {
    // Nom dynamique basé sur l’adresse MAC
    NimBLEDevice::init(ble_prefix_of_name); // init d'abord
    String id = (device_id && *device_id) ? String(device_id) : (String(ble_prefix_of_name) + NimBLEDevice::getAddress().toString().c_str());
    NimBLEDevice::setDeviceName(id.c_str());   // met vraiment le nom d’advertising
    NimBLEDevice::setPower(ESP_PWR_LVL_P9, ESP_BLE_PWR_TYPE_DEFAULT);

    // Création du servuer et service
    server_ = NimBLEDevice::createServer();
    server_->setCallbacks(new server_cb(&is_connected_));
    service_ = server_->createService(SERVICE_UUID);

    // Caractéristiques
    // Device ID
    device_id_.bind(service_->createCharacteristic(
        CHAR_DEVID_UUID, NIMBLE_PROPERTY::READ));
    device_id_.set(id);
    // Status
    status_.bind(service_->createCharacteristic(
        CHAR_STATUS_UUID, NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::NOTIFY));
    status_.set("idle");
    // SSID
    ssid_.bind(service_->createCharacteristic(
        CHAR_SSID_UUID, NIMBLE_PROPERTY::WRITE));
    ssid_.set("");
    ssid_.ch->setCallbacks(
        new write_cb(&ssid_, &status_));
    // Password
    pass_.bind(service_->createCharacteristic(
        CHAR_PASS_UUID, NIMBLE_PROPERTY::WRITE));
    pass_.set("");
    pass_.ch->setCallbacks(
        new write_cb(&pass_, &status_));
    // Application des credentials
    apply_wifi_credentials_.bind(service_->createCharacteristic(
        CHAR_APPLY_UUID, NIMBLE_PROPERTY::WRITE));
    apply_wifi_credentials_.set(false);
    apply_wifi_credentials_.ch->setCallbacks(
        new apply_cb(&apply_wifi_credentials_, &ssid_, &pass_, &status_));

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