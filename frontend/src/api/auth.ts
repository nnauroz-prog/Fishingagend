import { apiClient } from '@/api/client';

export interface Nutzer {
  id: string;
  email: string;
  anzeige_name: string;
  rolle: string;
}

export interface TokenAusgabe {
  token: string;
  token_typ: string;
  nutzer: Nutzer;
}

export const authApi = {
  registriere: (email: string, passwort: string, anzeige_name: string) =>
    apiClient
      .post<Nutzer>('/api/auth/registriere', { email, passwort, anzeige_name })
      .then((r) => r.data),
  anmelde: (email: string, passwort: string) =>
    apiClient
      .post<TokenAusgabe>('/api/auth/anmelde', { email, passwort })
      .then((r) => r.data),
  ich: () => apiClient.get<Nutzer>('/api/auth/ich').then((r) => r.data),
};
