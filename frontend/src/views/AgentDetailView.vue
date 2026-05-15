<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';

import { agentenApi } from '@/api/agenten';
import type { Agent } from '@/api/typen';
import { useAgentenStore } from '@/store/agenten';
import { useToastStore } from '@/store/toasts';

const route = useRoute();
const router = useRouter();
const { t } = useI18n();
const store = useAgentenStore();
const toasts = useToastStore();

const agent = ref<Agent | null>(null);
const ladend = ref(false);
const bearbeiten = ref(false);
const reflexionen = ref<string[]>([]);
const praeferenzen = ref<{
  personen: { name: string; anzahl: number }[];
  begriffe: { wort: string; anzahl: number }[];
  episoden: number;
} | null>(null);
const formular = reactive({
  name: '',
  beruf: '',
  hintergrund: '',
  werte: '',
  charakterzuege: '',
  sprachstil: 'neutral',
});

const id = computed(() => route.params.id as string);

onMounted(async () => {
  ladend.value = true;
  try {
    agent.value = await agentenApi.hole(id.value);
    [reflexionen.value, praeferenzen.value] = await Promise.all([
      agentenApi.reflexionen(id.value),
      agentenApi.praeferenzen(id.value),
    ]);
  } catch {
    toasts.fehler('Agent nicht gefunden.');
    router.replace({ name: 'agenten' });
  } finally {
    ladend.value = false;
  }
});

const beziehungenListe = computed(() =>
  agent.value
    ? Object.entries(agent.value.persona.beziehungen).map(([name, text]) => ({ name, text }))
    : [],
);

function tagGroesse(anzahl: number, max: number): string {
  // Tag-Cloud-Skalierung 0.75 - 1.5em
  const f = Math.min(1, anzahl / Math.max(max, 1));
  return `${(0.75 + f * 0.75).toFixed(2)}em`;
}

function bearbeitenStarten() {
  if (!agent.value) return;
  formular.name = agent.value.persona.name;
  formular.beruf = agent.value.persona.beruf ?? '';
  formular.hintergrund = agent.value.persona.hintergrund;
  formular.werte = agent.value.persona.werte.join(', ');
  formular.charakterzuege = agent.value.persona.charakterzuege.join(', ');
  formular.sprachstil = agent.value.persona.sprachstil;
  bearbeiten.value = true;
}

async function speichern() {
  if (!agent.value) return;
  const persona = {
    ...agent.value.persona,
    name: formular.name.trim(),
    beruf: formular.beruf.trim() || null,
    hintergrund: formular.hintergrund.trim(),
    werte: formular.werte.split(',').map((w) => w.trim()).filter(Boolean),
    charakterzuege: formular.charakterzuege.split(',').map((w) => w.trim()).filter(Boolean),
    sprachstil: formular.sprachstil,
  };
  agent.value = await agentenApi.aktualisiere(agent.value.id, persona);
  bearbeiten.value = false;
  toasts.erfolg('Agent gespeichert.');
}

async function loeschen() {
  if (!agent.value) return;
  if (!confirm(`"${agent.value.persona.name}" wirklich löschen?`)) return;
  await store.loeschen(agent.value.id);
  toasts.erfolg('Agent gelöscht.');
  router.push({ name: 'agenten' });
}
</script>

