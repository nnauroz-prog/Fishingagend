<script setup lang="ts">
import type { Nachricht } from '@/api/typen';

defineProps<{ nachricht: Nachricht }>();
</script>

<template>
  <div
    class="flex"
    :class="nachricht.rolle === 'nutzer' ? 'justify-end' : 'justify-start'"
  >
    <div
      class="max-w-[75%] rounded-lg px-4 py-2 text-sm shadow-sm"
      :class="
        nachricht.rolle === 'nutzer'
          ? 'bg-markenblau-600 text-white'
          : 'bg-white text-slate-900 dark:bg-slate-700 dark:text-slate-100'
      "
    >
      <p class="whitespace-pre-wrap">{{ nachricht.inhalt }}</p>
    </div>
  </div>
</template>
