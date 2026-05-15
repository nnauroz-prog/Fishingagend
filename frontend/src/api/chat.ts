import { apiBasis, apiClient } from '@/api/client';
import type { ChatAntwort, Nachricht } from '@/api/typen';

export const chatApi = {
  senden: (agent_id: string, nachricht: string, verlauf: Nachricht[]) =>
    apiClient
      .post<ChatAntwort>('/api/chat', { agent_id, nachricht, verlauf })
      .then((r) => r.data),

  /** SSE-Stream — ruft `aufDelta` für jeden Text-Chunk auf, `aufEnde` mit dem
   * Gesamttext und `aufFehler` falls etwas schiefgeht. Gibt eine Funktion
   * zurück, mit der man den Stream abbrechen kann. */
  stroeme(
    agent_id: string,
    nachricht: string,
    verlauf: Nachricht[],
    handler: {
      aufDelta: (text: string) => void;
      aufEnde: (gesamt: string) => void;
      aufFehler?: (meldung: string) => void;
    },
  ): () => void {
    const controller = new AbortController();

    (async () => {
      try {
        const antwort = await fetch(`${apiBasis()}/api/chat/strom`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ agent_id, nachricht, verlauf }),
          signal: controller.signal,
        });
        if (!antwort.ok || !antwort.body) {
          handler.aufFehler?.(`HTTP ${antwort.status}`);
          return;
        }
        const reader = antwort.body.getReader();
        const decoder = new TextDecoder();
        let puffer = '';
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          puffer += decoder.decode(value, { stream: true });
          const teile = puffer.split('\n\n');
          puffer = teile.pop() ?? '';
          for (const block of teile) {
            const event = parseSse(block);
            if (!event) continue;
            if (event.typ === 'delta') handler.aufDelta(event.daten.text);
            else if (event.typ === 'fertig') handler.aufEnde(event.daten.text);
            else if (event.typ === 'fehler') handler.aufFehler?.(event.daten.meldung);
          }
        }
      } catch (e) {
        if ((e as Error).name !== 'AbortError') {
          handler.aufFehler?.((e as Error).message);
        }
      }
    })();

    return () => controller.abort();
  },
};

function parseSse(block: string): { typ: string; daten: any } | null {
  let typ = 'message';
  let daten = '';
  for (const zeile of block.split('\n')) {
    if (zeile.startsWith('event:')) typ = zeile.slice(6).trim();
    else if (zeile.startsWith('data:')) daten += zeile.slice(5).trim();
  }
  if (!daten) return null;
  try {
    return { typ, daten: JSON.parse(daten) };
  } catch {
    return null;
  }
}
