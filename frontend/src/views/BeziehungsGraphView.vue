<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, shallowRef, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import { agentenApi } from '@/api/agenten';
import { erstelleLayout, type KnotenPos } from '@/werkzeuge/forcelayout';

const { t } = useI18n();
const router = useRouter();

interface GraphKnoten {
  id: string;
  agent_id: string | null;
  typ: 'agent' | 'extern';
  beruf: string;
}
interface GraphKante {
  von: string;
  nach: string;
  beschreibung: string;
}

const knoten = ref<GraphKnoten[]>([]);
const kanten = ref<GraphKante[]>([]);
const ladend = ref(true);

const breite = 900;
const hoehe = 560;

const positionen = shallowRef<KnotenPos[]>([]);
const aktiv = ref<string | null>(null);
let timer: number | null = null;

const positionVon = computed(() => {
  const m = new Map<string, KnotenPos>();
  positionen.value.forEach((k) => m.set(k.id, k));
  return m;
});

const knotenIndex = computed(() => {
  const m = new Map<string, GraphKnoten>();
  knoten.value.forEach((k) => m.set(k.id, k));
  return m;
});

const aktiveKnotenInfo = computed(() => (aktiv.value ? knotenIndex.value.get(aktiv.value) : null));

const aktiveKanten = computed(() =>
  aktiv.value
    ? kanten.value.filter((k) => k.von === aktiv.value || k.nach === aktiv.value)
    : [],
);

function neuStart() {
  if (timer) cancelAnimationFrame(timer);
  if (!knoten.value.length) {
    positionen.value = [];
    return;
  }
  const layout = erstelleLayout(
    knoten.value.map((k) => k.id),
    kanten.value.map((k) => ({ von: k.von, nach: k.nach })),
    breite,
    hoehe,
  );
  let i = 0;
  function tick() {
    layout.schritt();
    positionen.value = [...layout.knoten.values()];
    i++;
    if (i < 350) timer = requestAnimationFrame(tick);
    else timer = null;
  }
  tick();
}

async function laden() {
  ladend.value = true;
  try {
    const r = await agentenApi.beziehungsGraph();
    knoten.value = r.knoten;
    kanten.value = r.kanten;
  } finally {
    ladend.value = false;
  }
  neuStart();
}

function farbe(k: GraphKnoten): string {
  return k.typ === 'agent' ? '#2563eb' : '#94a3b8';
}

function gehe(k: GraphKnoten) {
  if (k.agent_id) router.push({ name: 'agent-detail', params: { id: k.agent_id } });
}

onMounted(laden);
onUnmounted(() => {
  if (timer) cancelAnimationFrame(timer);
});
watch(knoten, () => neuStart(), { deep: true });
</script>

<template>
  <section class="space-y-6">
    <header class="flex items-start justify-between">
      <div>
        <h1 class="text-2xl font-bold">{{ t('beziehungs_graph.titel') }}</h1>
        <p class="text-sm text-slate-500">{{ t('beziehungs_graph.einleitung') }}</p>
      </div>
      <button class="knopf-sekundaer text-xs" @click="laden">↻</button>
    </header>

    <p v-if="ladend" class="text-sm text-slate-500">…</p>
    <p v-else-if="!knoten.length" class="text-sm text-slate-500">
      {{ t('beziehungs_graph.leer') }}
    </p>

    <div v-else class="grid gap-4 lg:grid-cols-[1fr,18rem]">
      <div class="karte overflow-hidden">
        <svg
          :viewBox="`0 0 ${breite} ${hoehe}`"
          :width="breite"
          :height="hoehe"
          class="h-auto w-full max-w-full"
          role="img"
          :aria-label="t('beziehungs_graph.titel')"
        >
          <g class="text-slate-300 dark:text-slate-600">
            <line
              v-for="(k, i) in kanten"
              :key="i"
              :x1="positionVon.get(k.von)?.x ?? 0"
              :y1="positionVon.get(k.von)?.y ?? 0"
              :x2="positionVon.get(k.nach)?.x ?? 0"
              :y2="positionVon.get(k.nach)?.y ?? 0"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-opacity="0.6"
            />
          </g>
          <g
            v-for="k in positionen"
            :key="k.id"
            :transform="`translate(${k.x}, ${k.y})`"
            class="cursor-pointer"
            @click="gehe(knotenIndex.get(k.id)!)"
            @mouseover="aktiv = k.id"
            @mouseleave="aktiv = null"
          >
            <circle
              :r="aktiv === k.id ? 16 : 12"
              :fill="farbe(knotenIndex.get(k.id)!)"
              stroke="white"
              stroke-width="2"
            />
            <text
              y="26"
              text-anchor="middle"
              class="fill-current text-[11px] text-slate-700 dark:text-slate-200"
            >
              {{ k.id.length > 22 ? k.id.slice(0, 20) + '…' : k.id }}
            </text>
          </g>
        </svg>
      </div>

      <aside class="karte text-sm">
        <h2 class="mb-2 text-xs font-semibold uppercase text-slate-500">
          {{ t('beziehungs_graph.detail') }}
        </h2>

        <div v-if="aktiveKnotenInfo">
          <p class="text-base font-semibold">{{ aktiveKnotenInfo.id }}</p>
          <p v-if="aktiveKnotenInfo.beruf" class="text-xs text-slate-500">
            {{ aktiveKnotenInfo.beruf }}
          </p>
          <p class="mt-1 text-xs text-slate-400">{{ aktiveKnotenInfo.typ }}</p>

          <h3 v-if="aktiveKanten.length" class="mt-3 text-xs font-semibold uppercase text-slate-500">
            {{ t('beziehungs_graph.kanten') }}
          </h3>
          <ul class="mt-1 space-y-1.5 text-xs">
            <li v-for="(k, i) in aktiveKanten" :key="i" class="rounded bg-slate-50 p-2 dark:bg-slate-700">
              <strong>{{ k.von === aktiveKnotenInfo.id ? '→' : '←' }} {{ k.von === aktiveKnotenInfo.id ? k.nach : k.von }}</strong>
              <p class="text-slate-600 dark:text-slate-300">{{ k.beschreibung }}</p>
            </li>
          </ul>
        </div>

        <div v-else class="space-y-2 text-xs text-slate-500">
          <p>{{ t('beziehungs_graph.hover_hinweis') }}</p>
          <p class="pt-2"><strong>{{ knoten.length }}</strong> {{ t('beziehungs_graph.knoten_zaehler') }}</p>
          <p><strong>{{ kanten.length }}</strong> {{ t('beziehungs_graph.kanten_zaehler') }}</p>
        </div>

        <div class="mt-4 border-t border-slate-200 pt-3 text-xs dark:border-slate-700">
          <div class="flex items-center gap-2">
            <span class="inline-block h-3 w-3 rounded-full bg-markenblau-600" /> Agent
          </div>
          <div class="mt-1 flex items-center gap-2">
            <span class="inline-block h-3 w-3 rounded-full bg-slate-400" /> Extern
          </div>
        </div>
      </aside>
    </div>
  </section>
</template>
