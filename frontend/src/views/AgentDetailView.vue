<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';

import { agentenApi } from '@/api/agenten';
import type { Agent } from '@/api/typen';
import { useAgentenStore } from '@/store/agenten';
import { useToastStore } from '@/store/toasts';

const route = useRoute();
const router = useRouter();
const { t } = useI18n();
const store = useAgentenStore();
const toasts = useToastStore();

const agent = ref<Agent | null>(null);
const ladend = ref(false);

const id = computed(() => route.params.id as string);

onMounted(async () => {
  ladend.value = true;
  try {
    agent.value = await agentenApi.hole(id.value);
  } catch {
    toasts.fehler('Agent nicht gefunden.');
    router.replace({ name: 'agenten' });
  } finally {
    ladend.value = false;
  }
});

async function loeschen() {
  if (!agent.value) return;
  if (!confirm(`"${agent.value.persona.name}" wirklich löschen?`)) return;
  await store.loeschen(agent.value.id);
  toasts.erfolg('Agent gelöscht.');
  router.push({ name: 'agenten' });
}
</script>

<template>
  <section v-if="ladend" class="text-sm text-slate-500">…</section>
  <section v-else-if="agent" class="space-y-6">
    <header class="flex items-start justify-between">
      <div>
        <RouterLink to="/agenten" class="text-xs text-markenblau-600 hover:underline">
          ← {{ t('navigation.agenten') }}
        </RouterLink>
        <h1 class="text-3xl font-bold">{{ agent.persona.name }}</h1>
        <p v-if="agent.persona.beruf" class="text-slate-500">{{ agent.persona.beruf }}</p>
      </div>
      <div class="flex gap-2">
        <RouterLink :to="`/chat/${agent.id}`" class="knopf-primaer">
          {{ t('navigation.chat') }}
        </RouterLink>
        <button class="knopf-sekundaer" @click="loeschen">{{ t('agenten.loeschen') }}</button>
      </div>
    </header>

    <div class="grid gap-4 md:grid-cols-2">
      <article class="karte">
        <h2 class="mb-2 text-sm font-semibold uppercase text-slate-500">
          {{ t('agenten.hintergrund') }}
        </h2>
        <p class="whitespace-pre-wrap text-sm">{{ agent.persona.hintergrund || '—' }}</p>
      </article>

      <article class="karte">
        <h2 class="mb-2 text-sm font-semibold uppercase text-slate-500">{{ t('agenten.werte') }}</h2>
        <ul v-if="agent.persona.werte.length" class="flex flex-wrap gap-1">
          <li
            v-for="w in agent.persona.werte"
            :key="w"
            class="rounded bg-markenblau-50 px-2 py-0.5 text-xs text-markenblau-700 dark:bg-slate-700 dark:text-slate-200"
          >
            {{ w }}
          </li>
        </ul>
        <p v-else class="text-sm text-slate-500">—</p>
      </article>

      <article class="karte">
        <h2 class="mb-2 text-sm font-semibold uppercase text-slate-500">Charakterzüge</h2>
        <ul v-if="agent.persona.charakterzuege.length" class="flex flex-wrap gap-1">
          <li
            v-for="c in agent.persona.charakterzuege"
            :key="c"
            class="rounded bg-slate-100 px-2 py-0.5 text-xs dark:bg-slate-700"
          >
            {{ c }}
          </li>
        </ul>
        <p v-else class="text-sm text-slate-500">—</p>
      </article>

      <article class="karte">
        <h2 class="mb-2 text-sm font-semibold uppercase text-slate-500">Metadaten</h2>
        <dl class="grid grid-cols-2 gap-2 text-sm">
          <dt class="text-slate-500">ID</dt>
          <dd class="font-mono text-xs">{{ agent.id }}</dd>
          <dt class="text-slate-500">Sprachstil</dt>
          <dd>{{ agent.persona.sprachstil }}</dd>
          <dt v-if="agent.persona.alter" class="text-slate-500">Alter</dt>
          <dd v-if="agent.persona.alter">{{ agent.persona.alter }}</dd>
          <dt class="text-slate-500">Erstellt</dt>
          <dd>{{ new Date(agent.erstellt_am).toLocaleString('de-DE') }}</dd>
        </dl>
      </article>
    </div>
  </section>
</template>
