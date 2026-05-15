<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { simulationApi } from '@/api/simulation';
import type { Nachricht } from '@/api/typen';
import { useSimulationStore } from '@/store/simulation';
import { useToastStore } from '@/store/toasts';
import { rendereMarkdown } from '@/werkzeuge/markdown';

const { t } = useI18n();
const store = useSimulationStore();
const toasts = useToastStore();
const aktuellerBericht = ref<string | null>(null);
const aktuellerName = ref<string | null>(null);
const aktuelleId = ref<string | null>(null);
const ladend = ref(false);

const chatVerlauf = ref<Nachricht[]>([]);
const chatEingabe = ref('');
const chatSendet = ref(false);

const html = computed(() => (aktuellerBericht.value ? rendereMarkdown(aktuellerBericht.value) : ''));
const fertige = computed(() =>
  store.simulationen.filter((s) => s.status === 'abgeschlossen'),
);

onMounted(() => store.laden());

async function anzeigen(id: string, name: string) {
  ladend.value = true;
  chatVerlauf.value = [];
  aktuelleId.value = id;
  try {
    const r = await simulationApi.bericht(id);
    aktuellerBericht.value = r.markdown;
    aktuellerName.value = name;
  } catch {
    toasts.fehler('Bericht konnte nicht geladen werden.');
  } finally {
    ladend.value = false;
  }
}

async function senden() {
  if (!aktuelleId.value || !chatEingabe.value.trim()) return;
  const text = chatEingabe.value.trim();
  chatVerlauf.value.push({ rolle: 'nutzer', inhalt: text, zeitstempel: new Date().toISOString() });
  chatEingabe.value = '';
  chatSendet.value = true;
  try {
    const r = await simulationApi.berichtChat(aktuelleId.value, text, chatVerlauf.value.slice(0, -1));
    chatVerlauf.value.push({
      rolle: 'agent',
      inhalt: r.antwort,
      zeitstempel: new Date().toISOString(),
    });
  } catch {
    chatVerlauf.value.pop();
    toasts.fehler('Antwort konnte nicht geladen werden.');
  } finally {
    chatSendet.value = false;
  }
}

function drucken() {
  window.print();
}
</script>

<template>
  <section class="space-y-6">
    <h1 class="text-2xl font-bold">{{ t('berichte.titel') }}</h1>

    <p v-if="!fertige.length" class="text-sm text-slate-500">{{ t('berichte.leer') }}</p>

    <div v-else class="grid gap-6 lg:grid-cols-[20rem,1fr]">
      <ul class="space-y-1">
        <li
          v-for="sim in fertige"
          :key="sim.id"
        >
          <button
            class="w-full rounded border border-slate-200 px-3 py-2 text-left text-sm hover:bg-markenblau-50 dark:border-slate-700 dark:hover:bg-slate-700"
            :class="{ 'bg-markenblau-50 dark:bg-slate-700': aktuellerName === sim.name }"
            @click="anzeigen(sim.id, sim.name)"
          >
            <div class="font-medium">{{ sim.name }}</div>
            <div class="text-xs text-slate-500">
              {{ sim.schritte }} Schritte · {{ sim.agent_ids.length }} Agenten
            </div>
          </button>
        </li>
      </ul>

      <div class="space-y-4">
        <article class="karte prose prose-slate min-h-[24rem] max-w-none dark:prose-invert">
          <div v-if="aktuellerBericht" class="nicht-drucken mb-3 flex justify-end">
            <button class="knopf-sekundaer text-xs" @click="drucken">
              {{ t('berichte.drucken') }}
            </button>
          </div>
          <p v-if="ladend" class="text-sm text-slate-500">…</p>
          <p v-else-if="!aktuellerBericht" class="text-sm text-slate-500">
            {{ t('berichte.anzeigen') }} →
          </p>
          <div v-else v-html="html" />
        </article>

        <article v-if="aktuellerBericht" class="karte nicht-drucken space-y-3">
          <h3 class="text-sm font-semibold uppercase text-slate-500">
            {{ t('berichte.chat_titel') }}
          </h3>
          <div class="max-h-80 space-y-2 overflow-y-auto rounded bg-slate-50 p-3 text-sm dark:bg-slate-900">
            <p v-if="!chatVerlauf.length" class="text-slate-500">
              {{ t('berichte.chat_einleitung') }}
            </p>
            <div
              v-for="(n, i) in chatVerlauf"
              :key="i"
              class="rounded-lg px-3 py-2"
              :class="n.rolle === 'nutzer' ? 'bg-markenblau-600 text-white text-right ml-12' : 'bg-white dark:bg-slate-700 mr-12'"
            >
              {{ n.inhalt }}
            </div>
            <p v-if="chatSendet" class="text-xs text-slate-500">{{ t('chat.denkt') }}</p>
          </div>
          <form class="flex gap-2" @submit.prevent="senden">
            <input
              v-model="chatEingabe"
              :placeholder="t('berichte.chat_platzhalter')"
              class="eingabe flex-1"
              :disabled="chatSendet"
            />
            <button class="knopf-primaer" :disabled="chatSendet">
              {{ t('chat.senden') }}
            </button>
          </form>
        </article>
      </div>
    </div>
  </section>
</template>
