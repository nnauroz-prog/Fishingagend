import { apiClient } from '@/api/client';
import type { Agent, AgentErstellen, Persona } from '@/api/typen';

export const agentenApi = {
  liste: () => apiClient.get<Agent[]>('/api/agenten').then((r) => r.data),
  hole: (id: string) => apiClient.get<Agent>(`/api/agenten/${id}`).then((r) => r.data),
  erstelle: (eingabe: AgentErstellen) =>
    apiClient.post<Agent>('/api/agenten', eingabe).then((r) => r.data),
  loesche: (id: string) => apiClient.delete<void>(`/api/agenten/${id}`).then((r) => r.data),
  aktualisiere: (id: string, persona: Persona) =>
    apiClient.put<Agent>(`/api/agenten/${id}`, persona).then((r) => r.data),
  personaAusSaat: (saat: Record<string, string>) =>
    apiClient.post<Persona>('/api/agenten/aus-saat', { saat }).then((r) => r.data),
  ausGraph: (max_personen = 8, sofort_anlegen = true) =>
    apiClient
      .post<Agent[]>('/api/agenten/aus-graph', { max_personen, sofort_anlegen })
      .then((r) => r.data),
  merke: (id: string, inhalt: string) =>
    apiClient.post<{ status: string }>(`/api/agenten/${id}/gedaechtnis`, { inhalt }).then((r) => r.data),
  leseGedaechtnis: (id: string, grenze = 50) =>
    apiClient
      .get<string[]>(`/api/agenten/${id}/gedaechtnis`, { params: { grenze } })
      .then((r) => r.data),
};
