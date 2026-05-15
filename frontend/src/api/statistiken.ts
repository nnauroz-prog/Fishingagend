import { apiClient } from '@/api/client';

export interface Statistiken {
  agenten: number;
  simulationen: number;
  entitaeten: number;
  beziehungen: number;
  simulationen_nach_status: Record<string, number>;
}

export const statistikenApi = {
  hole: () => apiClient.get<Statistiken>('/api/statistiken').then((r) => r.data),
};
