<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink } from 'vue-router';

import { statistikenApi, type Statistiken } from '@/api/statistiken';

const { t } = useI18n();

const stats = ref<Statistiken | null>(null);

onMounted(async () => {
  try {
    stats.value = await statistikenApi.hole();
  } catch {
    // Backend evtl. nicht erreichbar — Startseite ist trotzdem nutzbar
  }
});

const merkmale = [
  {
    titel: 'GraphRAG',
    text: 'Aus rohen Texten werden Entitäten und Beziehungen extrahiert und zu einem Wissensgraphen verdichtet.',
    ziel: '/graphrag',
  },
  {
    titel: 'Persona-Generierung',
    text: 'Aus Saat-Stichworten werden glaubwürdige Agenten mit eigener Geschichte und Werten erzeugt.',
    ziel: '/agenten',
  },
  {
    titel: 'Dual-Welt-Simulation',
    text: 'Eine Kontroll- und eine Variantenwelt laufen parallel — der Effekt einer Variable wird direkt sichtbar.',
    ziel: '/simulation',
  },
  {
    titel: 'Berichts-Agent',
    text: 'Ein LLM-gestützter Agent fasst die Simulation in einem lesbaren Markdown-Bericht zusammen.',
    ziel: '/berichte',
  },
];
</script>

<template>
  <section class="space-y-12">
    <div class="text-center">
      <h1 class="text-4xl font-bold tracking-tight sm:text-5xl">
        {{ t('startseite.ueberschrift') }}
      </h1>
      <p class="mx-auto mt-4 max-w-2xl text-lg text-slate-600 dark:text-slate-300">
        {{ t('startseite.einleitung') }}
      </p>
      <RouterLink to="/agenten" class="knopf-primaer mt-6">
        {{ t('startseite.los') }}
      </RouterLink>
    </div>

    <div v-if="stats" class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <RouterLink
        to="/agenten"
        class="karte text-center transition hover:border-markenblau-500"
      >
        <p class="text-3xl font-black text-markenblau-600">{{ stats.agenten }}</p>
        <p class="text-xs uppercase text-slate-500">{{ t('navigation.agenten') }}</p>
      </RouterLink>
      <RouterLink
        to="/simulation"
        class="karte text-center transition hover:border-markenblau-500"
      >
        <p class="text-3xl font-black text-markenblau-600">{{ stats.simulationen }}</p>
        <p class="text-xs uppercase text-slate-500">{{ t('navigation.simulation') }}</p>
      </RouterLink>
      <RouterLink
        to="/graphrag"
        class="karte text-center transition hover:border-markenblau-500"
      >
        <p class="text-3xl font-black text-markenblau-600">{{ stats.entitaeten }}</p>
        <p class="text-xs uppercase text-slate-500">Entitäten</p>
      </RouterLink>
      <RouterLink
        to="/graphrag"
        class="karte text-center transition hover:border-markenblau-500"
      >
        <p class="text-3xl font-black text-markenblau-600">{{ stats.beziehungen }}</p>
        <p class="text-xs uppercase text-slate-500">Beziehungen</p>
      </RouterLink>
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <RouterLink
        v-for="m in merkmale"
        :key="m.titel"
        :to="m.ziel"
        class="karte transition hover:-translate-y-0.5 hover:border-markenblau-500"
      >
        <h2 class="text-lg font-semibold text-markenblau-700 dark:text-markenblau-500">
          {{ m.titel }} →
        </h2>
        <p class="mt-2 text-sm text-slate-600 dark:text-slate-300">{{ m.text }}</p>
      </RouterLink>
    </div>
  </section>
</template>
