#ifndef WIFI_PROVISIONER_H
#define WIFI_PROVISIONER_H



//----------------------------------------------------------------------------------
//- INCLUDES
#include <wifi_defs.h>



//----------------------------------------------------------------------------------
//- Classe
class wifi_provisioner {
public:
  void                  init(String device_id);
  bool                  connect(const String& ssid, const String& pass, uint32_t timeout_ms = 15000);
  void                  disconnect(bool erase_cfg = true);   // coupe le Wi-Fi (option: effacer cfg)
  
  String                get_device_id() const { return device_id_; }
  
  bool                  is_connected() const;
  String                ip() const;                        // IP locale (ou "")
  String                mac() const;                        // Adresse MAC (toujours dispo)
  String                netmask() const;                    // Masque (si connecté)
  String                gateway() const;                    // Passerelle (si connecté)
  int32_t               rssi() const;                     // RSSI si connecté (ou 0)


private:
  String device_id_;
};
#endif // WIFI_PROVISIONER_H
