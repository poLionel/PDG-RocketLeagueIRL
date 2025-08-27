#ifndef BLE_DEFS_H
#define BLE_DEFS_H



//----------------------------------------------------------------------------------
//- INCLUDES
//----------------------------------------------------------------------------------
#include <Arduino.h>
#include <NimBLEDevice.h>
#include <optional>
#include <mutex>



//----------------------------------------------------------------------------------
//- TYPES
//----------------------------------------------------------------------------------
// Codec générique (binaire brut)
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
// Spécialisation pour String
template<>
struct gatt_codec<String> {
    static void set(NimBLECharacteristic* ch, const String& v) {
        if (!ch) return;
        const uint8_t* p = reinterpret_cast<const uint8_t*>(v.c_str());
        ch->setValue(p, v.length());
    }
    static String get(NimBLECharacteristic* ch) {
        if (!ch) return String();
        std::string s = ch->getValue();
        return String(s.c_str());
    }
};
// Spécialisation pour bool
template<>
struct gatt_codec<bool> {
    static void set(NimBLECharacteristic* ch, const bool& v) {
        if (!ch) return; 
        uint8_t b = v ? 1 : 0; 
        ch->setValue(&b, 1);
    }
    static bool get(NimBLECharacteristic* ch) {
        if (!ch) return false; 
        std::string s = ch->getValue(); 
        return !s.empty() && s[0] != 0;
    }
};
// Valeur de slot générique
template<typename T>
struct gatt_slot_value {
    gatt_slot_value(const T& v = T{}) : value_(v) {}
    gatt_slot_value(const T& v, const T& mn, const T& mx)
        : value_(v)
        , min_((mn <= mx) ? mn : mx)
        , max_((mn <= mx) ? mx : mn)
    { clamp(); }

    void set(const T& v) { value_ = v; clamp(); }
    const T& get() const { return value_; }
private:
    T value_{};
    std::optional<T> min_{};
    std::optional<T> max_{};

    bool has_bounds() const { return min_.has_value() && max_.has_value(); }
    void clamp() {
        if constexpr (std::is_arithmetic_v<T>) {
            if (has_bounds()) {
                if (value_ < *min_) value_ = *min_;
                else if (value_ > *max_) value_ = *max_;
            }
        }
    }
};
// Slot générique
template<typename T>
struct gatt_slot {
    gatt_slot() = delete;
    gatt_slot(const NimBLEUUID& u,
              const gatt_slot_value<T>& initial,
              NimBLECharacteristicCallbacks* callbacks = nullptr)
        : uuid_(u), value_(initial), cb_(callbacks) {}


    ///////////////////////////////////////////////
    NimBLECharacteristic* 
                create(NimBLEService* service, uint32_t props, bool notify_initial = false) {
        std::lock_guard<std::mutex> lk(mtx_);
        ch_ = service->createCharacteristic(uuid_, props);
        if (cb_) ch_->setCallbacks(cb_);
        gatt_codec<T>::set(ch_, value_.get());
        if (notify_initial) ch_->notify();
        return ch_;
    }
    void        set_callback(NimBLECharacteristicCallbacks* callbacks) {
        std::lock_guard<std::mutex> lk(mtx_);
        cb_ = callbacks;
        if (ch_ && cb_) ch_->setCallbacks(cb_);
    }


    ///////////////////////////////////////////////
    void        set(const T& v) {
        std::lock_guard<std::mutex> lk(mtx_);
        value_.set(v);
    }
    T           get() const {
        std::lock_guard<std::mutex> lk(mtx_);
        return value_.get();
    }

    ///////////////////////////////////////////////
    void        publish(bool notify=false) {
        std::lock_guard<std::mutex> lk(mtx_);
        if (!ch_) return;
        gatt_codec<T>::set(ch_, value_.get());
        if (notify) ch_->notify();
    }
    void        pull() {
        std::lock_guard<std::mutex> lk(mtx_);
        if (!ch_) return;
        T v = gatt_codec<T>::get(ch_);
        value_.set(v); // re-clamp éventuel
    }

