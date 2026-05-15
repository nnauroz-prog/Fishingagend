<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

import { useAuthStore } from '@/store/auth';
import { useToastStore } from '@/store/toasts';

const { t } = useI18n();
const router = useRouter();
const auth = useAuthStore();
const toasts = useToastStore();

const modus = ref<'anmelden' | 'registrieren'>('anmelden');
const formular = reactive({ email: '', passwort: '', anzeige_name: '' });
const arbeitet = ref(false);

async function absenden() {
  arbeitet.value = true;
  try {
    if (modus.value === 'anmelden') {
      await auth.anmelde(formular.email, formular.passwort);
      toasts.erfolg(`Willkommen, ${auth.nutzer?.anzeige_name}!`);
    } else {
      await auth.registriere(formular.email, formular.passwort, formular.anzeige_name);
      toasts.erfolg('Konto erstellt und angemeldet.');
    }
    router.push('/');
  } finally {
    arbeitet.value = false;
  }
}
</script>

<template>
  <section class="mx-auto max-w-md space-y-6">
    <header class="text-center">
      <h1 class="text-2xl font-bold">
        {{ modus === 'anmelden' ? t('auth.anmelden') : t('auth.registrieren') }}
      </h1>
      <p class="text-sm text-slate-500">{{ t('auth.einleitung') }}</p>
    </header>

    <form class="karte space-y-3" @submit.prevent="absenden">
      <div v-if="modus === 'registrieren'">
        <label class="etikett">{{ t('auth.anzeige_name') }}</label>
        <input v-model="formular.anzeige_name" class="eingabe" required minlength="1" />
      </div>
      <div>
        <label class="etikett">{{ t('auth.email') }}</label>
        <input v-model="formular.email" type="email" class="eingabe" required />
      </div>
      <div>
        <label class="etikett">{{ t('auth.passwort') }}</label>
        <input v-model="formular.passwort" type="password" class="eingabe" required minlength="8" />
      </div>
      <button type="submit" class="knopf-primaer w-full" :disabled="arbeitet">
        {{ arbeitet ? '…' : modus === 'anmelden' ? t('auth.anmelden') : t('auth.registrieren') }}
      </button>
    </form>

    <p class="text-center text-sm">
      <button
        class="text-markenblau-600 hover:underline"
        @click="modus = modus === 'anmelden' ? 'registrieren' : 'anmelden'"
      >
        {{ modus === 'anmelden' ? t('auth.zur_registrierung') : t('auth.zur_anmeldung') }}
      </button>
    </p>
  </section>
</template>
