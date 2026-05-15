<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { simulationApi } from '@/api/simulation';
import { useSimulationStore } from '@/store/simulation';
import { useToastStore } from '@/store/toasts';
import { rendereMarkdown } from '@/werkzeuge/markdown';

const { t } = useI18n();
const store = useSimulationStore();
const toasts = useToastStore();
const aktuellerBericht = ref<string | null>(null);
const aktuellerName = ref<string | null>(null);
const ladend = ref(false);

const html = computed(() => (aktuellerBericht.value ? rendereMarkdown(aktuellerBericht.value) : ''));
const fertige = computed(() =>
  store.simulationen.filter((s) => s.status === 'abgeschlossen'),
);

onMounted(() => store.laden());

async function anzeigen(id: string, name: string) {
  ladend.value = true;
  try {
    const r = await simulationApi.bericht(id);
    aktuellerBericht.value = r.markdown;
    aktuellerName.value = name;
  } catch {
    toasts.fehler('Bericht konnte nicht geladen werden.');
  } finally {
    ladend.value = false;
  }
}

function drucken() {
  window.print();
}
</script>

<template>
  <section class="space-y-6">
    <h1 class="text-2xl font-bold">{{ t('berichte.titel') }}</h1>

    <p v-if="!fertige.length" class="text-sm text-slate-500">{{ t('berichte.leer') }}</p>

    <div v-else class="grid gap-6 lg:grid-cols-[20rem,1fr]">
      <ul class="space-y-1">
        <li
          v-for="sim in fertige"
          :key="sim.id"
        >
          <button
            class="w-full rounded border border-slate-200 px-3 py-2 text-left text-sm hover:bg-markenblau-50 dark:border-slate-700 dark:hover:bg-slate-700"
            :class="{ 'bg-markenblau-50 dark:bg-slate-700': aktuellerName === sim.name }"
            @click="anzeigen(sim.id, sim.name)"
          >
            <div class="font-medium">{{ sim.name }}</div>
            <div class="text-xs text-slate-500">
              {{ sim.schritte }} Schritte · {{ sim.agent_ids.length }} Agenten
            </div>
          </button>
        </li>
      </ul>

      <article class="karte prose prose-slate min-h-[24rem] max-w-none dark:prose-invert">
        <div v-if="aktuellerBericht" class="nicht-drucken mb-3 flex justify-end">
          <button class="knopf-sekundaer text-xs" @click="drucken">
            {{ t('berichte.drucken') }}
          </button>
        </div>
        <p v-if="ladend" class="text-sm text-slate-500">…</p>
        <p v-else-if="!aktuellerBericht" class="text-sm text-slate-500">
          {{ t('berichte.anzeigen') }} →
        </p>
        <div v-else v-html="html" />
      </article>
    </div>
  </section>
</template>
