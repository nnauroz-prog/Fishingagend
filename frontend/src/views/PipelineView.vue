<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import { agentenApi } from '@/api/agenten';
import { graphragApi, type Graph } from '@/api/graphrag';
import { simulationApi } from '@/api/simulation';
import { useAgentenStore } from '@/store/agenten';
import { useSimulationStore } from '@/store/simulation';
import { useToastStore } from '@/store/toasts';

const { t } = useI18n();
const router = useRouter();
const toasts = useToastStore();
const agentenStore = useAgentenStore();
const simStore = useSimulationStore();

const aktuellePhase = ref(1);

interface PhasenZustand {
  saatTexte: string;
  graph: Graph | null;
  maxPersonen: number;
  angelegteAgenten: string[];
  simName: string;
  simSchritte: number;
  simVariableJson: string;
  simDual: boolean;
  simId: string | null;
  bericht: string | null;
}

const z = reactive<PhasenZustand>({
  saatTexte: '',
  graph: null,
  maxPersonen: 5,
  angelegteAgenten: [],
  simName: 'Pipeline-Lauf',
  simSchritte: 5,
  simVariableJson: '{}',
  simDual: true,
  simId: null,
  bericht: null,
});

const arbeitet = ref(false);

const phasen = [
  { nummer: 1, titel: 'Graph-Aufbau', untertitel: 'GraphRAG aus Saat-Texten' },
  { nummer: 2, titel: 'Umgebungs-Setup', untertitel: 'Personas aus dem Graph erzeugen' },
  { nummer: 3, titel: 'Simulation', untertitel: 'Dual-Welt-Simulation starten' },
  { nummer: 4, titel: 'Berichts-Generierung', untertitel: 'ReportAgent mit Werkzeugen' },
  { nummer: 5, titel: 'Tiefe Interaktion', untertitel: 'Chat mit Agenten und Bericht' },
];

const fortschritt = computed(() => Math.round(((aktuellePhase.value - 1) / 5) * 100));

onMounted(async () => {
  z.graph = await graphragApi.lade();
  if (z.graph.entitaeten.length) aktuellePhase.value = 2;
});

async function phase1() {
  if (!z.saatTexte.trim()) {
    toasts.fehler('Bitte zuerst einen Saat-Text einfügen.');
    return;
  }
  arbeitet.value = true;
  try {
    z.graph = await graphragApi.extrahiere([z.saatTexte]);
    toasts.erfolg(`${z.graph.entitaeten.length} Entitäten · ${z.graph.beziehungen.length} Beziehungen`);
    aktuellePhase.value = 2;
  } finally {
    arbeitet.value = false;
  }
}

async function phase2() {
  arbeitet.value = true;
  try {
    const angelegte = await agentenApi.ausGraph(z.maxPersonen, true);
    z.angelegteAgenten = angelegte.map((a) => a.id);
    await agentenStore.laden();
    toasts.erfolg(`${angelegte.length} Agenten angelegt.`);
    aktuellePhase.value = 3;
  } finally {
    arbeitet.value = false;
  }
}

async function phase3() {
  arbeitet.value = true;
  try {
    let variable: Record<string, unknown> = {};
    try {
      variable = z.simVariableJson.trim() ? JSON.parse(z.simVariableJson) : {};
    } catch {
      toasts.fehler('Variable ist kein gültiges JSON.');
      return;
    }
    const ids = z.angelegteAgenten.length
      ? z.angelegteAgenten
      : agentenStore.agenten.slice(0, 8).map((a) => a.id);
    if (!ids.length) {
      toasts.fehler('Keine Agenten verfügbar.');
      return;
    }
    const sim = await simStore.planen({
      name: z.simName,
      agent_ids: ids,
      schritte: z.simSchritte,
      variable,
      dual_modus: z.simDual,
    });
    z.simId = sim.id;
    await simStore.starten(sim.id, true);
    toasts.erfolg('Simulation abgeschlossen.');
    aktuellePhase.value = 4;
  } finally {
    arbeitet.value = false;
  }
}

async function phase4() {
  if (!z.simId) return;
  arbeitet.value = true;
  try {
    const r = await simulationApi.bericht(z.simId);
    z.bericht = r.markdown;
    aktuellePhase.value = 5;
  } finally {
    arbeitet.value = false;
  }
}

function phase5() {
  if (z.simId) router.push({ name: 'simulation-detail', params: { id: z.simId } });
}

const beispielText = `Anna Schmidt forscht seit zehn Jahren am IPCC zu Extremwetterereignissen.
Markus König ist Bürgermeister einer Mittelstadt am Rhein.
Yuki Tanaka organisiert Klima-Demonstrationen in Hamburg.
Anna und Yuki kennen sich aus einem gemeinsamen Aktionsbündnis.`;
</script>

