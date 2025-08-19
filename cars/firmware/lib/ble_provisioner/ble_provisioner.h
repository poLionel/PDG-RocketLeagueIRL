#ifndef BLE_PROVISIONER_H
#define BLE_PROVISIONER_H



//----------------------------------------------------------------------------------
//- INCLUDES
#include <Arduino.h>
#include <NimBLEDevice.h>



//----------------------------------------------------------------------------------
//- STRUCTURES
// --- codec par défaut (binaire brut) ---
template<typename T>
struct gatt_codec {
    static void set(NimBLECharacteristic* ch, const T& v) {
        if (!ch) return;
            ch->setValue(reinterpret_cast<const uint8_t*>(&v), sizeof(T));
    }
    static T get(NimBLECharacteristic* ch) {
        T v{};
        if (!ch) return v;
        std::string s = ch->getValue();
        if (s.size() >= sizeof(T)) memcpy(&v, s.data(), sizeof(T));
        return v;
    }
};
// spécialisation pratique pour String
template<>
struct gatt_codec<String> {
    static void set(NimBLECharacteristic* ch, const String& v) {
        if (!ch) return; ch->setValue(v.c_str());
    }
    static String get(NimBLECharacteristic* ch) {
        if (!ch) return String(); std::string s = ch->getValue(); return String(s.c_str());
    }
};
// spécialisation pour bool (1 octet 0/1)
template<>
struct gatt_codec<bool> {
    static void set(NimBLECharacteristic* ch, const bool& v) {
        if (!ch) return; uint8_t b = v ? 1 : 0; ch->setValue(&b, 1);
    }
    static bool get(NimBLECharacteristic* ch) {
    if (!ch) return false; std::string s = ch->getValue(); return !s.empty() && s[0] != 0;
    }
};
// --- slot générique ---
template<typename T>
struct gatt_slot {
    T                     value{};         // valeur applicative (cache local)
    NimBLECharacteristic* ch = nullptr;    // caractéristique GATT associée

    void bind(NimBLECharacteristic* c) { ch = c; }

    void set(const T& v, bool notify=false) {
        value = v;
        if (ch) { gatt_codec<T>::set(ch, value); if (notify) ch->notify(); }
    }
    const T& get() const { return value; }
    void publish(bool notify=false) {
        if (ch) { gatt_codec<T>::set(ch, value); if (notify) ch->notify(); }
    }
    void pull() {
        if (ch) value = gatt_codec<T>::get(ch);
    }
    bool is_bound() const { return ch != nullptr; }
    void clear(bool notify=false) { set(T{}, notify); }
};



//----------------------------------------------------------------------------------
//- VARIABLES GLOBALES
// Configurations
static const char* ble_prefix_of_name          = "RL-CAR-";
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

    void                init(const char* device_id = nullptr);
    void                start();
    void                stop();

    String              get_ssid() const { return ssid_.get(); }
    String              get_pass() const { return pass_.get(); }
    String              get_status() const { return status_.get(); }
    String              get_device_id() const { return device_id_.get(); }

    bool                wifi_credentials_available() const { return apply_wifi_credentials_.get(); }
    void                consume_wifi_credentiels(String& ssid, String& pass);
    bool                is_connected() const { return is_connected_; }

private:
    NimBLEServer*       server_         = nullptr;
    NimBLEService*      service_        = nullptr;
    NimBLEAdvertising*  adv_            = nullptr;

    gatt_slot<String>   ssid_;
    gatt_slot<String>   pass_;
    gatt_slot<bool>     apply_wifi_credentials_;

    gatt_slot<String>   status_;
    gatt_slot<String>   device_id_;

    bool                is_connected_   = false;
};

#endif // BLE_PROVISIONER_H