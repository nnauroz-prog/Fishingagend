/**
 * Sehr kleines Force-Directed-Layout — Federn entlang Kanten,
 * Coulomb-Repulsion zwischen allen Knoten, Schwerkraft Richtung Zentrum.
 *
 * Bewusst keine D3-Abhaengigkeit: ~80 Zeilen, deterministisch via festem
 * Seed (Math.sin(i)) damit das Layout zwischen Reloads stabil bleibt.
 */

export interface KnotenPos {
  id: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
}

export interface KantenRef {
  von: string;
  nach: string;
}

export function erstelleLayout(
  knotenIds: string[],
  kanten: KantenRef[],
  breite: number,
  hoehe: number,
): { knoten: Map<string, KnotenPos>; schritt: () => void } {
  const knoten = new Map<string, KnotenPos>();
  const cx = breite / 2;
  const cy = hoehe / 2;
  const radius = Math.min(breite, hoehe) * 0.35;

  knotenIds.forEach((id, i) => {
    const winkel = (i / knotenIds.length) * Math.PI * 2;
    knoten.set(id, {
      id,
      x: cx + Math.cos(winkel) * radius * (0.6 + 0.4 * Math.abs(Math.sin(i * 1.3))),
      y: cy + Math.sin(winkel) * radius * (0.6 + 0.4 * Math.abs(Math.cos(i * 1.7))),
      vx: 0,
      vy: 0,
    });
  });

  function schritt() {
    const knotenListe = [...knoten.values()];

    // Repulsion: jeder gegen jeden
    for (let i = 0; i < knotenListe.length; i++) {
      for (let j = i + 1; j < knotenListe.length; j++) {
        const a = knotenListe[i];
        const b = knotenListe[j];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const dist2 = Math.max(dx * dx + dy * dy, 100);
        const f = 4500 / dist2;
        const dist = Math.sqrt(dist2);
        const fx = (dx / dist) * f;
        const fy = (dy / dist) * f;
        a.vx -= fx;
        a.vy -= fy;
        b.vx += fx;
        b.vy += fy;
      }
    }

    // Federn entlang Kanten
    for (const kante of kanten) {
      const a = knoten.get(kante.von);
      const b = knoten.get(kante.nach);
      if (!a || !b) continue;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
      const f = (dist - 120) * 0.04;
      const fx = (dx / dist) * f;
      const fy = (dy / dist) * f;
      a.vx += fx;
      a.vy += fy;
      b.vx -= fx;
      b.vy -= fy;
    }

    // Schwerkraft + Daempfung + Position aktualisieren
    for (const k of knotenListe) {
      k.vx += (cx - k.x) * 0.005;
      k.vy += (cy - k.y) * 0.005;
      k.vx *= 0.85;
      k.vy *= 0.85;
      k.x = Math.max(20, Math.min(breite - 20, k.x + k.vx));
      k.y = Math.max(20, Math.min(hoehe - 20, k.y + k.vy));
    }
  }

  return { knoten, schritt };
}
