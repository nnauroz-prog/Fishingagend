<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import { agentenApi } from '@/api/agenten';
import AgentKarte from '@/components/AgentKarte.vue';
import Suchfeld from '@/components/Suchfeld.vue';
import { useAgentenStore } from '@/store/agenten';

const { t } = useI18n();
const router = useRouter();
const store = useAgentenStore();

const formularSichtbar = ref(false);
const vorschlaegt = ref(false);
const suche = ref('');

const gefiltert = computed(() => {
  const q = suche.value.trim().toLowerCase();
  if (!q) return store.agenten;
  return store.agenten.filter((a) => {
    const blob = [
      a.persona.name,
      a.persona.beruf,
      a.persona.hintergrund,
      a.persona.werte.join(' '),
      a.persona.charakterzuege.join(' '),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return blob.includes(q);
  });
});
const formular = reactive({
  saat: '',
  name: '',
  beruf: '',
  hintergrund: '',
  werte: '',
  charakterzuege: [] as string[],
  sprachstil: 'neutral',
});

onMounted(() => store.laden());

async function vorschlagen() {
  if (!formular.saat.trim()) return;
  vorschlaegt.value = true;
  try {
    const persona = await agentenApi.personaAusSaat({ stichworte: formular.saat });
    formular.name = persona.name;
    formular.beruf = persona.beruf ?? '';
    formular.hintergrund = persona.hintergrund;
    formular.werte = persona.werte.join(', ');
    formular.charakterzuege = persona.charakterzuege;
    formular.sprachstil = persona.sprachstil;
  } finally {
    vorschlaegt.value = false;
  }
}

async function speichern() {
  if (!formular.name.trim()) return;
  await store.erstellen({
    persona: {
      name: formular.name.trim(),
      beruf: formular.beruf.trim() || null,
      hintergrund: formular.hintergrund.trim(),
      werte: formular.werte
        .split(',')
        .map((w) => w.trim())
        .filter(Boolean),
      charakterzuege: formular.charakterzuege,
      beziehungen: {},
      sprachstil: formular.sprachstil,
    },
  });
  formularSichtbar.value = false;
  Object.assign(formular, {
    saat: '',
    name: '',
    beruf: '',
    hintergrund: '',
    werte: '',
    charakterzuege: [],
    sprachstil: 'neutral',
  });
}

function zumChat(agentId: string) {
  router.push({ name: 'chat', params: { agentId } });
}
</script>

<template>
  <section class="space-y-6">
    <header class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">{{ t('agenten.titel') }}</h1>
      <button class="knopf-primaer" @click="formularSichtbar = !formularSichtbar">
        + {{ t('agenten.neuer_agent') }}
      </button>
    </header>

    <form v-if="formularSichtbar" class="karte space-y-3" @submit.prevent="speichern">
      <div>
        <label class="etikett" for="saat">{{ t('agenten.saat') }}</label>
        <div class="flex gap-2">
          <input id="saat" v-model="formular.saat" class="eingabe flex-1" />
          <button type="button" class="knopf-sekundaer" :disabled="vorschlaegt" @click="vorschlagen">
            {{ vorschlaegt ? t('agenten.vorschlaegt') : t('agenten.vorschlag') }}
          </button>
        </div>
      </div>

      <hr class="border-slate-200 dark:border-slate-700" />

      <div>
        <label class="etikett" for="name">{{ t('agenten.name') }}</label>
        <input id="name" v-model="formular.name" class="eingabe" required />
      </div>
      <div>
        <label class="etikett" for="beruf">{{ t('agenten.beruf') }}</label>
        <input id="beruf" v-model="formular.beruf" class="eingabe" />
      </div>
      <div>
        <label class="etikett" for="hintergrund">{{ t('agenten.hintergrund') }}</label>
        <textarea id="hintergrund" v-model="formular.hintergrund" rows="3" class="eingabe" />
      </div>
      <div>
        <label class="etikett" for="werte">{{ t('agenten.werte') }}</label>
        <input id="werte" v-model="formular.werte" class="eingabe" placeholder="Neugier, Ehrlichkeit" />
      </div>
      <div class="flex gap-2">
        <button type="submit" class="knopf-primaer">{{ t('agenten.speichern') }}</button>
        <button type="button" class="knopf-sekundaer" @click="formularSichtbar = false">
          {{ t('agenten.abbrechen') }}
        </button>
      </div>
    </form>

    <Suchfeld v-if="store.agenten.length" v-model="suche" :platzhalter="t('agenten.suchen')" />

    <p v-if="store.ladend" class="text-sm text-slate-500">…</p>
    <p v-else-if="!store.agenten.length" class="text-sm text-slate-500">{{ t('agenten.leer') }}</p>
    <p v-else-if="!gefiltert.length" class="text-sm text-slate-500">{{ t('agenten.kein_treffer') }}</p>

    <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <AgentKarte
        v-for="agent in gefiltert"
        :key="agent.id"
        :agent="agent"
        @loeschen="(id) => store.loeschen(id)"
        @chatten="zumChat"
      />
    </div>
  </section>
</template>
