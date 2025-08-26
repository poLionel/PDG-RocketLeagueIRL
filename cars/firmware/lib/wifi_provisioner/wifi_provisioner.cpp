//----------------------------------------------------------------------------------
//- INCLUDES
#include "wifi_provisioner.h"



//----------------------------------------------------------------------------------
//- MÉTHODES MEMBRES
void wifi_provisioner::init(String device_id){
    WiFi.mode(WIFI_STA);
    WiFi.persistent(false); // évite d’écrire en flash par défaut
    WiFi.setHostname(device_id_.c_str()); // à faire avant WiFi.begin()
}
bool wifi_provisioner::connect(const String& ssid, const String& pass, uint32_t timeout_ms){
    if (ssid.isEmpty()) return false;   
    // Coupe toute conn. précédente et applique hostname s'il a été défini
    WiFi.disconnect(true, true);
    delay(50);
    if (device_id_.length() > 0) WiFi.setHostname(device_id_.c_str());
    WiFi.begin(ssid.c_str(), pass.c_str()); 
    uint32_t t0 = millis();
    while (WiFi.status() != WL_CONNECTED && (millis() - t0) < timeout_ms) {
      delay(200);
    }
    return WiFi.status() == WL_CONNECTED;
}
void wifi_provisioner::disconnect(bool erase_cfg){
    WiFi.disconnect(erase_cfg, true);
}
bool wifi_provisioner::is_connected() const{
    return WiFi.status() == WL_CONNECTED;
}
String wifi_provisioner::ip() const{
    return is_connected() ? WiFi.localIP().toString() : String("");
}
int32_t wifi_provisioner::rssi() const{
    return is_connected() ? WiFi.RSSI() : 0;
}