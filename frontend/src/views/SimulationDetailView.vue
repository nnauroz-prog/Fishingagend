<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';

import { simulationApi } from '@/api/simulation';
import type { Simulation, SimulationSchritt } from '@/api/typen';
import { abonniereSimulation } from '@/api/websocket';
import VergleichsAnsicht from '@/components/VergleichsAnsicht.vue';
import { useToastStore } from '@/store/toasts';

const route = useRoute();
const { t } = useI18n();
const toasts = useToastStore();

const sim = ref<Simulation | null>(null);
const ladend = ref(true);
const ansicht = ref<'spalten' | 'vergleich'>('spalten');
let abbrechen: (() => void) | null = null;

const id = computed(() => route.params.id as string);

const kontroll = computed(() =>
  sim.value ? sim.value.verlauf.filter((s) => s.welt === 'kontrolle') : [],
);
const variante = computed(() =>
  sim.value ? sim.value.verlauf.filter((s) => s.welt === 'variante') : [],
);

const fortschritt = computed(() => {
  if (!sim.value) return 0;
  const erwartet = sim.value.schritte * (sim.value.dual_modus ? 2 : 1);
  if (!erwartet) return 0;
  return Math.min(100, Math.round((sim.value.verlauf.length / erwartet) * 100));
});

async function laden() {
  try {
    sim.value = await simulationApi.hole(id.value);
  } catch {
    toasts.fehler('Simulation nicht gefunden.');
  } finally {
    ladend.value = false;
  }
}

async function starte() {
  if (!sim.value) return;
  await simulationApi.starte(sim.value.id, false);
  toasts.info('Simulation gestartet — läuft im Hintergrund.');
  await laden();
}

function exportJson() {
  if (!sim.value) return;
  const blob = new Blob([JSON.stringify(sim.value, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `simulation-${sim.value.name.replace(/\s+/g, '-')}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function verbinde() {
  abbrechen?.();
  abbrechen = abonniereSimulation(id.value, (e) => {
    if (!sim.value) return;
    if (e.typ === 'schritt') {
      const neuer: SimulationSchritt = {
        nummer: e.nummer,
        welt: e.welt,
        ereignisse: e.ereignisse,
        agent_zustaende: {},
      };
      sim.value.verlauf.push(neuer);
    } else if (e.typ === 'status') {
      sim.value.status = e.status;
      if (e.status === 'abgeschlossen') {
        toasts.erfolg('Simulation abgeschlossen.');
      }
    }
  });
}

onMounted(async () => {
  await laden();
  verbinde();
});

onUnmounted(() => {
  abbrechen?.();
});
</script>

<template>
  <section v-if="ladend" class="text-sm text-slate-500">…</section>

  <section v-else-if="sim" class="space-y-6">
    <header>
      <RouterLink to="/simulation" class="text-xs text-markenblau-600 hover:underline">
        ← {{ t('navigation.simulation') }}
      </RouterLink>
      <h1 class="text-3xl font-bold">{{ sim.name }}</h1>
      <p v-if="sim.beschreibung" class="text-slate-500">{{ sim.beschreibung }}</p>
    </header>

    <div class="karte flex items-center gap-4">
      <span
        class="rounded-full px-3 py-1 text-sm font-medium"
        :class="{
          'bg-slate-200 text-slate-700': sim.status === 'geplant',
          'bg-yellow-100 text-yellow-700': sim.status === 'laeuft',
          'bg-green-100 text-green-700': sim.status === 'abgeschlossen',
          'bg-red-100 text-red-700': sim.status === 'fehlgeschlagen',
        }"
      >
        {{ t(`simulation.status_${sim.status}`) }}
      </span>
      <div class="flex-1">
        <div class="h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
          <div
            class="h-full bg-markenblau-600 transition-all"
            :style="{ width: `${fortschritt}%` }"
          />
        </div>
        <p class="mt-1 text-xs text-slate-500">
          {{ sim.verlauf.length }} / {{ sim.schritte * (sim.dual_modus ? 2 : 1) }} Schritte
        </p>
      </div>
      <button
        v-if="sim.status === 'geplant'"
        class="knopf-primaer"
        @click="starte"
      >
        ▶ {{ t('simulation.starten') }}
      </button>
    </div>

    <div v-if="sim.dual_modus" class="flex gap-2">
      <button
        class="knopf-sekundaer text-xs"
        :class="{ 'bg-markenblau-600 text-white hover:bg-markenblau-700': ansicht === 'spalten' }"
        @click="ansicht = 'spalten'"
      >
        Spalten
      </button>
      <button
        class="knopf-sekundaer text-xs"
        :class="{ 'bg-markenblau-600 text-white hover:bg-markenblau-700': ansicht === 'vergleich' }"
        @click="ansicht = 'vergleich'"
      >
        {{ t('simulation.vergleich') }}
      </button>
    </div>

    <article v-if="sim.dual_modus && ansicht === 'vergleich'" class="karte overflow-x-auto">
      <p v-if="Object.keys(sim.variable).length" class="mb-3 text-xs text-slate-500">
        Variable: <code>{{ JSON.stringify(sim.variable) }}</code>
      </p>
      <VergleichsAnsicht :simulation="sim" />
    </article>

    <div v-else class="grid gap-4" :class="sim.dual_modus ? 'lg:grid-cols-2' : ''">
      <article class="karte">
        <h2 class="mb-3 text-sm font-semibold uppercase text-slate-500">Kontroll-Welt</h2>
        <ul class="space-y-2 text-sm">
          <li
            v-for="s in kontroll"
            :key="`k-${s.nummer}`"
            class="rounded border-l-2 border-slate-300 pl-3 dark:border-slate-600"
          >
            <span class="text-xs text-slate-500">Schritt {{ s.nummer }}</span>
            <ul class="mt-1 space-y-0.5">
              <li v-for="(e, i) in s.ereignisse" :key="i">{{ e }}</li>
            </ul>
          </li>
          <li v-if="!kontroll.length" class="text-slate-500">Noch keine Schritte.</li>
        </ul>
      </article>

      <article v-if="sim.dual_modus" class="karte">
        <h2 class="mb-3 text-sm font-semibold uppercase text-markenblau-700 dark:text-markenblau-500">
          Varianten-Welt
        </h2>
        <p v-if="Object.keys(sim.variable).length" class="mb-3 text-xs text-slate-500">
          Variable: <code>{{ JSON.stringify(sim.variable) }}</code>
        </p>
        <ul class="space-y-2 text-sm">
          <li
            v-for="s in variante"
            :key="`v-${s.nummer}`"
            class="rounded border-l-2 border-markenblau-400 pl-3"
          >
            <span class="text-xs text-slate-500">Schritt {{ s.nummer }}</span>
            <ul class="mt-1 space-y-0.5">
              <li v-for="(e, i) in s.ereignisse" :key="i">{{ e }}</li>
            </ul>
          </li>
          <li v-if="!variante.length" class="text-slate-500">Noch keine Schritte.</li>
        </ul>
      </article>
    </div>

    <div class="flex gap-2">
      <RouterLink
        v-if="sim.status === 'abgeschlossen'"
        to="/berichte"
        class="knopf-sekundaer"
      >
        → {{ t('berichte.titel') }}
      </RouterLink>
      <button class="knopf-sekundaer text-xs" @click="exportJson">
        ⬇ JSON
      </button>
    </div>
  </section>
</template>
