#include <Arduino.h>
#include <NimBLEDevice.h>

#ifndef DEVICE_NAME
#define DEVICE_NAME "XIAO-S3-Provisioner"
#endif

// ==== UUIDs (garde-les ou remplace-les par les tiens) ====
static NimBLEUUID SERVICE_UUID   ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f0");
static NimBLEUUID CHAR_SSID_UUID ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f1");
static NimBLEUUID CHAR_PASS_UUID ("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f2");
static NimBLEUUID CHAR_DEVID_UUID("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f9");
static NimBLEUUID CHAR_STATUS_UUID("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f4");
static NimBLEUUID CHAR_APPLY_UUID("7f1f9b2a-6a43-4f62-8c2a-b9d3c0e4a1f3");


// ==== Variables reçues ====
static String g_ssid;
static String g_pass;

// Petit callback générique pour capter les écritures
class WriteToStringCB : public NimBLECharacteristicCallbacks {
public:
  WriteToStringCB(String* target, const char* label) : target_(target), label_(label) {}
  void onWrite(NimBLECharacteristic* c) override {
    std::string v = c->getValue();
    *target_ = String(v.c_str());
    Serial.printf("[BLE] %s reçu (%u octets)", label_, (unsigned)v.size());
  }
private:
  String* target_;
  const char* label_;
};
class ApplyCB : public NimBLECharacteristicCallbacks {
  void onWrite(NimBLECharacteristic* c) override {
    // ici: valider que g_ssid/g_pass non vides, sauver en NVS plus tard si tu veux
    NimBLECharacteristic* st = c->getService()->getCharacteristic(CHAR_STATUS_UUID);
    if (g_ssid.length() && g_pass.length()) { st->setValue("ok"); st->notify(); }
    else { st->setValue("missing"); st->notify(); }
  }
};

void setup() {
  Serial.begin(115200);
  delay(6000);
  Serial.println("Init BLE (réception SSID/MOTDEPASSE)…");

  NimBLEDevice::init(DEVICE_NAME); // init d'abord
  String name = String("XIAO-") + NimBLEDevice::getAddress().toString().c_str(); // puis adresse
  NimBLEDevice::setDeviceName(name.c_str());   // met vraiment le nom d’advertising
  NimBLEDevice::setPower(ESP_PWR_LVL_P9, ESP_BLE_PWR_TYPE_DEFAULT);

  NimBLEServer* server = NimBLEDevice::createServer();
  NimBLEService* service = server->createService(SERVICE_UUID);

  //----CARACTERISTIQUES----
  // ID
  NimBLECharacteristic* chDevId = service->createCharacteristic(
    CHAR_DEVID_UUID, NIMBLE_PROPERTY::READ);
  chDevId->setValue(name.c_str());
  // STATUS
  NimBLECharacteristic* chStatus = service->createCharacteristic(
    CHAR_STATUS_UUID, NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::NOTIFY
  );
  chStatus->setValue("idle");
  // Caractéristique SSID (écriture)
  NimBLECharacteristic* chSsid = service->createCharacteristic(
    CHAR_SSID_UUID, NIMBLE_PROPERTY::WRITE
  );
  chSsid->setCallbacks(new WriteToStringCB(&g_ssid, "SSID"));
  // Caractéristique mot de passe (écriture)
  NimBLECharacteristic* chPass = service->createCharacteristic(
    CHAR_PASS_UUID, NIMBLE_PROPERTY::WRITE
  );
  chPass->setCallbacks(new WriteToStringCB(&g_pass, "PASS"));
  // Appliquer paramettre
  NimBLECharacteristic* chApply = service->createCharacteristic(
    CHAR_APPLY_UUID, NIMBLE_PROPERTY::WRITE);
  chApply->setCallbacks(new ApplyCB());
  //-------------------------


  service->start();

  NimBLEAdvertising* adv = NimBLEDevice::getAdvertising();
  adv->addServiceUUID(SERVICE_UUID);
  adv->setScanResponse(true);
  adv->start();

  Serial.printf("Advertising BLE '%s' — en attente du SSID et mot de passe…", DEVICE_NAME);
}

void loop() {
  // Rien d’autre : on ne fait que recevoir et stocker SSID / PASS
  delay(100);
}