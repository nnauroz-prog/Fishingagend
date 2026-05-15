import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { abonniereSimulation } from '@/api/websocket';

class FakeSocket {
  static letzte: FakeSocket | null = null;
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;
  url: string;
  readyState = 0;
  onmessage: ((e: { data: string }) => void) | null = null;
  onerror: (() => void) | null = null;
  geschlossen = false;

  constructor(url: string) {
    this.url = url;
    FakeSocket.letzte = this;
    setTimeout(() => {
      this.readyState = 1;
    }, 0);
  }

  close() {
    this.readyState = 3;
    this.geschlossen = true;
  }
}

describe('abonniereSimulation', () => {
  beforeEach(() => {
    // @ts-expect-error – global polyfill
    globalThis.WebSocket = FakeSocket;
    FakeSocket.letzte = null;
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('öffnet eine WebSocket gegen den Backend-Pfad', () => {
    abonniereSimulation('abc', () => {});
    expect(FakeSocket.letzte).not.toBeNull();
    expect(FakeSocket.letzte!.url).toMatch(/\/api\/simulation\/abc\/strom$/);
    expect(FakeSocket.letzte!.url.startsWith('ws')).toBe(true);
  });

  it('reicht eingehende Nachrichten als Objekt durch', () => {
    const fn = vi.fn();
    abonniereSimulation('x', fn);
    FakeSocket.letzte!.onmessage!({
      data: JSON.stringify({ typ: 'schritt', nummer: 1, welt: 'kontrolle', ereignisse: ['Hi'] }),
    });
    expect(fn).toHaveBeenCalledWith(
      expect.objectContaining({ typ: 'schritt', nummer: 1, ereignisse: ['Hi'] }),
    );
  });

  it('schließt die Verbindung bei Abbruch', () => {
    const stop = abonniereSimulation('x', () => {});
    FakeSocket.letzte!.readyState = 1;
    stop();
    expect(FakeSocket.letzte!.geschlossen).toBe(true);
  });
});