    ///////////////////////////////////////////////
    void        bind(NimBLECharacteristic* c) {
        std::lock_guard<std::mutex> lk(mtx_);
        ch_ = c;
        if (cb_ && ch_) ch_->setCallbacks(cb_);
    }
    bool        is_bound() const {
        std::lock_guard<std::mutex> lk(mtx_);
        return ch_ != nullptr;
    }
    void        clear(bool notify=false) { 
        std::lock_guard<std::mutex> lk(mtx_);
        value_.set(T{});
        if (ch_) {
            gatt_codec<T>::set(ch_, value_.get());
            if (notify) ch_->notify();
        }
    }

private:
    mutable std::mutex                mtx_;
    gatt_slot_value<T>                value_{};
    NimBLEUUID                        uuid_{};
    NimBLECharacteristic*             ch_          = nullptr;
    NimBLECharacteristicCallbacks*    cb_          = nullptr;
};



//----------------------------------------------------------------------------------
//- VARIABLES GLOBALES
//----------------------------------------------------------------------------------
// UUIDs du service et des caractéristiques
static const NimBLEUUID SERVICE_UUID            ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f0");
static const NimBLEUUID CHAR_DEVID_UUID         ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f9");

static const NimBLEUUID CHAR_SSID_UUID          ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f1");
static const NimBLEUUID CHAR_PASS_UUID          ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f2");
static const NimBLEUUID CHAR_APPLY_UUID         ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f3");

static const NimBLEUUID CHAR_STATUS_UUID        ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f4");
static const NimBLEUUID CHAR_BATTERY_UUID       ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f5");

static const NimBLEUUID CHAR_DIR_X_UUID         ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f6");
static const NimBLEUUID CHAR_DIR_Y_UUID         ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f7");
static const NimBLEUUID CHAR_DIR_SPEED_UUID     ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f8");
static const NimBLEUUID CHAR_DECAY_MODE_UUID    ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1fa");



//----------------------------------------------------------------------------------
//- CALLBACK
//----------------------------------------------------------------------------------
class cb_write_ssid : public NimBLECharacteristicCallbacks {
public:
    cb_write_ssid(gatt_slot<String>* slot, gatt_slot<String>* status)
    : slot_(slot), status_(status) {}
    void onWrite(NimBLECharacteristic* c) override {
        std::string v = c->getValue();
        if (!v.empty()) {
            slot_->set(String(v.c_str()));         // MAJ cache local
        }
    }
private:
    gatt_slot<String>* slot_;
    gatt_slot<String>* status_;
};
class cb_write_pass : public NimBLECharacteristicCallbacks {
public:
    cb_write_pass(gatt_slot<String>* slot, gatt_slot<String>* status)
    : slot_(slot), status_(status) {}
    void onWrite(NimBLECharacteristic* c) override {
        std::string v = c->getValue();
        if (!v.empty()) {
            slot_->set(String(v.c_str()));         // MAJ cache local
        }
    }
private:
    gatt_slot<String>* slot_;
    gatt_slot<String>* status_;
};
class cb_write_direction : public NimBLECharacteristicCallbacks{
public:
    cb_write_direction(gatt_slot<int8_t>* direction, gatt_slot<String>* status)
    : direction_(direction), status_(status) {}
    void onWrite(NimBLECharacteristic* c) override {
        std::string v = c->getValue();
        if (!v.empty()) {
            int8_t dir = static_cast<int8_t>(v[0]);  // premier octet
            direction_->set(dir);

            // LOG série (tu verras enfin quelque chose)
            Serial.printf("[BLE][DIR] %s = %d / %d\n", c->getUUID().toString().c_str(), (int)dir, direction_->get());
        }
    }
private:
    gatt_slot<int8_t>* direction_;
    gatt_slot<String>* status_;
};
class cb_apply_wifi_credentials : public NimBLECharacteristicCallbacks {
public:
    cb_apply_wifi_credentials(gatt_slot<bool>* apply, gatt_slot<String>* ssid, gatt_slot<String>* pass, gatt_slot<String>* status)
    : apply_(apply), ssid_(ssid), pass_(pass), status_(status) {}
    void onWrite(NimBLECharacteristic* c) override {
        if (!ssid_->get().isEmpty() && !pass_->get().isEmpty() && c->getValue()){
            apply_->set(true);
            status_->set("configured");
            status_->publish();
        }
        else {
            apply_->set(false);
            status_->set("idle");
            status_->publish();
        }
    }
private:
    gatt_slot<bool>*   apply_;
    gatt_slot<String>* ssid_;
    gatt_slot<String>* pass_;
    gatt_slot<String>* status_;
};
#endif // BLE_DEFS_H