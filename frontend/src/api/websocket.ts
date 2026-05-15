import { apiBasis } from '@/api/client';

export type SimEreignis =
  | { typ: 'schritt'; nummer: number; welt: 'kontrolle' | 'variante'; ereignisse: string[] }
  | { typ: 'status'; status: 'geplant' | 'laeuft' | 'abgeschlossen' | 'fehlgeschlagen' }
  | { typ: 'ping' };

export function abonniereSimulation(
  simId: string,
  beim_ereignis: (e: SimEreignis) => void,
  bei_fehler?: (m: string) => void,
): () => void {
  const url = apiBasis()
    .replace(/^http/, 'ws')
    + `/api/simulation/${simId}/strom`;
  const ws = new WebSocket(url);

  ws.onmessage = (m) => {
    try {
      const event = JSON.parse(m.data) as SimEreignis;
      beim_ereignis(event);
    } catch (e) {
      bei_fehler?.(`Ungültige Nachricht: ${(e as Error).message}`);
    }
  };
  ws.onerror = () => bei_fehler?.('WebSocket-Fehler');

  return () => {
    if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
      ws.close();
    }
  };
}
