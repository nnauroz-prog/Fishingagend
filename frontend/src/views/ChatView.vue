<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';

import { chatApi } from '@/api/chat';
import type { Nachricht } from '@/api/typen';
import ChatNachricht from '@/components/ChatNachricht.vue';
import { useAgentenStore } from '@/store/agenten';
import { useToastStore } from '@/store/toasts';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const store = useAgentenStore();
const toasts = useToastStore();

const eingabe = ref('');
const verlauf = ref<Nachricht[]>([]);
const sendet = ref(false);
const aktiverStream = ref<(() => void) | null>(null);
const liste = ref<HTMLDivElement | null>(null);

const agentId = computed({
  get: () => (route.params.agentId as string) ?? '',
  set: (v) => router.replace({ name: 'chat', params: { agentId: v } }),
});

const aktiverAgent = computed(() => store.agenten.find((a) => a.id === agentId.value));

onMounted(async () => {
  if (!store.agenten.length) await store.laden();
});

onUnmounted(() => aktiverStream.value?.());

watch(agentId, () => {
  aktiverStream.value?.();
  verlauf.value = [];
});

async function nachUnten() {
  await nextTick();
  liste.value?.scrollTo({ top: liste.value.scrollHeight });
}

function senden() {
  if (!agentId.value || !eingabe.value.trim() || sendet.value) return;
  const text = eingabe.value.trim();
  verlauf.value.push({ rolle: 'nutzer', inhalt: text, zeitstempel: new Date().toISOString() });
  eingabe.value = '';
  sendet.value = true;

  const platzhalter: Nachricht = {
    rolle: 'agent',
    inhalt: '',
    zeitstempel: new Date().toISOString(),
  };
  verlauf.value.push(platzhalter);
  void nachUnten();

  aktiverStream.value = chatApi.stroeme(agentId.value, text, verlauf.value.slice(0, -2), {
    aufDelta(delta) {
      platzhalter.inhalt += delta;
      void nachUnten();
    },
    aufEnde(gesamt) {
      platzhalter.inhalt = gesamt;
      sendet.value = false;
      aktiverStream.value = null;
    },
    aufFehler(meldung) {
      platzhalter.inhalt = '';
      verlauf.value.pop();
      toasts.fehler(`${t('fehler.allgemein')} ${meldung}`);
      sendet.value = false;
      aktiverStream.value = null;
    },
  });
}

function abbrechen() {
  aktiverStream.value?.();
  aktiverStream.value = null;
  sendet.value = false;
}
</script>

<template>
  <section class="flex h-[calc(100vh-12rem)] flex-col gap-4">
    <header class="flex items-center justify-between gap-3">
      <h1 class="text-2xl font-bold">{{ t('chat.titel') }}</h1>
      <select v-model="agentId" class="eingabe max-w-xs">
        <option value="" disabled>{{ t('chat.agent_waehlen') }}</option>
        <option v-for="a in store.agenten" :key="a.id" :value="a.id">
          {{ a.persona.name }}
        </option>
      </select>
    </header>

    <p v-if="aktiverAgent" class="text-sm text-slate-500">
      {{ aktiverAgent.persona.beruf }} — {{ aktiverAgent.persona.hintergrund }}
    </p>

    <div ref="liste" class="karte flex-1 overflow-y-auto">
      <div v-if="!verlauf.length" class="grid h-full place-items-center text-sm text-slate-500">
        {{ t('chat.agent_waehlen') }}
      </div>
      <div v-else class="space-y-3">
        <ChatNachricht v-for="(n, i) in verlauf" :key="i" :nachricht="n" />
        <p v-if="sendet" class="text-xs text-slate-500">{{ t('chat.denkt') }}</p>
      </div>
    </div>

    <form class="flex gap-2" @submit.prevent="senden">
      <input
        v-model="eingabe"
        :placeholder="t('chat.platzhalter')"
        class="eingabe flex-1"
        :disabled="!agentId"
      />
      <button v-if="!sendet" type="submit" class="knopf-primaer" :disabled="!agentId">
        {{ t('chat.senden') }}
      </button>
      <button v-else type="button" class="knopf-sekundaer" @click="abbrechen">
        {{ t('chat.abbrechen') }}
      </button>
    </form>
  </section>
</template>
