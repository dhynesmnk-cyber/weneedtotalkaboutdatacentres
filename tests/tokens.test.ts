import { describe, expect, it } from 'vitest';
import {
  contrast,
  cssVariables,
  hexToRgbChannels,
  LAYER_NAMES,
  PALETTES,
  type Scheme,
} from '@/lib/design/tokens';
import { EVENT_CATEGORIES } from '@/lib/types';

/**
 * WCAG 2.2 AA: 4.5:1 for text, 3:1 for the boundaries of controls and other
 * meaningful graphics. Asserted for every pairing the site uses, in both
 * colour schemes, so a palette change that breaks one fails here first.
 */
const TEXT = 4.5;
const GRAPHIC = 3;

const SCHEMES: Scheme[] = ['light', 'dark'];

describe.each(SCHEMES)('%s palette', (scheme) => {
  const p = PALETTES[scheme];

  it.each(LAYER_NAMES)('%s ink is legible on its wash and on the page', (name) => {
    const layer = p.layers[name];
    expect(contrast(layer.ink, layer.wash)).toBeGreaterThanOrEqual(TEXT);
    expect(contrast(layer.ink, p.surface)).toBeGreaterThanOrEqual(TEXT);
  });

  it.each([600, 700, 800, 900] as const)('slate-%i text is legible on the page and on panels', (step) => {
    expect(contrast(p.slate[step], p.surface)).toBeGreaterThanOrEqual(TEXT);
    expect(contrast(p.slate[step], p.slate[50])).toBeGreaterThanOrEqual(TEXT);
    expect(contrast(p.slate[step], p.slate[100])).toBeGreaterThanOrEqual(TEXT);
  });

  it('keeps body text legible on every layer wash', () => {
    for (const name of LAYER_NAMES) {
      expect(contrast(p.slate[700], p.layers[name].wash)).toBeGreaterThanOrEqual(TEXT);
    }
  });

  it('gives form controls a visible boundary', () => {
    expect(contrast(p.slate[500], p.surface)).toBeGreaterThanOrEqual(GRAPHIC);
  });

  it('keeps the focus ring and skip link visible', () => {
    expect(contrast(p.layers.fact.ink, p.surface)).toBeGreaterThanOrEqual(GRAPHIC);
    // The skip link is surface-coloured text on a fact-ink background.
    expect(contrast(p.surface, p.layers.fact.ink)).toBeGreaterThanOrEqual(TEXT);
  });

  it.each([...EVENT_CATEGORIES])('the %s track chip is legible and its marker visible', (category) => {
    const track = p.tracks[category];
    expect(contrast(track.ink, track.wash)).toBeGreaterThanOrEqual(TEXT);
    expect(contrast(track.ink, p.surface)).toBeGreaterThanOrEqual(GRAPHIC);
  });

  it('keeps the three layers different hues', () => {
    const inks = LAYER_NAMES.map((n) => p.layers[n].ink);
    expect(new Set(inks).size).toBe(inks.length);
  });
});

describe('CSS variables', () => {
  it('emits the same set of variables for both schemes', () => {
    expect(Object.keys(cssVariables('dark')).sort()).toEqual(Object.keys(cssVariables('light')).sort());
  });

  it('keeps light mode identical to the palette it replaced', () => {
    const light = cssVariables('light');
    expect(light['--fact-ink']).toBe(hexToRgbChannels('#24405e'));
    expect(light['--editorial-ink']).toBe(hexToRgbChannels('#7a4413'));
    expect(light['--gap-ink']).toBe(hexToRgbChannels('#4d3378'));
    expect(light['--surface']).toBe('255 255 255');
  });

  it('rejects a colour that is not six-digit hex', () => {
    expect(() => hexToRgbChannels('#fff')).toThrow();
  });
});
