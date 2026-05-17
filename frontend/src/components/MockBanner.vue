<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

import { einstellungenApi } from '@/api/einstellungen';

const { t } = useI18n();
const mockAktiv = ref(false);
const versteckt = ref(localStorage.getItem('fishingagend-mock-versteckt') === '1');

onMounted(async () => {
  try {
    const e = await einstellungenApi.hole();
    // Mock-LLM ist aktiv, wenn KEIN passender API-Key fuer den gewaehlten
    // Provider gesetzt ist.
    if (e.llm.provider === 'anthropic' && !e.llm.anthropic_api_key_gesetzt) {
      mockAktiv.value = true;
    } else if (e.llm.provider === 'openai' && !e.llm.openai_api_key_gesetzt) {
      mockAktiv.value = true;
    }
  } catch {
    // Backend evtl. nicht erreichbar — Banner zeigen wir lieber nicht
  }
});

function ausblenden() {
  versteckt.value = true;
  localStorage.setItem('fishingagend-mock-versteckt', '1');
}
</script>

<template>
  <div
    v-if="mockAktiv && !versteckt"
    class="border-b border-yellow-300 bg-yellow-50 px-4 py-2 text-sm text-yellow-900 dark:border-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-200"
    role="status"
  >
    <div class="mx-auto flex max-w-7xl items-center gap-3">
      <span class="text-base">⚠</span>
      <p class="flex-1">
        <strong>{{ t('mock_banner.titel') }}</strong> — {{ t('mock_banner.text') }}
        <a
          href="https://console.anthropic.com/settings/keys"
          target="_blank"
          rel="noopener"
          class="underline"
        >
          {{ t('mock_banner.link') }}
        </a>
      </p>
      <button
        class="text-xs text-yellow-700 hover:text-yellow-900 dark:text-yellow-300"
        aria-label="Banner ausblenden"
        @click="ausblenden"
      >
        ✕
      </button>
    </div>
  </div>
</template>
