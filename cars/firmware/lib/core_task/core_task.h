#ifndef CORE_TASK_H
#define CORE_TASK_H



//----------------------------------------------------------------------------------
//- INCLUDES
//----------------------------------------------------------------------------------
#include <stdint.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"



//----------------------------------------------------------------------------------
//- ALIAS
//----------------------------------------------------------------------------------
using core_setup_fn         = void (*)(void*);
using core_loop_fn          = void (*)(void*);
using core_teardown_fn      = void (*)(void*);



//----------------------------------------------------------------------------------
//- STRUCTURES
//----------------------------------------------------------------------------------
struct task_component {
  core_setup_fn             on_setup;     // peut être nullptr
  core_loop_fn              on_loop;      // doit exécuter une itération
  core_teardown_fn          on_teardown;  // peut être nullptr
  void*                     ctx;          // contexte optionnel
};
struct task_settings {
  const char*               name;         // nom FreeRTOS (affiché dans les logs)
  UBaseType_t               prio;         // priorité FreeRTOS
  uint32_t                  stack_words;  // taille pile (en mots)
  int                       core_id;      // -1 = non épinglée, sinon 0/1 (ESP32)
  EventGroupHandle_t        evt;          // groupe d'événements (gate)
  EventBits_t               gate_bit;     // bit à surveiller (start/stop)
  uint32_t                  period_ms;    // période d'itération (0 = pas de sleep auto)
};
struct core_task_config {
    task_settings           settings;
    task_component          component;
};



//----------------------------------------------------------------------------------
//- Class
//----------------------------------------------------------------------------------
class core_task {
public:
    core_task(core_task_config cfg);

    void                        start();
private:
  core_task_config              cfg_;

  static void                   trampoline(void* pv);
};



#endif //CORE_TASK_H