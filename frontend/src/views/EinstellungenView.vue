<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { einstellungenApi, type Einstellungen } from '@/api/einstellungen';

const { t } = useI18n();
const e = ref<Einstellungen | null>(null);
const ladend = ref(true);

onMounted(async () => {
  try {
    e.value = await einstellungenApi.hole();
  } finally {
    ladend.value = false;
  }
});

function badge(an: boolean): string {
  return an
    ? 'rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700 dark:bg-green-900/40 dark:text-green-200'
    : 'rounded-full bg-yellow-100 px-2 py-0.5 text-xs text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-200';
}
</script>

<template>
  <section class="space-y-6">
    <header>
      <h1 class="text-2xl font-bold">{{ t('einstellungen.titel') }}</h1>
      <p class="text-sm text-slate-500">{{ t('einstellungen.einleitung') }}</p>
    </header>

    <p v-if="ladend" class="text-sm text-slate-500">…</p>

    <div v-else-if="e" class="space-y-4">
      <article class="karte space-y-3">
        <h2 class="font-semibold">LLM-Provider</h2>
        <dl class="grid grid-cols-1 gap-x-6 gap-y-2 text-sm sm:grid-cols-2">
          <dt class="text-slate-500">Aktiver Provider</dt>
          <dd>
            <span class="rounded bg-markenblau-50 px-2 py-0.5 font-mono text-xs text-markenblau-700 dark:bg-slate-700 dark:text-markenblau-300">
              {{ e.llm.provider }}
            </span>
          </dd>

          <dt class="text-slate-500">Anthropic-Modell</dt>
          <dd class="font-mono">{{ e.llm.anthropic_modell }}</dd>

          <dt class="text-slate-500">Anthropic-API-Key</dt>
          <dd>
            <span :class="badge(e.llm.anthropic_api_key_gesetzt)">
              {{ e.llm.anthropic_api_key_gesetzt ? t('einstellungen.gesetzt') : t('einstellungen.fehlt') }}
            </span>
          </dd>

          <dt class="text-slate-500">OpenAI-Modell</dt>
          <dd class="font-mono">{{ e.llm.openai_modell }}</dd>

          <dt class="text-slate-500">OpenAI-Basis-URL</dt>
          <dd class="font-mono text-xs">{{ e.llm.openai_basis_url || '(default)' }}</dd>

          <dt class="text-slate-500">OpenAI-API-Key</dt>
          <dd>
            <span :class="badge(e.llm.openai_api_key_gesetzt)">
              {{ e.llm.openai_api_key_gesetzt ? t('einstellungen.gesetzt') : t('einstellungen.fehlt') }}
            </span>
          </dd>
        </dl>
        <p class="text-xs text-slate-500">{{ t('einstellungen.hinweis_env') }}</p>
      </article>

      <article class="karte">
        <h2 class="mb-2 font-semibold">Simulation</h2>
        <dl class="grid grid-cols-1 gap-x-6 gap-y-2 text-sm sm:grid-cols-2">
          <dt class="text-slate-500">Max. Agenten pro Sim</dt>
          <dd>{{ e.simulation.max_agenten }}</dd>
          <dt class="text-slate-500">Standard-Schritte</dt>
          <dd>{{ e.simulation.simulations_schritte }}</dd>
          <dt class="text-slate-500">Demo-Daten beim Start</dt>
          <dd>{{ e.simulation.demo_daten_einspielen ? 'aktiv' : 'aus' }}</dd>
        </dl>
      </article>

      <article class="karte">
        <h2 class="mb-2 font-semibold">Persistenz</h2>
        <p class="text-sm">Datenbank-Dialekt: <code class="font-mono">{{ e.datenbank_dialekt }}</code></p>
      </article>
    </div>
  </section>
</template>
