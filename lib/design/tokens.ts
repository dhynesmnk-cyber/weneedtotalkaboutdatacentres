/**
 * Design tokens: the single source for every colour the site uses.
 *
 * Tailwind reads these as CSS variables (see tailwind.config.ts), so a class
 * such as `text-fact-ink` or `bg-slate-50` resolves to a variable that changes
 * with the reader's colour scheme. Light values for `slate` and `surface` are
 * Tailwind's own, so light mode looks exactly as it did before tokens existed;
 * dark values are new.
 *
 * The three layer families (fact, editorial, gap) stay different hues in both
 * schemes, per the fact/opinion separation rule in docs/UI.md. Contrast is
 * asserted in tests/tokens.test.ts against the WCAG 2.2 AA thresholds.
 */

// Relative, not '@/lib/types': tailwind.config.ts loads this file outside the
// Next.js resolver, where the path alias does not exist.
import { EVENT_CATEGORIES, type EventCategory } from '../types';

export type Scheme = 'light' | 'dark';

/** Neutral greys, 50 (lightest in light mode) to 950. Inverted for dark. */
export const SLATE_STEPS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950] as const;
export type SlateStep = (typeof SLATE_STEPS)[number];

const SLATE: Record<Scheme, Record<SlateStep, string>> = {
  light: {
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a',
    950: '#020617',
  },
  dark: {
    50: '#121b2b',
    100: '#19243a',
    200: '#253247',
    300: '#334259',
    400: '#5f6f86',
    500: '#8a99ae',
    600: '#a5b2c4',
    700: '#c3cddb',
    800: '#dbe2ec',
    900: '#edf1f6',
    950: '#f7f9fb',
  },
};

/** A layer's three roles: background, border and text. */
export type Layer = { wash: string; edge: string; ink: string };

export const LAYER_NAMES = ['fact', 'editorial', 'gap', 'defect'] as const;
export type LayerName = (typeof LAYER_NAMES)[number];

const LAYERS: Record<Scheme, Record<LayerName, Layer>> = {
  light: {
    // Fact layer: cool, neutral, evidential.
    fact: { wash: '#eef2f7', edge: '#c3cfdd', ink: '#24405e' },
    // Editorial layer: warm, clearly not the fact layer.
    editorial: { wash: '#fdf1e7', edge: '#e8c5a0', ink: '#7a4413' },
    // Gaps are a finding, not an error. Distinct from both layers.
    gap: { wash: '#f4f0fa', edge: '#cfc0e8', ink: '#4d3378' },
    // A defect in the data itself: a blank with no gap record, a broken citation.
    defect: { wash: '#fef2f2', edge: '#fca5a5', ink: '#991b1b' },
  },
  dark: {
    fact: { wash: '#14243a', edge: '#3a5a7e', ink: '#a9c6e8' },
    editorial: { wash: '#33200f', edge: '#7a5230', ink: '#f3c79c' },
    gap: { wash: '#241a38', edge: '#5f4a8a', ink: '#cdb9f0' },
    defect: { wash: '#3a1414', edge: '#8a3434', ink: '#f6b2b2' },
  },
};

/**
 * One colour per timeline track (G2 in docs/UX-PLAN.md). Hues follow the
 * Okabe-Ito colour-blind-safe set, darkened (light mode) or lightened (dark
 * mode) until the text clears 4.5:1 on its own wash. Every chip also carries
 * its category in words, so colour is never the only signal.
 */
export type Track = { wash: string; ink: string };

const TRACKS: Record<Scheme, Record<EventCategory, Track>> = {
  light: {
    planning: { wash: '#e6f1f8', ink: '#0b4f7c' },
    construction: { wash: '#fbf0dc', ink: '#6e4300' },
    media: { wash: '#f8e9f1', ink: '#85325f' },
    political: { wash: '#fbe9df', ink: '#953805' },
    community: { wash: '#e1f3ec', ink: '#005c43' },
    financial: { wash: '#f6f3d6', ink: '#575000' },
  },
  dark: {
    planning: { wash: '#0e2a3d', ink: '#9fd0f2' },
    construction: { wash: '#33270c', ink: '#f2c66b' },
    media: { wash: '#3a1a2c', ink: '#f0b3d3' },
    political: { wash: '#3d1d0d', ink: '#f7ad86' },
    community: { wash: '#0c3127', ink: '#86dcbf' },
    financial: { wash: '#2f2c0b', ink: '#e3d77a' },
  },
};

/** The page background. `bg-white` resolves to this. */
const SURFACE: Record<Scheme, string> = { light: '#ffffff', dark: '#0d1420' };

export type Palette = {
  surface: string;
  slate: Record<SlateStep, string>;
  layers: Record<LayerName, Layer>;
  tracks: Record<EventCategory, Track>;
};

export const PALETTES: Record<Scheme, Palette> = {
  light: { surface: SURFACE.light, slate: SLATE.light, layers: LAYERS.light, tracks: TRACKS.light },
  dark: { surface: SURFACE.dark, slate: SLATE.dark, layers: LAYERS.dark, tracks: TRACKS.dark },
};

/** `#24405e` to `36 64 94`, the form Tailwind's `<alpha-value>` needs. */
export function hexToRgbChannels(hex: string): string {
  const match = /^#([0-9a-f]{6})$/i.exec(hex);
  if (!match) throw new Error(`Not a six-digit hex colour: ${hex}`);
  const value = parseInt(match[1] as string, 16);
  return `${(value >> 16) & 255} ${(value >> 8) & 255} ${value & 255}`;
}

/** Every CSS custom property for one scheme, values as RGB channels. */
export function cssVariables(scheme: Scheme): Record<string, string> {
  const palette = PALETTES[scheme];
  const vars: Record<string, string> = {
    '--surface': hexToRgbChannels(palette.surface),
  };
  for (const step of SLATE_STEPS) {
    vars[`--slate-${step}`] = hexToRgbChannels(palette.slate[step]);
  }
  for (const name of LAYER_NAMES) {
    const layer = palette.layers[name];
    vars[`--${name}-wash`] = hexToRgbChannels(layer.wash);
    vars[`--${name}-edge`] = hexToRgbChannels(layer.edge);
    vars[`--${name}-ink`] = hexToRgbChannels(layer.ink);
  }
  for (const category of EVENT_CATEGORIES) {
    const track = palette.tracks[category];
    vars[`--track-${category}-wash`] = hexToRgbChannels(track.wash);
    vars[`--track-${category}-ink`] = hexToRgbChannels(track.ink);
  }
  return vars;
}

/** A Tailwind colour value backed by a variable, keeping opacity modifiers working. */
export function tokenColour(variable: string): string {
  return `rgb(var(--${variable}) / <alpha-value>)`;
}

/** Relative luminance, WCAG 2.2 definition. */
export function luminance(hex: string): number {
  const [r, g, b] = hexToRgbChannels(hex)
    .split(' ')
    .map((c) => {
      const s = Number(c) / 255;
      return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
    }) as [number, number, number];
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** Contrast ratio between two colours, from 1 to 21. */
export function contrast(a: string, b: string): number {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x) as [number, number];
  return (hi + 0.05) / (lo + 0.05);
}
