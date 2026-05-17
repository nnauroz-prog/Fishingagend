<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import { vorlagenApi, type Vorlage } from '@/api/vorlagen';
import { useToastStore } from '@/store/toasts';

const { t } = useI18n();
const router = useRouter();
const toasts = useToastStore();

const vorlagen = ref<Vorlage[]>([]);
const ladend = ref(true);
const startet = ref<string | null>(null);

onMounted(async () => {
  try {
    vorlagen.value = await vorlagenApi.liste();
  } finally {
    ladend.value = false;
  }
});

const kategorien = computed(() => {
  const map = new Map<string, Vorlage[]>();
  vorlagen.value.forEach((v) => {
    if (!map.has(v.kategorie)) map.set(v.kategorie, []);
    map.get(v.kategorie)!.push(v);
  });
  return [...map.entries()];
});

const farbe: Record<string, string> = {
  Politik: 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-200',
  Gesundheit: 'bg-pink-50 text-pink-700 dark:bg-pink-900/30 dark:text-pink-200',
  Medien: 'bg-violet-50 text-violet-700 dark:bg-violet-900/30 dark:text-violet-200',
  Wirtschaft: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-200',
  Bildung: 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-200',
};

async function anwenden(v: Vorlage, sofort: boolean) {
  startet.value = v.schluessel;
  try {
    const sim = await vorlagenApi.anwenden(v.schluessel, undefined, sofort);
    toasts.erfolg(`"${sim.name}" angelegt.`);
    router.push({ name: 'simulation-detail', params: { id: sim.id } });
  } finally {
    startet.value = null;
  }
}
</script>

<template>
  <section class="space-y-6">
    <header>
      <h1 class="text-2xl font-bold">{{ t('vorlagen.titel') }}</h1>
      <p class="text-sm text-slate-500">{{ t('vorlagen.einleitung') }}</p>
    </header>

    <p v-if="ladend" class="text-sm text-slate-500">…</p>

    <div v-else class="space-y-8">
      <section v-for="[kat, liste] in kategorien" :key="kat" class="space-y-3">
        <h2 class="text-xs font-semibold uppercase text-slate-500">{{ kat }}</h2>
        <div class="grid gap-4 md:grid-cols-2">
          <article
            v-for="v in liste"
            :key="v.schluessel"
            class="karte flex flex-col gap-3"
          >
            <header class="flex items-start justify-between gap-3">
              <h3 class="text-lg font-semibold">{{ v.titel }}</h3>
              <span class="rounded-full px-2 py-0.5 text-xs" :class="farbe[v.kategorie] ?? 'bg-slate-100 dark:bg-slate-700'">
                {{ v.kategorie }}
              </span>
            </header>
            <p class="text-sm text-slate-600 dark:text-slate-300">{{ v.beschreibung }}</p>
            <dl class="grid grid-cols-2 gap-x-3 gap-y-1 text-xs text-slate-500">
              <div>👥 {{ v.anzahl_personas }} Personas</div>
              <div>⏱ {{ v.schritte }} Schritte</div>
              <div v-if="v.dual_modus">🌓 Dual-Welt</div>
              <div v-if="v.plattform_modus">📣 Plattform</div>
            </dl>
            <footer class="mt-auto flex gap-2">
              <button
                class="knopf-primaer flex-1 text-xs"
                :disabled="startet === v.schluessel"
                @click="anwenden(v, true)"
              >
                {{ startet === v.schluessel ? '…' : t('vorlagen.start_sofort') }}
              </button>
              <button
                class="knopf-sekundaer text-xs"
                :disabled="startet === v.schluessel"
                @click="anwenden(v, false)"
              >
                {{ t('vorlagen.nur_anlegen') }}
              </button>
            </footer>
          </article>
        </div>
      </section>
    </div>
  </section>
</template>
