<script setup lang="ts">
import { computed } from 'vue';

import type { Simulation, SimulationSchritt } from '@/api/typen';

const props = defineProps<{ simulation: Simulation }>();

interface Paar {
  nummer: number;
  kontrolle: SimulationSchritt | null;
  variante: SimulationSchritt | null;
}

const paare = computed<Paar[]>(() => {
  const map = new Map<number, Paar>();
  for (const s of props.simulation.verlauf) {
    const eintrag = map.get(s.nummer) ?? { nummer: s.nummer, kontrolle: null, variante: null };
    if (s.welt === 'kontrolle') eintrag.kontrolle = s;
    else eintrag.variante = s;
    map.set(s.nummer, eintrag);
  }
  return Array.from(map.values()).sort((a, b) => a.nummer - b.nummer);
});

function unterschiedlich(a: SimulationSchritt | null, b: SimulationSchritt | null): boolean {
  if (!a || !b) return true;
  return JSON.stringify(a.ereignisse) !== JSON.stringify(b.ereignisse);
}
</script>

<template>
  <table class="w-full table-fixed border-collapse">
    <thead>
      <tr class="border-b border-slate-200 text-left text-xs uppercase text-slate-500 dark:border-slate-700">
        <th class="w-16 py-2">#</th>
        <th class="py-2">Kontroll-Welt</th>
        <th class="py-2 text-markenblau-700 dark:text-markenblau-500">Varianten-Welt</th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="p in paare"
        :key="p.nummer"
        class="border-b border-slate-100 align-top dark:border-slate-700/60"
        :class="unterschiedlich(p.kontrolle, p.variante) ? 'bg-yellow-50/40 dark:bg-yellow-900/10' : ''"
      >
        <td class="py-3 text-xs text-slate-500">{{ p.nummer }}</td>
        <td class="py-3 pr-4 text-sm">
          <ul class="space-y-1">
            <li v-for="(e, i) in p.kontrolle?.ereignisse ?? []" :key="`k-${i}`">{{ e }}</li>
          </ul>
          <p v-if="!p.kontrolle" class="text-slate-400">—</p>
        </td>
        <td class="py-3 pl-4 text-sm border-l border-slate-200 dark:border-slate-700">
          <ul class="space-y-1">
            <li v-for="(e, i) in p.variante?.ereignisse ?? []" :key="`v-${i}`">{{ e }}</li>
          </ul>
          <p v-if="!p.variante" class="text-slate-400">—</p>
        </td>
      </tr>
    </tbody>
  </table>
</template>
