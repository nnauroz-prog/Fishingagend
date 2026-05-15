import { apiClient } from '@/api/client';
import type { Agent, AgentErstellen } from '@/api/typen';

export const agentenApi = {
  liste: () => apiClient.get<Agent[]>('/api/agenten').then((r) => r.data),
  hole: (id: string) => apiClient.get<Agent>(`/api/agenten/${id}`).then((r) => r.data),
  erstelle: (eingabe: AgentErstellen) =>
    apiClient.post<Agent>('/api/agenten', eingabe).then((r) => r.data),
  loesche: (id: string) => apiClient.delete<void>(`/api/agenten/${id}`).then((r) => r.data),
};
