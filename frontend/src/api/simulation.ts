import { apiClient } from '@/api/client';
import type { Simulation, SimulationErstellen } from '@/api/typen';

export const simulationApi = {
  liste: () => apiClient.get<Simulation[]>('/api/simulation').then((r) => r.data),
  hole: (id: string) => apiClient.get<Simulation>(`/api/simulation/${id}`).then((r) => r.data),
  plane: (eingabe: SimulationErstellen) =>
    apiClient.post<Simulation>('/api/simulation', eingabe).then((r) => r.data),
  starte: (id: string) =>
    apiClient.post<Simulation>(`/api/simulation/${id}/starte`).then((r) => r.data),
  bericht: (id: string) =>
    apiClient.get<{ simulation_id: string; markdown: string }>(`/api/berichte/${id}`).then((r) => r.data),
};
