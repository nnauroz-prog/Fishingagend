<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink } from 'vue-router';

const { t, locale, availableLocales } = useI18n();

const dunkel = ref(document.documentElement.classList.contains('dark'));

function themaWechseln() {
  dunkel.value = !dunkel.value;
  document.documentElement.classList.toggle('dark', dunkel.value);
  localStorage.setItem('fishingagend-thema', dunkel.value ? 'dunkel' : 'hell');
}

function spracheWechseln() {
  const naechste = locale.value === 'de' ? 'en' : 'de';
  locale.value = naechste;
  localStorage.setItem('fishingagend-sprache', naechste);
}

const links = [
  { ziel: '/', schluessel: 'navigation.startseite' },
  { ziel: '/agenten', schluessel: 'navigation.agenten' },
  { ziel: '/chat', schluessel: 'navigation.chat' },
  { ziel: '/simulation', schluessel: 'navigation.simulation' },
  { ziel: '/graphrag', schluessel: 'navigation.graphrag' },
  { ziel: '/berichte', schluessel: 'navigation.berichte' },
];
</script>

<template>
  <header class="border-b border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
      <RouterLink to="/" class="flex items-center gap-2">
        <img src="/favicon.svg" alt="" class="h-7 w-7" />
        <span class="text-lg font-semibold">{{ t('app.name') }}</span>
      </RouterLink>

      <nav class="hidden items-center gap-1 md:flex">
        <RouterLink
          v-for="l in links"
          :key="l.ziel"
          :to="l.ziel"
          class="rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-700 dark:hover:text-white"
          active-class="bg-markenblau-50 text-markenblau-700 dark:bg-slate-700 dark:text-white"
        >
          {{ t(l.schluessel) }}
        </RouterLink>
      </nav>

      <div class="flex items-center gap-2">
        <button class="knopf-sekundaer text-xs" @click="spracheWechseln">
          {{ availableLocales.find((s) => s !== locale)?.toUpperCase() }}
        </button>
        <button
          class="knopf-sekundaer text-xs"
          :title="t('navigation.thema_wechseln')"
          @click="themaWechseln"
        >
          {{ dunkel ? '☀' : '☾' }}
        </button>
      </div>
    </div>
  </header>
</template>
