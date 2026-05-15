<script setup lang="ts">
import { onMounted } from 'vue';

import Navigationsleiste from '@/components/Navigationsleiste.vue';

onMounted(() => {
  const gespeichert = localStorage.getItem('fishingagend-thema');
  const dunkel =
    gespeichert === 'dunkel' ||
    (gespeichert === null && window.matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.classList.toggle('dark', dunkel);
});
</script>

<template>
  <div class="flex h-full flex-col">
    <Navigationsleiste />
    <main class="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 lg:px-8">
      <RouterView />
    </main>
    <footer class="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500 dark:border-slate-700 dark:bg-slate-800">
      Fishingagend · {{ new Date().getFullYear() }} · AGPL-3.0
    </footer>
  </div>
</template>
