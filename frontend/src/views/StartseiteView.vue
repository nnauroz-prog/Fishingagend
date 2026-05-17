<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink } from 'vue-router';

import { apiClient } from '@/api/client';
import { simulationApi } from '@/api/simulation';
import { statistikenApi, type Statistiken } from '@/api/statistiken';
import type { Simulation } from '@/api/typen';
import { vorlagenApi, type Vorlage } from '@/api/vorlagen';
import Avatar from '@/components/Avatar.vue';

const { t } = useI18n();

const stats = ref<Statistiken | null>(null);
const letzteSims = ref<Simulation[]>([]);
const beliebteVorlagen = ref<Vorlage[]>([]);
const audit = ref<{ id: number; zeitstempel: string; aktion: string; ressource: string }[]>([]);

onMounted(async () => {
  const [s, sims, vorl, a] = await Promise.allSettled([
    statistikenApi.hole(),
    simulationApi.liste(),
    vorlagenApi.liste(),
    apiClient.get<typeof audit.value>('/api/audit', { params: { limit: 6 } }),
  ]);
  if (s.status === 'fulfilled') stats.value = s.value;
  if (sims.status === 'fulfilled') letzteSims.value = sims.value.slice(-3).reverse();
  if (vorl.status === 'fulfilled') beliebteVorlagen.value = vorl.value.slice(0, 3);
  if (a.status === 'fulfilled') audit.value = a.value.data;
});

const statusFarbe: Record<string, string> = {
  geplant: 'bg-slate-200 text-slate-700',
  laeuft: 'bg-yellow-100 text-yellow-700',
  abgeschlossen: 'bg-green-100 text-green-700',
  fehlgeschlagen: 'bg-red-100 text-red-700',
};

const kpis = computed(() => {
  if (!stats.value) return [];
  return [
    { titel: t('navigation.agenten'), wert: stats.value.agenten, ziel: '/agenten' },
    { titel: t('navigation.simulation'), wert: stats.value.simulationen, ziel: '/simulation' },
    { titel: 'Entitäten', wert: stats.value.entitaeten, ziel: '/graphrag' },
    { titel: 'Beziehungen', wert: stats.value.beziehungen, ziel: '/beziehungen' },
  ];
});
</script>

<template>
  <section class="space-y-8">
    <!-- Hero -->
    <div class="text-center">
      <h1 class="text-3xl font-bold tracking-tight sm:text-4xl">
        {{ t('startseite.ueberschrift') }}
      </h1>
      <p class="mx-auto mt-3 max-w-2xl text-slate-600 dark:text-slate-300">
        {{ t('startseite.einleitung') }}
      </p>
      <div class="mt-5 flex flex-wrap justify-center gap-2">
        <RouterLink to="/pipeline" class="knopf-primaer">
          {{ t('navigation.pipeline') }} →
        </RouterLink>
        <RouterLink to="/vorlagen" class="knopf-sekundaer">
          {{ t('navigation.vorlagen') }}
        </RouterLink>
      </div>
    </div>

    <!-- KPI-Kacheln -->
    <div v-if="kpis.length" class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <RouterLink
        v-for="k in kpis"
        :key="k.ziel"
        :to="k.ziel"
        class="karte text-center transition hover:border-markenblau-500"
      >
        <p class="text-3xl font-black text-markenblau-600">{{ k.wert }}</p>
        <p class="text-xs uppercase text-slate-500">{{ k.titel }}</p>
      </RouterLink>
    </div>

    <!-- Zwei Spalten: letzte Sims + Vorlagen-Quicklinks -->
    <div class="grid gap-4 lg:grid-cols-2">
      <article class="karte">
        <header class="mb-3 flex items-center justify-between">
          <h2 class="text-sm font-semibold uppercase text-slate-500">
            {{ t('startseite.letzte_sims') }}
          </h2>
          <RouterLink to="/simulation" class="text-xs text-markenblau-600 hover:underline">
            Alle →
          </RouterLink>
        </header>
        <ul v-if="letzteSims.length" class="space-y-2 text-sm">
          <li
            v-for="sim in letzteSims"
            :key="sim.id"
            class="flex items-center justify-between rounded border border-slate-100 px-3 py-2 dark:border-slate-700"
          >
            <RouterLink
              :to="`/simulation/${sim.id}`"
              class="truncate font-medium hover:text-markenblau-700"
            >
              {{ sim.name }}
            </RouterLink>
            <span
              class="ml-2 shrink-0 rounded-full px-2 py-0.5 text-xs"
              :class="statusFarbe[sim.status] ?? 'bg-slate-100'"
            >
              {{ t(`simulation.status_${sim.status}`) }}
            </span>
          </li>
        </ul>
        <p v-else class="text-sm text-slate-500">
          {{ t('startseite.keine_sims') }}
        </p>
      </article>

      <article class="karte">
        <header class="mb-3 flex items-center justify-between">
          <h2 class="text-sm font-semibold uppercase text-slate-500">
            {{ t('startseite.vorlagen') }}
          </h2>
          <RouterLink to="/vorlagen" class="text-xs text-markenblau-600 hover:underline">
            Alle →
          </RouterLink>
        </header>
        <ul class="space-y-2 text-sm">
          <li
            v-for="v in beliebteVorlagen"
            :key="v.schluessel"
            class="rounded border border-slate-100 px-3 py-2 dark:border-slate-700"
          >
            <div class="flex items-center justify-between">
              <span class="font-medium">{{ v.titel }}</span>
              <span class="text-xs text-slate-500">{{ v.kategorie }}</span>
            </div>
            <p class="mt-1 line-clamp-1 text-xs text-slate-500">{{ v.beschreibung }}</p>
          </li>
        </ul>
      </article>
    </div>

    <!-- Audit-Aktivität -->
    <article v-if="audit.length" class="karte">
      <header class="mb-3 flex items-center justify-between">
        <h2 class="text-sm font-semibold uppercase text-slate-500">
          {{ t('startseite.letzte_aktivitaet') }}
        </h2>
        <RouterLink to="/audit" class="text-xs text-markenblau-600 hover:underline">
          Alle →
        </RouterLink>
      </header>
      <ul class="space-y-1 text-sm">
        <li
          v-for="e in audit"
          :key="e.id"
          class="flex items-center gap-3 rounded px-2 py-1 text-xs hover:bg-slate-50 dark:hover:bg-slate-700"
        >
          <span class="w-32 shrink-0 font-mono text-slate-400">
            {{ new Date(e.zeitstempel).toLocaleTimeString('de-DE') }}
          </span>
          <Avatar :name="e.aktion" groesse="klein" />
          <span class="flex-1 truncate">
            <strong>{{ e.aktion }}</strong> · {{ e.ressource }}
          </span>
        </li>
      </ul>
    </article>
  </section>
</template>
