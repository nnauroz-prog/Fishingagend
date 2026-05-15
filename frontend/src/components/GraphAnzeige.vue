<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, shallowRef, watch } from 'vue';

import type { Graph } from '@/api/graphrag';
import { erstelleLayout, type KnotenPos } from '@/werkzeuge/forcelayout';

const props = defineProps<{ graph: Graph }>();

const breite = 720;
const hoehe = 480;

const knotenPos = shallowRef<KnotenPos[]>([]);
const aktiv = ref<string | null>(null);
let timer: number | null = null;

const farbe = (typ: string) => {
  const palette: Record<string, string> = {
    Person: '#2563eb',
    Organisation: '#0d9488',
    Ort: '#ca8a04',
    Konzept: '#7c3aed',
    Ereignis: '#dc2626',
  };
  return palette[typ] ?? '#64748b';
};

const ids = computed(() => props.graph.entitaeten.map((e) => e.name));
const kanten = computed(() => props.graph.beziehungen.map((b) => ({ von: b.von, nach: b.nach })));
const typVon = computed(() => {
  const m = new Map<string, string>();
  props.graph.entitaeten.forEach((e) => m.set(e.name, e.typ));
  return m;
});

function neuStart() {
  if (!ids.value.length) {
    knotenPos.value = [];
    if (timer) cancelAnimationFrame(timer);
    timer = null;
    return;
  }
  const layout = erstelleLayout(ids.value, kanten.value, breite, hoehe);
  let iterationen = 0;
  function tick() {
    layout.schritt();
    knotenPos.value = [...layout.knoten.values()];
    iterationen++;
    if (iterationen < 300) timer = requestAnimationFrame(tick);
    else timer = null;
  }
  tick();
}

const positionVon = computed(() => {
  const m = new Map<string, KnotenPos>();
  knotenPos.value.forEach((k) => m.set(k.id, k));
  return m;
});

onMounted(neuStart);
onUnmounted(() => {
  if (timer) cancelAnimationFrame(timer);
});
watch(
  () => props.graph,
  () => neuStart(),
  { deep: true },
);
</script>

<template>
  <div class="overflow-hidden rounded-lg bg-slate-50 dark:bg-slate-900">
    <svg
      :viewBox="`0 0 ${breite} ${hoehe}`"
      :width="breite"
      :height="hoehe"
      class="h-auto w-full max-w-full"
      role="img"
      aria-label="Wissensgraph"
    >
      <g stroke="currentColor" class="text-slate-300 dark:text-slate-600">
        <line
          v-for="(b, i) in graph.beziehungen"
          :key="i"
          :x1="positionVon.get(b.von)?.x ?? 0"
          :y1="positionVon.get(b.von)?.y ?? 0"
          :x2="positionVon.get(b.nach)?.x ?? 0"
          :y2="positionVon.get(b.nach)?.y ?? 0"
          :stroke-width="Math.max(1, b.gewicht * 2)"
          stroke-opacity="0.6"
        />
      </g>

      <g>
        <g
          v-for="k in knotenPos"
          :key="k.id"
          :transform="`translate(${k.x}, ${k.y})`"
          class="cursor-pointer"
          @mouseover="aktiv = k.id"
          @mouseleave="aktiv = null"
        >
          <circle
            r="14"
            :fill="farbe(typVon.get(k.id) ?? '')"
            stroke="white"
            stroke-width="2"
          />
          <text
            y="28"
            text-anchor="middle"
            class="fill-current text-[10px] text-slate-700 dark:text-slate-200"
          >
            {{ k.id.length > 18 ? k.id.slice(0, 16) + '…' : k.id }}
          </text>
        </g>
      </g>
    </svg>

    <p v-if="!graph.entitaeten.length" class="p-6 text-center text-sm text-slate-500">
      Noch keine Entitäten. Bitte zuerst einen Text extrahieren.
    </p>
  </div>
</template>
