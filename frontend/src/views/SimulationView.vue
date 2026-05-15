<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import SimulationsAnzeige from '@/components/SimulationsAnzeige.vue';
import { useAgentenStore } from '@/store/agenten';
import { useSimulationStore } from '@/store/simulation';

const { t } = useI18n();
const sims = useSimulationStore();
const agenten = useAgentenStore();

const formular = reactive({
  name: '',
  beschreibung: '',
  schritte: 10,
  variableJson: '{}',
  dual_modus: true,
  ausgewaehlt: [] as string[],
});

const fehler = ref<string | null>(null);

onMounted(async () => {
  await Promise.all([sims.laden(), agenten.laden()]);
});

async function planen() {
  fehler.value = null;
  let variable: Record<string, unknown> = {};
  try {
    variable = formular.variableJson.trim() ? JSON.parse(formular.variableJson) : {};
  } catch {
    fehler.value = 'Variable ist kein gültiges JSON.';
    return;
  }
  if (!formular.ausgewaehlt.length) {
    fehler.value = 'Mindestens einen Agenten auswählen.';
    return;
  }
  await sims.planen({
    name: formular.name || 'Unbenannte Simulation',
    beschreibung: formular.beschreibung,
    agent_ids: formular.ausgewaehlt,
    schritte: formular.schritte,
    variable,
    dual_modus: formular.dual_modus,
  });
}
</script>

<template>
  <section class="space-y-6">
    <h1 class="text-2xl font-bold">{{ t('simulation.titel') }}</h1>

    <form class="karte grid gap-3 md:grid-cols-2" @submit.prevent="planen">
      <div class="md:col-span-2">
        <label class="etikett">Name</label>
        <input v-model="formular.name" class="eingabe" />
      </div>
      <div>
        <label class="etikett">{{ t('simulation.schritte') }}</label>
        <input v-model.number="formular.schritte" type="number" min="1" max="500" class="eingabe" />
      </div>
      <div>
        <label class="etikett">
          <input v-model="formular.dual_modus" type="checkbox" class="mr-2" />
          {{ t('simulation.dual_modus') }}
        </label>
      </div>
      <div class="md:col-span-2">
        <label class="etikett">{{ t('simulation.agenten') }}</label>
        <select v-model="formular.ausgewaehlt" multiple class="eingabe h-32">
          <option v-for="a in agenten.agenten" :key="a.id" :value="a.id">
            {{ a.persona.name }}
          </option>
        </select>
      </div>
      <div class="md:col-span-2">
        <label class="etikett">{{ t('simulation.variable') }}</label>
        <textarea v-model="formular.variableJson" rows="3" class="eingabe font-mono text-xs" />
      </div>
      <p v-if="fehler" class="text-sm text-red-600 md:col-span-2">{{ fehler }}</p>
      <div class="md:col-span-2 flex justify-end">
        <button type="submit" class="knopf-primaer">{{ t('simulation.neue') }}</button>
      </div>
    </form>

    <div class="grid gap-4 md:grid-cols-2">
      <div v-for="sim in sims.simulationen" :key="sim.id" class="space-y-2">
        <SimulationsAnzeige :simulation="sim" />
        <button
          v-if="sim.status === 'geplant'"
          class="knopf-sekundaer text-xs"
          @click="sims.starten(sim.id)"
        >
          ▶ {{ t('simulation.starten') }}
        </button>
      </div>
    </div>
  </section>
</template>
