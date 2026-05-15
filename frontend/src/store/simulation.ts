import { defineStore } from 'pinia';
import { ref } from 'vue';

import { simulationApi } from '@/api/simulation';
import type { Simulation, SimulationErstellen } from '@/api/typen';

export const useSimulationStore = defineStore('simulation', () => {
  const simulationen = ref<Simulation[]>([]);
  const aktiv = ref<Simulation | null>(null);
  const ladend = ref(false);

  async function laden() {
    ladend.value = true;
    try {
      simulationen.value = await simulationApi.liste();
    } finally {
      ladend.value = false;
    }
  }

  async function planen(eingabe: SimulationErstellen) {
    const neu = await simulationApi.plane(eingabe);
    simulationen.value.push(neu);
    aktiv.value = neu;
    return neu;
  }

  async function starten(id: string, sofort = false) {
    const sim = await simulationApi.starte(id, sofort);
    const idx = simulationen.value.findIndex((s) => s.id === id);
    if (idx >= 0) simulationen.value[idx] = sim;
    aktiv.value = sim;
    return sim;
  }

  async function aktualisiere(id: string) {
    const sim = await simulationApi.hole(id);
    const idx = simulationen.value.findIndex((s) => s.id === id);
    if (idx >= 0) simulationen.value[idx] = sim;
    return sim;
  }

  return { simulationen, aktiv, ladend, laden, planen, starten, aktualisiere };
});
