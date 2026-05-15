<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { apiClient } from '@/api/client';

const { t } = useI18n();

interface Eintrag {
  id: number;
  zeitstempel: string;
  aktion: string;
  ressource: string;
  ressource_id: string | null;
  details: Record<string, unknown> | null;
}

const eintraege = ref<Eintrag[]>([]);
const filter = ref<string>('');
const ladend = ref(true);

async function laden() {
  ladend.value = true;
  try {
    const r = await apiClient.get<Eintrag[]>('/api/audit', {
      params: { limit: 200, ...(filter.value ? { ressource: filter.value } : {}) },
    });
    eintraege.value = r.data;
  } finally {
    ladend.value = false;
  }
}

const ressourcen = computed(() => {
  const s = new Set<string>();
  eintraege.value.forEach((e) => s.add(e.ressource));
  return [...s];
});

function farbe(aktion: string): string {
  if (aktion.includes('_geloescht') || aktion.includes('fehlgeschlagen')) {
    return 'bg-red-50 text-red-700 dark:bg-red-900/40 dark:text-red-200';
  }
  if (aktion.includes('_erstellt') || aktion.includes('_geplant')) {
    return 'bg-green-50 text-green-700 dark:bg-green-900/40 dark:text-green-200';
  }
  if (aktion.includes('_aktualisiert')) {
    return 'bg-yellow-50 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-200';
  }
  return 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-200';
}

onMounted(laden);
</script>

<template>
  <section class="space-y-6">
    <header class="flex items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold">{{ t('audit.titel') }}</h1>
        <p class="text-sm text-slate-500">{{ t('audit.einleitung') }}</p>
      </div>
      <div class="flex gap-2">
        <select v-model="filter" class="eingabe text-xs" @change="laden">
          <option value="">{{ t('audit.alle') }}</option>
          <option v-for="r in ressourcen" :key="r" :value="r">{{ r }}</option>
        </select>
        <button class="knopf-sekundaer text-xs" @click="laden">↻</button>
      </div>
    </header>

    <p v-if="ladend" class="text-sm text-slate-500">…</p>
    <p v-else-if="!eintraege.length" class="text-sm text-slate-500">
      {{ t('audit.leer') }}
    </p>

    <div v-else class="karte overflow-hidden p-0">
      <table class="w-full table-fixed border-collapse text-sm">
        <thead class="bg-slate-50 text-left text-xs uppercase text-slate-500 dark:bg-slate-700">
          <tr>
            <th class="w-44 p-2">{{ t('audit.zeit') }}</th>
            <th class="w-40 p-2">{{ t('audit.aktion') }}</th>
            <th class="w-32 p-2">{{ t('audit.ressource') }}</th>
            <th class="p-2">{{ t('audit.details') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="e in eintraege"
            :key="e.id"
            class="border-t border-slate-100 dark:border-slate-700/60"
          >
            <td class="p-2 font-mono text-xs text-slate-500">
              {{ new Date(e.zeitstempel).toLocaleString('de-DE') }}
            </td>
            <td class="p-2">
              <span class="rounded px-2 py-0.5 text-xs" :class="farbe(e.aktion)">
                {{ e.aktion }}
              </span>
            </td>
            <td class="p-2">
              <p>{{ e.ressource }}</p>
              <p v-if="e.ressource_id" class="font-mono text-[10px] text-slate-400">
                {{ e.ressource_id.slice(0, 8) }}…
              </p>
            </td>
            <td class="p-2 font-mono text-xs">
              {{ e.details ? JSON.stringify(e.details) : '—' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
