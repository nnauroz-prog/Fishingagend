import { apiClient } from '@/api/client';
import type {
  FeedBeitrag,
  Folge,
  Simulation,
  SimulationErstellen,
} from '@/api/typen';

export const simulationApi = {
  liste: () => apiClient.get<Simulation[]>('/api/simulation').then((r) => r.data),
  hole: (id: string) => apiClient.get<Simulation>(`/api/simulation/${id}`).then((r) => r.data),
  plane: (eingabe: SimulationErstellen) =>
    apiClient.post<Simulation>('/api/simulation', eingabe).then((r) => r.data),
  starte: (id: string, sofort = false) =>
    apiClient
      .post<Simulation>(`/api/simulation/${id}/starte`, null, { params: { sofort } })
      .then((r) => r.data),
  bericht: (id: string) =>
    apiClient.get<{ simulation_id: string; markdown: string }>(`/api/berichte/${id}`).then((r) => r.data),
  berichtChat: (id: string, nachricht: string, verlauf: { rolle: string; inhalt: string; zeitstempel: string }[]) =>
    apiClient
      .post<{ antwort: string }>(`/api/berichte/${id}/chat`, { nachricht, verlauf })
      .then((r) => r.data),
  feed: (id: string, welt?: string) =>
    apiClient
      .get<FeedBeitrag[]>(`/api/simulation/${id}/feed`, { params: welt ? { welt } : {} })
      .then((r) => r.data),
  folgen: (id: string, welt?: string) =>
    apiClient
      .get<Folge[]>(`/api/simulation/${id}/folgen`, { params: welt ? { welt } : {} })
      .then((r) => r.data),
  ausText: (beschreibung: string) =>
    apiClient
      .post<SimulationErstellen>('/api/simulation/aus-text', { beschreibung })
      .then((r) => r.data),
  batch: (
    vorlage: SimulationErstellen,
    variablen_serie: Record<string, unknown>[],
    sofort_starten = false,
  ) =>
    apiClient
      .post<Simulation[]>('/api/simulation/batch', {
        vorlage,
        variablen_serie,
        sofort_starten,
      })
      .then((r) => r.data),
};
