<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { RouterLink } from 'vue-router';

const { t } = useI18n();

const merkmale = [
  {
    titel: 'GraphRAG',
    text: 'Aus rohen Texten werden Entitäten und Beziehungen extrahiert und zu einem Wissensgraphen verdichtet.',
  },
  {
    titel: 'Persona-Generierung',
    text: 'Aus dem Wissensgraphen werden glaubwürdige Agenten mit eigener Geschichte und Werten erzeugt.',
  },
  {
    titel: 'Dual-Welt-Simulation',
    text: 'Eine Kontroll- und eine Variantenwelt laufen parallel — der Effekt einer Variable wird direkt sichtbar.',
  },
  {
    titel: 'Berichts-Agent',
    text: 'Ein Werkzeug-bewehrter Agent fasst die Simulation in einem lesbaren Bericht zusammen.',
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

    <div class="grid gap-4 md:grid-cols-2">
      <article v-for="m in merkmale" :key="m.titel" class="karte">
        <h2 class="text-lg font-semibold text-markenblau-700 dark:text-markenblau-500">{{ m.titel }}</h2>
        <p class="mt-2 text-sm text-slate-600 dark:text-slate-300">{{ m.text }}</p>
      </article>
    </div>
  </section>
</template>
