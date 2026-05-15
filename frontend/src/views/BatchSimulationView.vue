<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import { simulationApi } from '@/api/simulation';
import type { Simulation } from '@/api/typen';
import { useAgentenStore } from '@/store/agenten';
import { useToastStore } from '@/store/toasts';

const { t } = useI18n();
const router = useRouter();
const agenten = useAgentenStore();
const toasts = useToastStore();

const vorlage = reactive({
  name: 'Sensitivitäts-Lauf',
  schritte: 5,
  ausgewaehlt: [] as string[],
  dual_modus: true,
  plattform_modus: false,
});

const serieText = ref('[{"x": 1}, {"x": 2}, {"x": 3}]');
const fehler = ref<string | null>(null);
const angelegt = ref<Simulation[]>([]);
const arbeitet = ref(false);

onMounted(() => agenten.laden());

async function ausfuehren() {
  fehler.value = null;
  let serie: Record<string, unknown>[];
  try {
    serie = JSON.parse(serieText.value);
    if (!Array.isArray(serie) || !serie.length) throw new Error('leer');
  } catch {
    fehler.value = 'Variablen-Serie ist kein gültiges JSON-Array.';
    return;
  }
  if (!vorlage.ausgewaehlt.length) {
    fehler.value = 'Mindestens einen Agenten auswählen.';
    return;
  }

  arbeitet.value = true;
  try {
    angelegt.value = await simulationApi.batch(
      {
        name: vorlage.name,
        agent_ids: vorlage.ausgewaehlt,
        schritte: vorlage.schritte,
        variable: {},
        dual_modus: vorlage.dual_modus,
        plattform_modus: vorlage.plattform_modus,
      },
      serie,
      true,
    );
    toasts.erfolg(`${angelegt.value.length} Simulationen gestartet.`);
  } finally {
    arbeitet.value = false;
  }
}
</script>

<template>
  <section class="space-y-6">
    <header>
      <h1 class="text-2xl font-bold">{{ t('batch.titel') }}</h1>
      <p class="text-sm text-slate-500">{{ t('batch.einleitung') }}</p>
    </header>

    <form class="karte grid gap-3 md:grid-cols-2" @submit.prevent="ausfuehren">
      <div class="md:col-span-2">
        <label class="etikett">Name (Präfix)</label>
        <input v-model="vorlage.name" class="eingabe" />
      </div>
      <div>
        <label class="etikett">{{ t('simulation.schritte') }}</label>
        <input v-model.number="vorlage.schritte" type="number" min="1" max="50" class="eingabe" />
      </div>
      <div class="space-y-1">
        <label class="etikett">
          <input v-model="vorlage.dual_modus" type="checkbox" class="mr-2" />
          {{ t('simulation.dual_modus') }}
        </label>
        <label class="etikett">
          <input v-model="vorlage.plattform_modus" type="checkbox" class="mr-2" />
          {{ t('simulation.plattform_modus') }}
        </label>
      </div>
      <div class="md:col-span-2">
        <label class="etikett">{{ t('simulation.agenten') }}</label>
        <select v-model="vorlage.ausgewaehlt" multiple class="eingabe h-32">
          <option v-for="a in agenten.agenten" :key="a.id" :value="a.id">
            {{ a.persona.name }}
          </option>
        </select>
      </div>
      <div class="md:col-span-2">
        <label class="etikett">{{ t('batch.serie') }}</label>
        <textarea v-model="serieText" rows="5" class="eingabe font-mono text-xs" />
        <p class="mt-1 text-xs text-slate-500">{{ t('batch.serie_hinweis') }}</p>
      </div>
      <p v-if="fehler" class="text-sm text-red-600 md:col-span-2">{{ fehler }}</p>
      <div class="md:col-span-2 flex justify-end">
        <button type="submit" class="knopf-primaer" :disabled="arbeitet">
          {{ arbeitet ? '…' : t('batch.start') }}
        </button>
      </div>
    </form>

    <div v-if="angelegt.length" class="space-y-2">
      <h2 class="text-sm font-semibold uppercase text-slate-500">
        {{ t('batch.angelegte') }} ({{ angelegt.length }})
      </h2>
      <ul class="space-y-1">
        <li
          v-for="sim in angelegt"
          :key="sim.id"
          class="flex items-center justify-between rounded border border-slate-200 px-4 py-2 dark:border-slate-700"
        >
          <div>
            <p class="font-medium">{{ sim.name }}</p>
            <p class="text-xs text-slate-500 font-mono">
              {{ JSON.stringify(sim.variable) }}
            </p>
          </div>
          <button
            class="knopf-sekundaer text-xs"
            @click="router.push({ name: 'simulation-detail', params: { id: sim.id } })"
          >
            → öffnen
          </button>
        </li>
      </ul>
      <RouterLink to="/simulation/vergleich" class="knopf-sekundaer text-xs">
        ⇆ {{ t('vergleich.titel') }}
      </RouterLink>
    </div>
  </section>
</template>
