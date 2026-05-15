import { apiClient } from '@/api/client';
import type { ChatAntwort, Nachricht } from '@/api/typen';

export const chatApi = {
  senden: (agent_id: string, nachricht: string, verlauf: Nachricht[]) =>
    apiClient
      .post<ChatAntwort>('/api/chat', { agent_id, nachricht, verlauf })
      .then((r) => r.data),
};
