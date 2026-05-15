import { apiClient } from '@/api/client';

export interface Entitaet {
  name: string;
  typ: string;
  beschreibung: string;
}

export interface Beziehung {
  von: string;
  nach: string;
  art: string;
  gewicht: number;
}

export interface Graph {
  entitaeten: Entitaet[];
  beziehungen: Beziehung[];
}

export const graphragApi = {
  extrahiere: (texte: string[]) =>
    apiClient.post<Graph>('/api/graphrag/extrahieren', { texte }).then((r) => r.data),
  lade: () => apiClient.get<Graph>('/api/graphrag/graph').then((r) => r.data),
  loesche: () => apiClient.delete<void>('/api/graphrag/graph').then((r) => r.data),
  abfrage: (frage: string) =>
    apiClient.post<{ antwort: string }>('/api/graphrag/abfrage', { frage }).then((r) => r.data),
};
