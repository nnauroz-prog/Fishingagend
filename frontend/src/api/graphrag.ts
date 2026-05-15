import { apiClient } from '@/api/client';

export interface ExtraktionsErgebnis {
  entitaeten: number;
  beziehungen: number;
}

export const graphragApi = {
  extrahiere: (texte: string[]) =>
    apiClient
      .post<ExtraktionsErgebnis>('/api/graphrag/extrahieren', { texte })
      .then((r) => r.data),
  abfrage: (frage: string) =>
    apiClient
      .post<{ antwort: string }>('/api/graphrag/abfrage', { frage })
      .then((r) => r.data),
};
