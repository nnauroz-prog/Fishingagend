import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

import { authApi, type Nutzer } from '@/api/auth';

const SPEICHER_SCHLUESSEL = 'fishingagend-auth';

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null);
  const nutzer = ref<Nutzer | null>(null);

  function lade() {
    const roh = localStorage.getItem(SPEICHER_SCHLUESSEL);
    if (!roh) return;
    try {
      const daten = JSON.parse(roh);
      token.value = daten.token;
      nutzer.value = daten.nutzer;
    } catch {
      localStorage.removeItem(SPEICHER_SCHLUESSEL);
    }
  }

  function speichere() {
    if (token.value && nutzer.value) {
      localStorage.setItem(
        SPEICHER_SCHLUESSEL,
        JSON.stringify({ token: token.value, nutzer: nutzer.value }),
      );
    } else {
      localStorage.removeItem(SPEICHER_SCHLUESSEL);
    }
  }

  async function anmelde(email: string, passwort: string) {
    const r = await authApi.anmelde(email, passwort);
    token.value = r.token;
    nutzer.value = r.nutzer;
    speichere();
  }

  async function registriere(email: string, passwort: string, anzeige_name: string) {
    await authApi.registriere(email, passwort, anzeige_name);
    await anmelde(email, passwort);
  }

  function abmelden() {
    token.value = null;
    nutzer.value = null;
    speichere();
  }

  const angemeldet = computed(() => !!token.value);

  return { token, nutzer, angemeldet, lade, anmelde, registriere, abmelden };
});