<template>
  <section v-if="ladend" class="text-sm text-slate-500">…</section>
  <section v-else-if="agent" class="space-y-6">
    <header class="flex items-start justify-between">
      <div>
        <RouterLink to="/agenten" class="text-xs text-markenblau-600 hover:underline">
          ← {{ t('navigation.agenten') }}
        </RouterLink>
        <h1 class="text-3xl font-bold">{{ agent.persona.name }}</h1>
        <p v-if="agent.persona.beruf" class="text-slate-500">{{ agent.persona.beruf }}</p>
      </div>
      <div class="flex gap-2">
        <RouterLink :to="`/chat/${agent.id}`" class="knopf-primaer">
          {{ t('navigation.chat') }}
        </RouterLink>
        <button class="knopf-sekundaer" @click="bearbeitenStarten">
          {{ t('agenten.bearbeiten') }}
        </button>
        <button class="knopf-sekundaer" @click="loeschen">{{ t('agenten.loeschen') }}</button>
      </div>
    </header>

    <form v-if="bearbeiten" class="karte space-y-3" @submit.prevent="speichern">
      <div>
        <label class="etikett">{{ t('agenten.name') }}</label>
        <input v-model="formular.name" class="eingabe" required />
      </div>
      <div>
        <label class="etikett">{{ t('agenten.beruf') }}</label>
        <input v-model="formular.beruf" class="eingabe" />
      </div>
      <div>
        <label class="etikett">{{ t('agenten.hintergrund') }}</label>
        <textarea v-model="formular.hintergrund" rows="3" class="eingabe" />
      </div>
      <div class="grid gap-3 sm:grid-cols-2">
        <div>
          <label class="etikett">{{ t('agenten.werte') }}</label>
          <input v-model="formular.werte" class="eingabe" />
        </div>
        <div>
          <label class="etikett">Charakterzüge</label>
          <input v-model="formular.charakterzuege" class="eingabe" />
        </div>
      </div>
      <div>
        <label class="etikett">Sprachstil</label>
        <input v-model="formular.sprachstil" class="eingabe" />
      </div>
      <div class="flex gap-2">
        <button type="submit" class="knopf-primaer">{{ t('agenten.speichern') }}</button>
        <button type="button" class="knopf-sekundaer" @click="bearbeiten = false">
          {{ t('agenten.abbrechen') }}
        </button>
      </div>
    </form>

    <div class="grid gap-4 md:grid-cols-2">
      <article class="karte">
        <h2 class="mb-2 text-sm font-semibold uppercase text-slate-500">
          {{ t('agenten.hintergrund') }}
        </h2>
        <p class="whitespace-pre-wrap text-sm">{{ agent.persona.hintergrund || '—' }}</p>
      </article>

      <article class="karte">
        <h2 class="mb-2 text-sm font-semibold uppercase text-slate-500">{{ t('agenten.werte') }}</h2>
        <ul v-if="agent.persona.werte.length" class="flex flex-wrap gap-1">
          <li
            v-for="w in agent.persona.werte"
            :key="w"
            class="rounded bg-markenblau-50 px-2 py-0.5 text-xs text-markenblau-700 dark:bg-slate-700 dark:text-slate-200"
          >
            {{ w }}
          </li>
        </ul>
        <p v-else class="text-sm text-slate-500">—</p>
      </article>

      <article class="karte">
        <h2 class="mb-2 text-sm font-semibold uppercase text-slate-500">Charakterzüge</h2>
        <ul v-if="agent.persona.charakterzuege.length" class="flex flex-wrap gap-1">
          <li
            v-for="c in agent.persona.charakterzuege"
            :key="c"
            class="rounded bg-slate-100 px-2 py-0.5 text-xs dark:bg-slate-700"
          >
            {{ c }}
          </li>
        </ul>
        <p v-else class="text-sm text-slate-500">—</p>
      </article>

      <article v-if="beziehungenListe.length" class="karte">
        <h2 class="mb-2 text-sm font-semibold uppercase text-slate-500">
          {{ t('agent_detail.beziehungen') }}
        </h2>
        <ul class="space-y-1.5 text-sm">
          <li
            v-for="b in beziehungenListe"
            :key="b.name"
            class="flex items-baseline gap-2"
          >
            <strong class="shrink-0">{{ b.name }}:</strong>
            <span class="text-slate-600 dark:text-slate-300">{{ b.text }}</span>
          </li>
        </ul>
      </article>

      <article v-if="reflexionen.length" class="karte">
        <h2 class="mb-2 text-sm font-semibold uppercase text-slate-500">
          {{ t('agent_detail.reflexionen') }}
        </h2>
        <ul class="space-y-2 text-sm">
          <li
            v-for="(r, i) in reflexionen.slice(0, 5)"
            :key="i"
            class="rounded border-l-2 border-markenblau-400 bg-slate-50 px-3 py-2 dark:bg-slate-700"
          >
            {{ r.replace(/^\[Reflexion zu Sim [^\]]+\]\s*/, '') }}
          </li>
        </ul>
      </article>

      <article v-if="praeferenzen && praeferenzen.episoden > 0" class="karte md:col-span-2">
        <h2 class="mb-2 text-sm font-semibold uppercase text-slate-500">
          {{ t('agent_detail.praeferenzen') }}
          <span class="ml-2 text-xs font-normal normal-case text-slate-400">
            ({{ praeferenzen.episoden }} {{ t('agent_detail.episoden') }})
          </span>
        </h2>
        <div class="grid gap-4 sm:grid-cols-2">
          <div v-if="praeferenzen.personen.length">
            <h3 class="mb-1 text-xs uppercase text-slate-400">{{ t('agent_detail.personen') }}</h3>
            <div class="flex flex-wrap items-baseline gap-x-2 gap-y-1">
              <span
                v-for="p in praeferenzen.personen"
                :key="p.name"
                class="rounded bg-markenblau-50 px-2 py-0.5 text-markenblau-700 dark:bg-slate-700 dark:text-markenblau-300"
                :style="{ fontSize: tagGroesse(p.anzahl, praeferenzen.personen[0]?.anzahl ?? 1) }"
              >
                {{ p.name }} <sup class="text-[0.7em] opacity-60">{{ p.anzahl }}</sup>
              </span>
            </div>
          </div>
          <div v-if="praeferenzen.begriffe.length">
            <h3 class="mb-1 text-xs uppercase text-slate-400">{{ t('agent_detail.begriffe') }}</h3>
            <div class="flex flex-wrap items-baseline gap-x-2 gap-y-1">
              <span
                v-for="b in praeferenzen.begriffe"
                :key="b.wort"
                class="rounded bg-slate-100 px-2 py-0.5 dark:bg-slate-700"
                :style="{ fontSize: tagGroesse(b.anzahl, praeferenzen.begriffe[0]?.anzahl ?? 1) }"
              >
                {{ b.wort }}
              </span>
            </div>
          </div>
        </div>
      </article>

      <article class="karte">
        <h2 class="mb-2 text-sm font-semibold uppercase text-slate-500">Metadaten</h2>
        <dl class="grid grid-cols-2 gap-2 text-sm">
          <dt class="text-slate-500">ID</dt>
          <dd class="font-mono text-xs">{{ agent.id }}</dd>
          <dt class="text-slate-500">Sprachstil</dt>
          <dd>{{ agent.persona.sprachstil }}</dd>
          <dt v-if="agent.persona.alter" class="text-slate-500">Alter</dt>
          <dd v-if="agent.persona.alter">{{ agent.persona.alter }}</dd>
          <dt class="text-slate-500">Erstellt</dt>
          <dd>{{ new Date(agent.erstellt_am).toLocaleString('de-DE') }}</dd>
        </dl>
      </article>
    </div>
  </section>
</template>
