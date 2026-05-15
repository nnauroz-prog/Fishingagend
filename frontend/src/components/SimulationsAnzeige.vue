<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import type { Simulation } from '@/api/typen';

const props = defineProps<{ simulation: Simulation }>();
const { t } = useI18n();

const statusKey = computed(() => `simulation.status_${props.simulation.status}`);
</script>

<template>
  <article class="karte">
    <header class="mb-3 flex items-start justify-between">
      <div>
        <h3 class="text-lg font-semibold">{{ simulation.name }}</h3>
        <p v-if="simulation.beschreibung" class="text-sm text-slate-500">
          {{ simulation.beschreibung }}
        </p>
      </div>
      <span
        class="rounded-full px-2 py-0.5 text-xs"
        :class="{
          'bg-slate-200 text-slate-700': simulation.status === 'geplant',
          'bg-yellow-100 text-yellow-700': simulation.status === 'laeuft',
          'bg-green-100 text-green-700': simulation.status === 'abgeschlossen',
          'bg-red-100 text-red-700': simulation.status === 'fehlgeschlagen',
        }"
      >
        {{ t(statusKey) }}
      </span>
    </header>

    <dl class="grid grid-cols-2 gap-2 text-sm sm:grid-cols-4">
      <div>
        <dt class="text-slate-500">{{ t('simulation.schritte') }}</dt>
        <dd class="font-medium">{{ simulation.schritte }}</dd>
      </div>
      <div>
        <dt class="text-slate-500">{{ t('simulation.agenten') }}</dt>
        <dd class="font-medium">{{ simulation.agent_ids.length }}</dd>
      </div>
      <div>
        <dt class="text-slate-500">Dual-Modus</dt>
        <dd class="font-medium">{{ simulation.dual_modus ? 'ja' : 'nein' }}</dd>
      </div>
      <div>
        <dt class="text-slate-500">Verlauf</dt>
        <dd class="font-medium">{{ simulation.verlauf.length }}</dd>
      </div>
    </dl>
  </article>
</template>
