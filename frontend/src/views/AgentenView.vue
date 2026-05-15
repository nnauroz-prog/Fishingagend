<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import AgentKarte from '@/components/AgentKarte.vue';
import { useAgentenStore } from '@/store/agenten';

const { t } = useI18n();
const router = useRouter();
const store = useAgentenStore();

const formularSichtbar = ref(false);
const formular = reactive({
  name: '',
  beruf: '',
  hintergrund: '',
  werte: '',
});

onMounted(() => store.laden());

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
      charakterzuege: [],
      beziehungen: {},
      sprachstil: 'neutral',
    },
  });
  formularSichtbar.value = false;
  Object.assign(formular, { name: '', beruf: '', hintergrund: '', werte: '' });
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

    <p v-if="store.ladend" class="text-sm text-slate-500">…</p>
    <p v-else-if="!store.agenten.length" class="text-sm text-slate-500">{{ t('agenten.leer') }}</p>

    <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <AgentKarte
        v-for="agent in store.agenten"
        :key="agent.id"
        :agent="agent"
        @loeschen="(id) => store.loeschen(id)"
        @chatten="zumChat"
      />
    </div>
  </section>
</template>