<template>
  <section class="space-y-6">
    <header>
      <h1 class="text-2xl font-bold">{{ t('pipeline.titel') }}</h1>
      <p class="text-sm text-slate-500">{{ t('pipeline.einleitung') }}</p>
    </header>

    <!-- Fortschrittsleiste -->
    <div class="karte">
      <div class="mb-3 flex items-center gap-2 overflow-x-auto">
        <button
          v-for="p in phasen"
          :key="p.nummer"
          class="flex shrink-0 items-center gap-2 rounded-full px-3 py-1.5 text-xs transition"
          :class="
            aktuellePhase === p.nummer
              ? 'bg-markenblau-600 text-white'
              : aktuellePhase > p.nummer
                ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-200'
                : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
          "
          @click="aktuellePhase = p.nummer"
        >
          <span class="font-bold">{{ p.nummer }}</span>
          <span>{{ p.titel }}</span>
        </button>
      </div>
      <div class="h-1.5 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
        <div class="h-full bg-markenblau-600 transition-all" :style="{ width: `${fortschritt}%` }" />
      </div>
    </div>

    <!-- Phase 1 -->
    <article v-if="aktuellePhase === 1" class="karte space-y-3">
      <h2 class="text-lg font-semibold">1 · {{ phasen[0].titel }}</h2>
      <p class="text-sm text-slate-500">{{ t('pipeline.phase1') }}</p>
      <textarea
        v-model="z.saatTexte"
        rows="8"
        class="eingabe font-mono text-sm"
        :placeholder="beispielText"
      />
      <div class="flex gap-2">
        <button class="knopf-primaer" :disabled="arbeitet" @click="phase1">
          {{ arbeitet ? '…' : t('pipeline.weiter') }}
        </button>
        <button class="knopf-sekundaer text-xs" @click="z.saatTexte = beispielText">
          {{ t('pipeline.beispiel') }}
        </button>
      </div>
    </article>

    <!-- Phase 2 -->
    <article v-else-if="aktuellePhase === 2" class="karte space-y-3">
      <h2 class="text-lg font-semibold">2 · {{ phasen[1].titel }}</h2>
      <p class="text-sm text-slate-500">{{ t('pipeline.phase2') }}</p>
      <p v-if="z.graph" class="text-xs text-slate-500">
        Graph: {{ z.graph.entitaeten.length }} Entitäten ·
        {{ z.graph.entitaeten.filter((e) => e.typ.toLowerCase() === 'person').length }} Personen
      </p>
      <div>
        <label class="etikett">Maximale Personen-Personas</label>
        <input v-model.number="z.maxPersonen" type="number" min="1" max="20" class="eingabe" />
      </div>
      <div class="flex gap-2">
        <button class="knopf-sekundaer" @click="aktuellePhase = 1">← Zurück</button>
        <button class="knopf-primaer" :disabled="arbeitet" @click="phase2">
          {{ arbeitet ? '…' : t('pipeline.weiter') }}
        </button>
      </div>
    </article>

    <!-- Phase 3 -->
    <article v-else-if="aktuellePhase === 3" class="karte space-y-3">
      <h2 class="text-lg font-semibold">3 · {{ phasen[2].titel }}</h2>
      <p class="text-sm text-slate-500">{{ t('pipeline.phase3') }}</p>
      <div class="grid gap-3 sm:grid-cols-2">
        <div>
          <label class="etikett">Name</label>
          <input v-model="z.simName" class="eingabe" />
        </div>
        <div>
          <label class="etikett">Schritte</label>
          <input v-model.number="z.simSchritte" type="number" min="1" max="50" class="eingabe" />
        </div>
        <div class="sm:col-span-2">
          <label class="etikett">Variable (JSON)</label>
          <textarea v-model="z.simVariableJson" rows="2" class="eingabe font-mono text-xs" />
        </div>
        <label class="etikett sm:col-span-2">
          <input v-model="z.simDual" type="checkbox" class="mr-2" />
          {{ t('simulation.dual_modus') }}
        </label>
      </div>
      <div class="flex gap-2">
        <button class="knopf-sekundaer" @click="aktuellePhase = 2">← Zurück</button>
        <button class="knopf-primaer" :disabled="arbeitet" @click="phase3">
          {{ arbeitet ? '…' : t('pipeline.starte') }}
        </button>
      </div>
    </article>

    <!-- Phase 4 -->
    <article v-else-if="aktuellePhase === 4" class="karte space-y-3">
      <h2 class="text-lg font-semibold">4 · {{ phasen[3].titel }}</h2>
      <p class="text-sm text-slate-500">{{ t('pipeline.phase4') }}</p>
      <div class="flex gap-2">
        <button class="knopf-sekundaer" @click="aktuellePhase = 3">← Zurück</button>
        <button class="knopf-primaer" :disabled="arbeitet" @click="phase4">
          {{ arbeitet ? '…' : t('pipeline.bericht_erstellen') }}
        </button>
      </div>
      <pre v-if="z.bericht" class="whitespace-pre-wrap rounded bg-slate-50 p-3 text-xs dark:bg-slate-700">{{ z.bericht }}</pre>
    </article>

    <!-- Phase 5 -->
    <article v-else-if="aktuellePhase === 5" class="karte space-y-3">
      <h2 class="text-lg font-semibold">5 · {{ phasen[4].titel }}</h2>
      <p class="text-sm text-slate-500">{{ t('pipeline.phase5') }}</p>
      <div class="grid gap-2 sm:grid-cols-2">
        <RouterLink to="/agenten" class="karte text-center transition hover:border-markenblau-500">
          <p class="font-semibold">→ {{ t('navigation.chat') }}</p>
          <p class="text-xs text-slate-500">Mit einem Agenten sprechen</p>
        </RouterLink>
        <button
          class="karte text-center transition hover:border-markenblau-500"
          @click="phase5"
        >
          <p class="font-semibold">→ {{ t('pipeline.bericht_chat') }}</p>
          <p class="text-xs text-slate-500">Mit dem ReportAgent chatten</p>
        </button>
      </div>
    </article>
  </section>
</template>
