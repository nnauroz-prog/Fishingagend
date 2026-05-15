import { describe, expect, it } from 'vitest';

import { router } from '@/router';

describe('router', () => {
  it('hat alle Hauptseiten als benannte Routen', () => {
    const namen = router.getRoutes().map((r) => r.name);
    for (const erwartet of [
      'startseite',
      'agenten',
      'agent-detail',
      'chat',
      'simulation',
      'simulation-detail',
      'graphrag',
      'berichte',
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
