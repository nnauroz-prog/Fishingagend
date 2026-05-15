import { describe, expect, it } from 'vitest';

import { erstelleLayout } from '@/werkzeuge/forcelayout';

describe('erstelleLayout', () => {
  it('platziert alle Knoten innerhalb der Box', () => {
    const { knoten, schritt } = erstelleLayout(['a', 'b', 'c'], [{ von: 'a', nach: 'b' }], 400, 300);
    for (let i = 0; i < 50; i++) schritt();
    for (const k of knoten.values()) {
      expect(k.x).toBeGreaterThanOrEqual(20);
      expect(k.x).toBeLessThanOrEqual(380);
      expect(k.y).toBeGreaterThanOrEqual(20);
      expect(k.y).toBeLessThanOrEqual(280);
    }
  });

  it('konvergiert: Geschwindigkeiten werden klein', () => {
    const { knoten, schritt } = erstelleLayout(
      ['a', 'b', 'c', 'd'],
      [
        { von: 'a', nach: 'b' },
        { von: 'b', nach: 'c' },
        { von: 'c', nach: 'd' },
      ],
      500,
      400,
    );
    for (let i = 0; i < 200; i++) schritt();
    const maxV = Math.max(...[...knoten.values()].map((k) => Math.hypot(k.vx, k.vy)));
    expect(maxV).toBeLessThan(2);
  });

  it('liefert leeres Layout bei keinen Knoten', () => {
    const { knoten } = erstelleLayout([], [], 400, 300);
    expect(knoten.size).toBe(0);
  });
});
