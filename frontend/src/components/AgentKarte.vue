<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { RouterLink } from 'vue-router';

import type { Agent } from '@/api/typen';

defineProps<{ agent: Agent }>();
defineEmits<{ loeschen: [string]; chatten: [string] }>();

const { t } = useI18n();
</script>

<template>
  <article class="karte flex flex-col gap-2">
    <header class="flex items-start justify-between">
      <div>
        <h3 class="text-lg font-semibold">{{ agent.persona.name }}</h3>
        <p v-if="agent.persona.beruf" class="text-sm text-slate-500">{{ agent.persona.beruf }}</p>
      </div>
      <span class="rounded-full bg-markenblau-50 px-2 py-0.5 text-xs text-markenblau-700 dark:bg-slate-700 dark:text-slate-200">
        {{ agent.id.slice(0, 6) }}
      </span>
    </header>

    <p v-if="agent.persona.hintergrund" class="text-sm text-slate-600 dark:text-slate-300">
      {{ agent.persona.hintergrund }}
    </p>

    <ul v-if="agent.persona.werte.length" class="flex flex-wrap gap-1 pt-1">
      <li
        v-for="wert in agent.persona.werte"
        :key="wert"
        class="rounded bg-slate-100 px-2 py-0.5 text-xs dark:bg-slate-700"
      >
        {{ wert }}
      </li>
    </ul>

    <footer class="mt-2 flex flex-wrap gap-2">
      <RouterLink :to="`/agenten/${agent.id}`" class="knopf-sekundaer text-xs">
        Details
      </RouterLink>
      <button class="knopf-primaer text-xs" @click="$emit('chatten', agent.id)">
        {{ t('navigation.chat') }}
      </button>
      <button class="knopf-sekundaer text-xs" @click="$emit('loeschen', agent.id)">
        {{ t('agenten.loeschen') }}
      </button>
    </footer>
  </article>
</template>
