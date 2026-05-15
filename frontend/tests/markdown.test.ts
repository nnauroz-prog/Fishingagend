import { describe, expect, it } from 'vitest';

import { rendereMarkdown } from '@/werkzeuge/markdown';

describe('rendereMarkdown', () => {
  it('rendert Überschriften und Listen', () => {
    const html = rendereMarkdown('# Titel\n\n- eins\n- zwei');
    expect(html).toContain('<h1>Titel</h1>');
    expect(html).toContain('<li>eins</li>');
    expect(html).toContain('<li>zwei</li>');
  });

  it('rendert fettgedruckten Text', () => {
    const html = rendereMarkdown('Das ist **wichtig**.');
    expect(html).toContain('<strong>wichtig</strong>');
  });
});
