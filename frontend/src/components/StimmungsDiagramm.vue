<script setup lang="ts">
import { computed } from 'vue';

interface Punkt {
  schritt: number;
  score: number;
}

const props = defineProps<{
  reihen: { name: string; farbe: string; daten: Punkt[] }[];
}>();

const breite = 720;
const hoehe = 220;
const padding = 30;

const maxSchritt = computed(() =>
  Math.max(1, ...props.reihen.flatMap((r) => r.daten.map((d) => d.schritt))),
);

function x(schritt: number): number {
  if (maxSchritt.value <= 1) return padding;
  return padding + ((schritt - 1) / (maxSchritt.value - 1)) * (breite - 2 * padding);
}

function y(score: number): number {
  // -1 → unten, +1 → oben
  return (hoehe / 2) - score * ((hoehe / 2) - padding);
}

function pfad(daten: Punkt[]): string {
  if (!daten.length) return '';
  return daten
    .map((d, i) => `${i === 0 ? 'M' : 'L'} ${x(d.schritt)} ${y(d.score)}`)
    .join(' ');
}

const ticks = [-1, -0.5, 0, 0.5, 1];
</script>

<template>
  <svg
    :viewBox="`0 0 ${breite} ${hoehe}`"
    :width="breite"
    :height="hoehe"
    class="h-auto w-full max-w-full"
    role="img"
    aria-label="Stimmungsverlauf"
  >
    <!-- Y-Gitter -->
    <g class="text-slate-200 dark:text-slate-700">
      <line
        v-for="t in ticks"
        :key="t"
        :x1="padding"
        :x2="breite - padding"
        :y1="y(t)"
        :y2="y(t)"
        stroke="currentColor"
        :stroke-dasharray="t === 0 ? 'none' : '2 4'"
      />
    </g>
    <g class="text-slate-400">
      <text
        v-for="t in ticks"
        :key="`l-${t}`"
        :x="padding - 6"
        :y="y(t) + 3"
        text-anchor="end"
        class="fill-current text-[9px]"
      >
        {{ t > 0 ? '+' : '' }}{{ t }}
      </text>
    </g>

    <!-- Datenreihen -->
    <g v-for="r in reihen" :key="r.name">
      <path :d="pfad(r.daten)" fill="none" :stroke="r.farbe" stroke-width="2" />
      <circle
        v-for="(p, i) in r.daten"
        :key="i"
        :cx="x(p.schritt)"
        :cy="y(p.score)"
        r="3"
        :fill="r.farbe"
      />
    </g>

    <!-- Legende -->
    <g>
      <g
        v-for="(r, i) in reihen"
        :key="`leg-${r.name}`"
        :transform="`translate(${padding + i * 130}, ${hoehe - 6})`"
      >
        <rect width="10" height="10" :fill="r.farbe" />
        <text x="14" y="9" class="fill-current text-[11px] text-slate-600 dark:text-slate-300">
          {{ r.name }}
        </text>
      </g>
    </g>
  </svg>
</template>
