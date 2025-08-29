//----------------------------------------------------------------------------------
//- INCLUDES
//----------------------------------------------------------------------------------
#include "core_task.h"



//----------------------------------------------------------------------------------
//- CONSTRUCTEURS / DESCTRUCTEURS
//----------------------------------------------------------------------------------
core_task::core_task(core_task_config cfg) : 
    cfg_(cfg) {}



//----------------------------------------------------------------------------------
//- MÉTHODES MEMBRES
//----------------------------------------------------------------------------------
void core_task::start() {
    if (cfg_.settings.core_id >= 0 && cfg_.settings.core_id <= 1) {
        xTaskCreatePinnedToCore(
        &core_task::trampoline,
        cfg_.settings.name,
        cfg_.settings.stack_words,
        this,
        cfg_.settings.prio,
        /*handle*/ nullptr,
        cfg_.settings.core_id
        );
    }
}
void core_task::trampoline(void* pv) {
    auto* self  = static_cast<core_task*>(pv);
    const char* tname = pcTaskGetName(NULL);

    for (;;) {
    // --- Gate & START ---
    xEventGroupWaitBits(
        self->cfg_.settings.evt,
        self->cfg_.settings.gate_bit,
        pdFALSE,  // ne pas clear le bit à l’entrée
        pdTRUE,   // attendre que TOUS les bits passés soient levés (ici un seul)
        portMAX_DELAY
    );
    printf("[%s] START\n", tname);

    // --- Setup ---
    if (self->cfg_.component.on_setup) {
        self->cfg_.component.on_setup(self->cfg_.component.ctx);
    }

    // --- Boucle tant que le gate est actif ---
    while (xEventGroupGetBits(self->cfg_.settings.evt) & self->cfg_.settings.gate_bit) {
        if (self->cfg_.component.on_loop) {
        self->cfg_.component.on_loop(self->cfg_.component.ctx);
        }
        if (self->cfg_.settings.period_ms > 0) {
        vTaskDelay(pdMS_TO_TICKS(self->cfg_.settings.period_ms));
        }
        // sinon: on laisse la loop être “self-paced” (bloquante ou yield interne)
    }

    // --- Teardown & STOP ---
    if (self->cfg_.component.on_teardown) {
        self->cfg_.component.on_teardown(self->cfg_.component.ctx);
    }
    printf("[%s] STOP\n", tname);
    // puis retour à l’attente du gate
    }
}