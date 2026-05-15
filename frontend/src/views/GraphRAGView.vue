<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { graphragApi } from '@/api/graphrag';
import { useToastStore } from '@/store/toasts';

const { t } = useI18n();
const toasts = useToastStore();

const text = ref('');
const frage = ref('');
const ergebnis = ref<{ entitaeten: number; beziehungen: number } | null>(null);
const antwort = ref<string | null>(null);
const verarbeitet = ref(false);

async function extrahieren() {
  if (!text.value.trim()) return;
  verarbeitet.value = true;
  ergebnis.value = null;
  try {
    ergebnis.value = await graphragApi.extrahiere([text.value]);
    toasts.erfolg(
      `${ergebnis.value.entitaeten} Entitäten · ${ergebnis.value.beziehungen} Beziehungen`,
    );
  } finally {
    verarbeitet.value = false;
  }
}

async function abfragen() {
  if (!frage.value.trim()) return;
  antwort.value = null;
  const r = await graphragApi.abfrage(frage.value);
  antwort.value = r.antwort;
}
</script>

<template>
  <section class="space-y-6">
    <header>
      <h1 class="text-2xl font-bold">{{ t('graphrag.titel') }}</h1>
      <p class="text-sm text-slate-500">{{ t('graphrag.einleitung') }}</p>
    </header>

    <article class="karte space-y-3">
      <h2 class="font-semibold">{{ t('graphrag.extrahieren') }}</h2>
      <textarea
        v-model="text"
        rows="8"
        class="eingabe font-mono text-sm"
        :placeholder="t('graphrag.text_platzhalter')"
      />
      <div class="flex items-center gap-3">
        <button class="knopf-primaer" :disabled="verarbeitet" @click="extrahieren">
          {{ verarbeitet ? t('graphrag.verarbeitet') : t('graphrag.extrahieren_knopf') }}
        </button>
        <p v-if="ergebnis" class="text-sm text-slate-600 dark:text-slate-300">
          → {{ ergebnis.entitaeten }} Entitäten, {{ ergebnis.beziehungen }} Beziehungen
        </p>
      </div>
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
