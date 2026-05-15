<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { graphragApi, type Graph } from '@/api/graphrag';
import GraphAnzeige from '@/components/GraphAnzeige.vue';
import { useToastStore } from '@/store/toasts';

const { t } = useI18n();
const toasts = useToastStore();

const text = ref('');
const frage = ref('');
const graph = ref<Graph>({ entitaeten: [], beziehungen: [] });
const antwort = ref<string | null>(null);
const verarbeitet = ref(false);

async function laden() {
  graph.value = await graphragApi.lade();
}

async function extrahieren() {
  if (!text.value.trim()) return;
  verarbeitet.value = true;
  try {
    graph.value = await graphragApi.extrahiere([text.value]);
    toasts.erfolg(
      `${graph.value.entitaeten.length} Entitäten · ${graph.value.beziehungen.length} Beziehungen`,
    );
    text.value = '';
  } finally {
    verarbeitet.value = false;
  }
}

async function leeren() {
  if (!confirm('Den gesamten Wissensgraphen wirklich löschen?')) return;
  await graphragApi.loesche();
  graph.value = { entitaeten: [], beziehungen: [] };
  toasts.info('Wissensgraph geleert.');
}

async function abfragen() {
  if (!frage.value.trim()) return;
  antwort.value = null;
  const r = await graphragApi.abfrage(frage.value);
  antwort.value = r.antwort;
}

onMounted(laden);
</script>

<template>
  <section class="space-y-6">
    <header class="flex items-start justify-between gap-2">
      <div>
        <h1 class="text-2xl font-bold">{{ t('graphrag.titel') }}</h1>
        <p class="text-sm text-slate-500">{{ t('graphrag.einleitung') }}</p>
      </div>
      <button
        v-if="graph.entitaeten.length"
        class="knopf-sekundaer text-xs"
        @click="leeren"
      >
        {{ t('graphrag.leeren') }}
      </button>
    </header>

    <article class="karte space-y-3">
      <h2 class="font-semibold">{{ t('graphrag.extrahieren') }}</h2>
      <textarea
        v-model="text"
        rows="6"
        class="eingabe font-mono text-sm"
        :placeholder="t('graphrag.text_platzhalter')"
      />
      <button class="knopf-primaer" :disabled="verarbeitet" @click="extrahieren">
        {{ verarbeitet ? t('graphrag.verarbeitet') : t('graphrag.extrahieren_knopf') }}
      </button>
    </article>

    <article class="karte space-y-2">
      <header class="flex items-center justify-between">
        <h2 class="font-semibold">{{ t('graphrag.graph') }}</h2>
        <p class="text-xs text-slate-500">
          {{ graph.entitaeten.length }} Entitäten · {{ graph.beziehungen.length }} Beziehungen
        </p>
      </header>
      <GraphAnzeige :graph="graph" />
    </article>

    <article class="karte space-y-3">
      <h2 class="font-semibold">{{ t('graphrag.abfragen') }}</h2>
      <div class="flex gap-2">
        <input
          v-model="frage"
          class="eingabe flex-1"
          :placeholder="t('graphrag.frage_platzhalter')"
          @keyup.enter="abfragen"
        />
        <button class="knopf-primaer" @click="abfragen">{{ t('graphrag.fragen') }}</button>
      </div>
      <p v-if="antwort" class="rounded bg-slate-50 p-3 text-sm dark:bg-slate-700">{{ antwort }}</p>
    </article>
  </section>
</template>
