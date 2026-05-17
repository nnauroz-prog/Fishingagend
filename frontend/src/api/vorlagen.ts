import { apiClient } from '@/api/client';
import type { Simulation } from '@/api/typen';

export interface Vorlage {
  schluessel: string;
  titel: string;
  beschreibung: string;
  kategorie: string;
  schritte: number;
  dual_modus: boolean;
  plattform_modus: boolean;
  anzahl_personas: number;
}

export const vorlagenApi = {
  liste: () => apiClient.get<Vorlage[]>('/api/vorlagen').then((r) => r.data),
  anwenden: (schluessel: string, name?: string, sofort_starten = false) =>
    apiClient
      .post<Simulation>(`/api/vorlagen/${schluessel}/anwenden`, {
        name,
        sofort_starten,
      })
      .then((r) => r.data),
};
