import { setActivePinia, createPinia } from 'pinia';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { agentenApi } from '@/api/agenten';
import type { Agent } from '@/api/typen';
import { useAgentenStore } from '@/store/agenten';

vi.mock('@/api/agenten', () => ({
  agentenApi: {
    liste: vi.fn(),
    erstelle: vi.fn(),
    loesche: vi.fn(),
  },
}));

const beispielAgent: Agent = {
  id: 'a1',
  persona: {
    name: 'Anna',
    hintergrund: '',
    werte: [],
    charakterzuege: [],
    beziehungen: {},
    sprachstil: 'neutral',
  },
  erstellt_am: '2026-01-01T00:00:00Z',
  aktualisiert_am: '2026-01-01T00:00:00Z',
};

describe('agentenStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it('lädt Agenten via API', async () => {
    vi.mocked(agentenApi.liste).mockResolvedValue([beispielAgent]);
    const store = useAgentenStore();
    await store.laden();
    expect(store.agenten).toEqual([beispielAgent]);
    expect(store.ladend).toBe(false);
  });

  it('setzt Fehler bei Lade-Problem', async () => {
    vi.mocked(agentenApi.liste).mockRejectedValue(new Error('boom'));
    const store = useAgentenStore();
    await store.laden();
    expect(store.fehler).toBe('boom');
  });

  it('löscht einen Agenten lokal nach API-Aufruf', async () => {
    vi.mocked(agentenApi.liste).mockResolvedValue([beispielAgent]);
    vi.mocked(agentenApi.loesche).mockResolvedValue(undefined as unknown as void);
    const store = useAgentenStore();
    await store.laden();
    await store.loeschen('a1');
    expect(store.agenten).toEqual([]);
  });
});
