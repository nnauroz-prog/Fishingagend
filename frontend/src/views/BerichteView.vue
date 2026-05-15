<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { simulationApi } from '@/api/simulation';
import { useSimulationStore } from '@/store/simulation';

const { t } = useI18n();
const store = useSimulationStore();
const aktuellerBericht = ref<string | null>(null);

onMounted(() => store.laden());

async function anzeigen(id: string) {
  const r = await simulationApi.bericht(id);
  aktuellerBericht.value = r.markdown;
}
</script>

<template>
  <section class="space-y-6">
    <h1 class="text-2xl font-bold">{{ t('berichte.titel') }}</h1>

    <p v-if="!store.simulationen.length" class="text-sm text-slate-500">{{ t('berichte.leer') }}</p>

    <ul class="space-y-2">
      <li
        v-for="sim in store.simulationen.filter((s) => s.status === 'abgeschlossen')"
        :key="sim.id"
        class="flex items-center justify-between rounded border border-slate-200 px-4 py-2 dark:border-slate-700"
      >
        <span>{{ sim.name }}</span>
        <button class="knopf-sekundaer text-xs" @click="anzeigen(sim.id)">
          {{ t('berichte.anzeigen') }}
        </button>
      </li>
    </ul>

    <pre
      v-if="aktuellerBericht"
      class="karte whitespace-pre-wrap font-mono text-xs"
    >{{ aktuellerBericht }}</pre>
  </section>
</template>
