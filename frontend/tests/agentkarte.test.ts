import { mount } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';
import { describe, expect, it } from 'vitest';

import AgentKarte from '@/components/AgentKarte.vue';
import de from '@/i18n/de.json';

const i18n = createI18n({ legacy: false, locale: 'de', messages: { de } });

const beispielAgent = {
  id: 'abc-123',
  persona: {
    name: 'Lisa Weber',
    alter: 34,
    beruf: 'Klimawissenschaftlerin',
    hintergrund: 'Forscht zu Extremwetter.',
    werte: ['Wahrheit', 'Wirkung'],
    charakterzuege: ['analytisch'],
    beziehungen: {},
    sprachstil: 'fachlich',
  },
  erstellt_am: '2026-01-01T00:00:00Z',
  aktualisiert_am: '2026-01-01T00:00:00Z',
};

describe('AgentKarte', () => {
  it('zeigt Name und Beruf an', () => {
    const w = mount(AgentKarte, {
      props: { agent: beispielAgent },
      global: { plugins: [i18n] },
    });
    expect(w.text()).toContain('Lisa Weber');
    expect(w.text()).toContain('Klimawissenschaftlerin');
  });

  it('löst loeschen-Event mit Agent-ID aus', async () => {
    const w = mount(AgentKarte, {
      props: { agent: beispielAgent },
      global: { plugins: [i18n] },
    });
    await w.find('button:nth-child(2)').trigger('click');
    expect(w.emitted('loeschen')?.[0]).toEqual(['abc-123']);
  });
});
