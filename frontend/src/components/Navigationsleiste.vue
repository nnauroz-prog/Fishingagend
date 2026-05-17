<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterLink, useRouter } from 'vue-router';

import Avatar from '@/components/Avatar.vue';
import { useAuthStore } from '@/store/auth';

const { t, locale, availableLocales } = useI18n();
const auth = useAuthStore();
const router = useRouter();

const dunkel = ref(document.documentElement.classList.contains('dark'));
const mobilOffen = ref(false);

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

function abmelden() {
  auth.abmelden();
  mobilOffen.value = false;
  router.push('/anmelden');
}

// Auf dem Handy gruppieren wir, damit die Navigationsleiste mit 11 Links
// nicht ueberlaeuft. Auf Desktop zeigen wir alles flach.
const haupt = [
  { ziel: '/', schluessel: 'navigation.startseite' },
  { ziel: '/pipeline', schluessel: 'navigation.pipeline' },
  { ziel: '/vorlagen', schluessel: 'navigation.vorlagen' },
  { ziel: '/agenten', schluessel: 'navigation.agenten' },
  { ziel: '/chat', schluessel: 'navigation.chat' },
  { ziel: '/simulation', schluessel: 'navigation.simulation' },
];

const weitere = [
  { ziel: '/beziehungen', schluessel: 'navigation.beziehungen' },
  { ziel: '/graphrag', schluessel: 'navigation.graphrag' },
  { ziel: '/berichte', schluessel: 'navigation.berichte' },
  { ziel: '/einstellungen', schluessel: 'navigation.einstellungen' },
  { ziel: '/audit', schluessel: 'navigation.audit' },
];

const alle = [...haupt, ...weitere];
</script>

<template>
  <header class="border-b border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
      <RouterLink to="/" class="flex items-center gap-2" @click="mobilOffen = false">
        <img src="/favicon.svg" alt="" class="h-7 w-7" />
        <span class="text-lg font-semibold">{{ t('app.name') }}</span>
      </RouterLink>

      <!-- Desktop-Navigation -->
      <nav class="hidden items-center gap-1 lg:flex">
        <RouterLink
          v-for="l in alle"
          :key="l.ziel"
          :to="l.ziel"
          class="rounded-md px-2.5 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-700 dark:hover:text-white"
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

        <template v-if="auth.angemeldet && auth.nutzer">
          <div class="hidden items-center gap-2 pl-2 sm:flex">
            <Avatar :name="auth.nutzer.anzeige_name" groesse="klein" />
            <button
              class="text-xs text-slate-500 hover:text-red-600"
              :title="t('auth.abmelden')"
              @click="abmelden"
            >
              ↪
            </button>
          </div>
        </template>
        <RouterLink
          v-else
          to="/anmelden"
          class="hidden text-xs sm:inline-flex knopf-primaer"
        >
          {{ t('auth.anmelden') }}
        </RouterLink>

        <!-- Hamburger fuer Mobile -->
        <button
          class="knopf-sekundaer text-base lg:hidden"
          aria-label="Menü"
          @click="mobilOffen = !mobilOffen"
        >
          {{ mobilOffen ? '✕' : '☰' }}
        </button>
      </div>
    </div>

    <!-- Mobile-Aufklapper -->
    <Transition name="mobil">
      <nav
        v-if="mobilOffen"
        class="border-t border-slate-200 bg-white px-4 py-2 lg:hidden dark:border-slate-700 dark:bg-slate-800"
      >
        <RouterLink
          v-for="l in alle"
          :key="l.ziel"
          :to="l.ziel"
          class="block rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-700"
          active-class="bg-markenblau-50 text-markenblau-700 dark:bg-slate-700 dark:text-white"
          @click="mobilOffen = false"
        >
          {{ t(l.schluessel) }}
        </RouterLink>

        <div class="mt-2 border-t border-slate-200 pt-2 dark:border-slate-700">
          <template v-if="auth.angemeldet && auth.nutzer">
            <div class="flex items-center gap-2 px-3 py-2">
              <Avatar :name="auth.nutzer.anzeige_name" groesse="klein" />
              <span class="text-sm">{{ auth.nutzer.anzeige_name }}</span>
              <button class="ml-auto text-xs text-red-600" @click="abmelden">
                {{ t('auth.abmelden') }}
              </button>
            </div>
          </template>
          <RouterLink
            v-else
            to="/anmelden"
            class="block rounded-md px-3 py-2 text-sm font-medium text-markenblau-700"
            @click="mobilOffen = false"
          >
            → {{ t('auth.anmelden') }}
          </RouterLink>
        </div>
      </nav>
    </Transition>
  </header>
</template>

<style scoped>
.mobil-enter-active,
.mobil-leave-active {
  transition: opacity 0.15s ease, max-height 0.2s ease;
  overflow: hidden;
}
.mobil-enter-from,
.mobil-leave-to {
  opacity: 0;
  max-height: 0;
}
.mobil-enter-to,
.mobil-leave-from {
  opacity: 1;
  max-height: 600px;
}
</style>
