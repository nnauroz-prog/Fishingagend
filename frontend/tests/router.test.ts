import { describe, expect, it } from 'vitest';

import { router } from '@/router';

describe('router', () => {
  it('hat alle Hauptseiten als benannte Routen', () => {
    const namen = router.getRoutes().map((r) => r.name);
    for (const erwartet of [
      'startseite',
      'agenten',
      'agent-detail',
      'beziehungen',
      'chat',
      'simulation',
      'simulation-detail',
      'simulation-vergleich',
      'simulation-batch',
      'graphrag',
      'berichte',
      'pipeline',
      'vorlagen',
      'einstellungen',
      'audit',
      'anmelden',
      'nicht-gefunden',
    ]) {
      expect(namen).toContain(erwartet);
    }
  });

  it('erkennt unbekannte Pfade als nicht-gefunden', () => {
    const aufgeloest = router.resolve('/voellig-unbekannt');
    expect(aufgeloest.name).toBe('nicht-gefunden');
  });
});
