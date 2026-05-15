import axios from 'axios';

import { useToastStore } from '@/store/toasts';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASIS ?? 'http://localhost:8000',
  timeout: 30_000,
});

// Token aus localStorage automatisch im Authorization-Header senden
apiClient.interceptors.request.use((config) => {
  try {
    const roh = localStorage.getItem('fishingagend-auth');
    if (roh) {
      const daten = JSON.parse(roh);
      if (daten?.token) {
        config.headers = config.headers ?? {};
        config.headers.Authorization = `Bearer ${daten.token}`;
      }
    }
  } catch {
    // ignore
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (fehler) => {
    const status = fehler?.response?.status;
    const detail = fehler?.response?.data?.detail;
    const meldung = detail || fehler?.message || 'Unbekannter Fehler';

    // Pinia-Store darf erst zur Laufzeit geholt werden, sonst bricht
    // das Setup beim Modul-Import.
    try {
      const toasts = useToastStore();
      if (status && status >= 500) {
        toasts.fehler(`Serverfehler ${status}: ${meldung}`);
      } else if (!fehler.response) {
        toasts.fehler(`Verbindung zum Server nicht möglich: ${meldung}`);
      } else if (status >= 400 && status !== 404) {
        toasts.fehler(`${status}: ${meldung}`);
      }
    } catch {
      // Pinia noch nicht initialisiert (z. B. in Tests) — ignorieren.
    }

    if (import.meta.env.DEV) {
      console.error('[api]', status, fehler?.config?.url, meldung);
    }
    return Promise.reject(fehler);
  },
);

export const apiBasis = (): string =>
  (import.meta.env.VITE_API_BASIS as string | undefined) ?? 'http://localhost:8000';
