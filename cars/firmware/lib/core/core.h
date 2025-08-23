#ifndef CORE_H
#define CORE_H



//----------------------------------------------------------------------------------
//- INCLUDES
//----------------------------------------------------------------------------------
#include <Arduino.h>
#include "ble_provisioner.h"
#include "wifi_provisioner.h"



//----------------------------------------------------------------------------------
// BIT DE FLAG (SYNC)
//----------------------------------------------------------------------------------
void core_init(ble_provisioner* ble, wifi_provisioner* wifi);
void core_start();



#endif //CORE_H