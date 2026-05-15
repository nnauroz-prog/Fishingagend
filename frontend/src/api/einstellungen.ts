import { apiClient } from '@/api/client';

export interface Einstellungen {
  llm: {
    provider: string;
    anthropic_modell: string;
    anthropic_api_key_gesetzt: boolean;
    openai_modell: string;
    openai_basis_url: string | null;
    openai_api_key_gesetzt: boolean;
  };
  simulation: {
    max_agenten: number;
    simulations_schritte: number;
    demo_daten_einspielen: boolean;
  };
  datenbank_dialekt: string;
}

export const einstellungenApi = {
  hole: () => apiClient.get<Einstellungen>('/api/einstellungen').then((r) => r.data),
};
