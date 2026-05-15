<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';

import { simulationApi } from '@/api/simulation';
import type { FeedBeitrag, Folge, Simulation, SimulationSchritt } from '@/api/typen';
import { abonniereSimulation } from '@/api/websocket';
import FeedAnzeige from '@/components/FeedAnzeige.vue';
import StimmungsDiagramm from '@/components/StimmungsDiagramm.vue';
import VergleichsAnsicht from '@/components/VergleichsAnsicht.vue';
import { useToastStore } from '@/store/toasts';

const route = useRoute();
const { t } = useI18n();
const toasts = useToastStore();

const sim = ref<Simulation | null>(null);
const ladend = ref(true);
const ansicht = ref<'spalten' | 'vergleich' | 'feed' | 'replay'>('spalten');
const feed = ref<FeedBeitrag[]>([]);
const folgen = ref<Folge[]>([]);
const stimmung = ref<Record<string, { schritt: number; score: number }[]>>({});
const replaySchritt = ref(1);
const replaySpielt = ref(false);
let replayTimer: ReturnType<typeof setInterval> | null = null;
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
    if (sim.value?.plattform_modus) {
      [feed.value, folgen.value] = await Promise.all([
        simulationApi.feed(id.value),
        simulationApi.folgen(id.value),
      ]);
      ansicht.value = 'feed';
    }
    if (sim.value?.status === 'abgeschlossen') {
      stimmung.value = await simulationApi.stimmung(id.value);
    }
  } catch {
    toasts.fehler('Simulation nicht gefunden.');
  } finally {
    ladend.value = false;
  }
}

const replaySchritte = computed(() => sim.value?.schritte ?? 0);
const sichtbareSchritte = computed(() => {
  if (!sim.value) return [];
  if (ansicht.value !== 'replay') return sim.value.verlauf;
  return sim.value.verlauf.filter((s) => s.nummer <= replaySchritt.value);
});

const stimmungsReihen = computed(() => {
  const farben: Record<string, string> = {
    kontrolle: '#64748b',
    variante: '#2563eb',
  };
  return Object.entries(stimmung.value).map(([welt, daten]) => ({
    name: welt,
    farbe: farben[welt] ?? '#64748b',
    daten,
  }));
});

function replaySpielen() {
  if (replaySpielt.value) {
    replayPause();
    return;
  }
  replaySpielt.value = true;
  replayTimer = setInterval(() => {
    if (replaySchritt.value >= replaySchritte.value) {
      replayPause();
      return;
    }
    replaySchritt.value++;
  }, 800);
}

function replayPause() {
  replaySpielt.value = false;
  if (replayTimer) clearInterval(replayTimer);
  replayTimer = null;
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

    <div class="flex flex-wrap gap-2">
      <button
        v-if="sim.dual_modus"
        class="knopf-sekundaer text-xs"
        :class="{ 'bg-markenblau-600 text-white hover:bg-markenblau-700': ansicht === 'spalten' }"
        @click="ansicht = 'spalten'"
      >
        Spalten
      </button>
      <button
        v-if="sim.dual_modus"
        class="knopf-sekundaer text-xs"
        :class="{ 'bg-markenblau-600 text-white hover:bg-markenblau-700': ansicht === 'vergleich' }"
        @click="ansicht = 'vergleich'"
      >
        {{ t('simulation.vergleich') }}
      </button>
      <button
        v-if="sim.plattform_modus"
        class="knopf-sekundaer text-xs"
        :class="{ 'bg-markenblau-600 text-white hover:bg-markenblau-700': ansicht === 'feed' }"
        @click="ansicht = 'feed'"
      >
        Feed
      </button>
      <button
        v-if="sim.status === 'abgeschlossen'"
        class="knopf-sekundaer text-xs"
        :class="{ 'bg-markenblau-600 text-white hover:bg-markenblau-700': ansicht === 'replay' }"
        @click="ansicht = 'replay'; replaySchritt = 1"
      >
        Replay
      </button>
    </div>

    <article v-if="ansicht === 'replay'" class="karte space-y-3">
      <header class="flex items-center gap-3">
        <button class="knopf-primaer text-xs" @click="replaySpielen">
          {{ replaySpielt ? '⏸ Pause' : '▶ Play' }}
        </button>
        <span class="text-sm tabular-nums text-slate-500">
          Schritt {{ replaySchritt }} / {{ replaySchritte }}
        </span>
        <input
          v-model.number="replaySchritt"
          type="range"
          min="1"
          :max="replaySchritte"
          class="flex-1"
          @input="replayPause"
        />
      </header>

      <div class="grid gap-4" :class="sim.dual_modus ? 'lg:grid-cols-2' : ''">
        <div
          v-for="welt in (sim.dual_modus ? ['kontrolle', 'variante'] : ['kontrolle'])"
          :key="welt"
          class="rounded border-l-2 p-3"
          :class="welt === 'kontrolle' ? 'border-slate-300 dark:border-slate-600' : 'border-markenblau-400'"
        >
          <h3
            class="mb-2 text-xs font-semibold uppercase"
            :class="welt === 'kontrolle' ? 'text-slate-500' : 'text-markenblau-700 dark:text-markenblau-500'"
          >
            {{ welt }}
          </h3>
          <ul class="space-y-1 text-sm">
            <li
              v-for="(e, i) in sichtbareSchritte
                .filter((s) => s.welt === welt)
                .flatMap((s) => s.ereignisse.map((eg) => `[${s.nummer}] ${eg}`))"
              :key="i"
            >
              {{ e }}
            </li>
          </ul>
        </div>
      </div>
    </article>

    <article v-if="sim.status === 'abgeschlossen' && stimmungsReihen.length" class="karte">
      <h2 class="mb-2 text-sm font-semibold uppercase text-slate-500">Stimmungsverlauf</h2>
      <StimmungsDiagramm :reihen="stimmungsReihen" />
    </article>

    <article v-if="sim.plattform_modus && ansicht === 'feed'" class="space-y-4">
      <div v-if="sim.dual_modus" class="grid gap-4 lg:grid-cols-2">
        <div class="karte">
          <h3 class="mb-3 text-sm font-semibold uppercase text-slate-500">Kontroll-Welt</h3>
          <FeedAnzeige :feed="feed" :folgen="folgen" welt="kontrolle" />
        </div>
        <div class="karte">
          <h3 class="mb-3 text-sm font-semibold uppercase text-markenblau-700 dark:text-markenblau-500">
            Varianten-Welt
          </h3>
          <FeedAnzeige :feed="feed" :folgen="folgen" welt="variante" />
        </div>
      </div>
      <div v-else class="karte">
        <FeedAnzeige :feed="feed" :folgen="folgen" />
      </div>
    </article>

    <article v-else-if="sim.dual_modus && ansicht === 'vergleich'" class="karte overflow-x-auto">
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
