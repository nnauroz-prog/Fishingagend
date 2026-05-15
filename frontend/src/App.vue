<script setup lang="ts">
import { onMounted } from 'vue';

import Navigationsleiste from '@/components/Navigationsleiste.vue';
import ToastSchicht from '@/components/ToastSchicht.vue';

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
      <RouterView v-slot="{ Component, route }">
        <Transition name="seite" mode="out-in">
          <component :is="Component" :key="route.fullPath" />
        </Transition>
      </RouterView>
    </main>
    <footer class="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500 dark:border-slate-700 dark:bg-slate-800">
      Fishingagend · {{ new Date().getFullYear() }} · AGPL-3.0
    </footer>
    <ToastSchicht />
  </div>
</template>

<style>
.seite-enter-active,
.seite-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.seite-enter-from,
.seite-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
</style>
