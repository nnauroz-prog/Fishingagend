import { defineStore } from 'pinia';
import { ref } from 'vue';

import { agentenApi } from '@/api/agenten';
import type { Agent, AgentErstellen } from '@/api/typen';

export const useAgentenStore = defineStore('agenten', () => {
  const agenten = ref<Agent[]>([]);
  const ladend = ref(false);
  const fehler = ref<string | null>(null);

  async function laden() {
    ladend.value = true;
    fehler.value = null;
    try {
      agenten.value = await agentenApi.liste();
    } catch (e) {
      fehler.value = (e as Error).message;
    } finally {
      ladend.value = false;
    }
  }

  async function erstellen(eingabe: AgentErstellen) {
    const neu = await agentenApi.erstelle(eingabe);
    agenten.value.push(neu);
    return neu;
  }

  async function loeschen(id: string) {
    await agentenApi.loesche(id);
    agenten.value = agenten.value.filter((a) => a.id !== id);
  }

  return { agenten, ladend, fehler, laden, erstellen, loeschen };
});
