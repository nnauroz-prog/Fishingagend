<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';

import { chatApi } from '@/api/chat';
import type { Nachricht } from '@/api/typen';
import ChatNachricht from '@/components/ChatNachricht.vue';
import { useAgentenStore } from '@/store/agenten';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const store = useAgentenStore();

const eingabe = ref('');
const verlauf = ref<Nachricht[]>([]);
const sendet = ref(false);
const liste = ref<HTMLDivElement | null>(null);

const agentId = computed({
  get: () => (route.params.agentId as string) ?? '',
  set: (v) => router.replace({ name: 'chat', params: { agentId: v } }),
});

const aktiverAgent = computed(() => store.agenten.find((a) => a.id === agentId.value));

onMounted(async () => {
  if (!store.agenten.length) await store.laden();
});

watch(agentId, () => {
  verlauf.value = [];
});

async function senden() {
  if (!agentId.value || !eingabe.value.trim()) return;
  const text = eingabe.value.trim();
  verlauf.value.push({ rolle: 'nutzer', inhalt: text, zeitstempel: new Date().toISOString() });
  eingabe.value = '';
  sendet.value = true;
  await nextTick();
  liste.value?.scrollTo({ top: liste.value.scrollHeight });

  try {
    const antwort = await chatApi.senden(agentId.value, text, verlauf.value);
    verlauf.value.push(antwort.nachricht);
  } catch {
    verlauf.value.push({
      rolle: 'system',
      inhalt: t('fehler.netzwerk'),
      zeitstempel: new Date().toISOString(),
    });
  } finally {
    sendet.value = false;
    await nextTick();
    liste.value?.scrollTo({ top: liste.value.scrollHeight });
  }
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

    <div
      ref="liste"
      class="karte flex-1 overflow-y-auto"
    >
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
        :disabled="!agentId || sendet"
      />
      <button type="submit" class="knopf-primaer" :disabled="!agentId || sendet">
        {{ t('chat.senden') }}
      </button>
    </form>
  </section>
</template>
