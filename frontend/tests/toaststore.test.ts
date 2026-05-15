import { setActivePinia, createPinia } from 'pinia';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useToastStore } from '@/store/toasts';

describe('toaststore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.useFakeTimers();
  });

  it('fügt einen Toast hinzu und entfernt ihn nach Ablauf', () => {
    const store = useToastStore();
    store.erfolg('Geschafft', 1000);
    expect(store.liste).toHaveLength(1);
    expect(store.liste[0].typ).toBe('erfolg');
    vi.advanceTimersByTime(1000);
    expect(store.liste).toHaveLength(0);
  });

  it('hält Toasts mit dauer 0 dauerhaft', () => {
    const store = useToastStore();
    store.info('Bleibt', 0);
    vi.advanceTimersByTime(60_000);
    expect(store.liste).toHaveLength(1);
  });

  it('entferne(id) räumt einen Toast manuell weg', () => {
    const store = useToastStore();
    const id = store.fehler('Fehler', 0);
    store.entferne(id);
    expect(store.liste).toHaveLength(0);
  });
});
