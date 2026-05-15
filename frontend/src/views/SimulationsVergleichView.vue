<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

import { simulationApi } from '@/api/simulation';
import type { Simulation } from '@/api/typen';
import { useSimulationStore } from '@/store/simulation';
import { rendereMarkdown } from '@/werkzeuge/markdown';

const { t } = useI18n();
const store = useSimulationStore();

const linkeId = ref('');
const rechteId = ref('');

const linkeSim = ref<Simulation | null>(null);
const rechteSim = ref<Simulation | null>(null);
const linkerBericht = ref<string | null>(null);
const rechterBericht = ref<string | null>(null);

const fertige = computed(() =>
  store.simulationen.filter((s) => s.status === 'abgeschlossen'),
);

onMounted(async () => {
  await store.laden();
  if (fertige.value.length >= 2) {
    linkeId.value = fertige.value[0].id;
    rechteId.value = fertige.value[1].id;
  }
});

async function ladeLinks() {
  if (!linkeId.value) return;
  linkeSim.value = await simulationApi.hole(linkeId.value);
  linkerBericht.value = (await simulationApi.bericht(linkeId.value)).markdown;
}

async function ladeRechts() {
  if (!rechteId.value) return;
  rechteSim.value = await simulationApi.hole(rechteId.value);
  rechterBericht.value = (await simulationApi.bericht(rechteId.value)).markdown;
}

watch(linkeId, ladeLinks);
watch(rechteId, ladeRechts);

function statistik(s: Simulation | null): Record<string, number | string> {
  if (!s) return {};
  const akteure: Record<string, number> = {};
  for (const sch of s.verlauf) {
    for (const e of sch.ereignisse) {
      if (e.includes(':')) {
        const name = e.split(':', 1)[0].trim();
        akteure[name] = (akteure[name] ?? 0) + 1;
      }
    }
  }
  const top = Object.entries(akteure)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([n, k]) => `${n} (${k})`)
    .join(', ');
  return {
    Status: s.status,
    Schritte: s.schritte,
    Agenten: s.agent_ids.length,
    'Verlaufs-Einträge': s.verlauf.length,
    'Dual-Modus': s.dual_modus ? 'ja' : 'nein',
    'Plattform-Modus': s.plattform_modus ? 'ja' : 'nein',
    'Top-Akteure': top || '—',
    Variable: JSON.stringify(s.variable) || '—',
  };
}
</script>

<template>
  <section class="space-y-6">
    <header>
      <h1 class="text-2xl font-bold">{{ t('vergleich.titel') }}</h1>
      <p class="text-sm text-slate-500">{{ t('vergleich.einleitung') }}</p>
    </header>

    <p v-if="fertige.length < 2" class="text-sm text-slate-500">
      {{ t('vergleich.zu_wenig') }}
    </p>

    <div v-else class="grid gap-4 md:grid-cols-2">
      <article class="karte">
        <select v-model="linkeId" class="eingabe">
          <option value="" disabled>{{ t('vergleich.waehle') }}</option>
          <option v-for="s in fertige" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
        <dl v-if="linkeSim" class="mt-4 grid grid-cols-[max-content,1fr] gap-x-3 gap-y-1 text-sm">
          <template v-for="(v, k) in statistik(linkeSim)" :key="k">
            <dt class="text-slate-500">{{ k }}</dt>
            <dd class="font-mono text-xs">{{ v }}</dd>
          </template>
        </dl>
      </article>

      <article class="karte">
        <select v-model="rechteId" class="eingabe">
          <option value="" disabled>{{ t('vergleich.waehle') }}</option>
          <option v-for="s in fertige" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
        <dl v-if="rechteSim" class="mt-4 grid grid-cols-[max-content,1fr] gap-x-3 gap-y-1 text-sm">
          <template v-for="(v, k) in statistik(rechteSim)" :key="k">
            <dt class="text-slate-500">{{ k }}</dt>
            <dd class="font-mono text-xs">{{ v }}</dd>
          </template>
        </dl>
      </article>

      <article v-if="linkerBericht" class="karte prose prose-sm max-w-none dark:prose-invert">
        <h3 class="!mt-0 text-xs uppercase text-slate-500">{{ t('vergleich.bericht') }}</h3>
        <div v-html="rendereMarkdown(linkerBericht)" />
      </article>

      <article v-if="rechterBericht" class="karte prose prose-sm max-w-none dark:prose-invert">
        <h3 class="!mt-0 text-xs uppercase text-slate-500">{{ t('vergleich.bericht') }}</h3>
        <div v-html="rendereMarkdown(rechterBericht)" />
      </article>
    </div>
  </section>
</template>
