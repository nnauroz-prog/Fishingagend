<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>

<template>
  <section class="grid place-items-center py-24 text-center">
    <div class="space-y-4">
      <p class="text-7xl font-black text-markenblau-600">404</p>
      <h1 class="text-2xl font-bold">{{ t('nicht_gefunden.titel') }}</h1>
      <p class="text-slate-500">{{ t('nicht_gefunden.text') }}</p>
      <RouterLink to="/" class="knopf-primaer">
        ← {{ t('navigation.startseite') }}
      </RouterLink>
    </div>
  </section>
</template>
