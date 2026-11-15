import type { Config } from 'tailwindcss';
import plugin from 'tailwindcss/plugin';
import {
  cssVariables,
  LAYER_NAMES,
  SLATE_STEPS,
  tokenColour,
} from './lib/design/tokens';
import { EVENT_CATEGORIES } from './lib/types';

/**
 * Colour tokens are semantic, not decorative, and live in lib/design/tokens.ts.
 * Every colour below is a CSS variable, so the same class serves both colour
 * schemes. `white` and `slate` are remapped too: the pages were written with
 * them, and remapping is what lets every existing page follow the reader's
 * dark mode preference without a `dark:` variant on every element.
 *
 * Contrast for every pair the site uses is asserted in tests/tokens.test.ts.
 */

const slate = Object.fromEntries(SLATE_STEPS.map((s) => [s, tokenColour(`slate-${s}`)]));

const layers = Object.fromEntries(
  LAYER_NAMES.map((name) => [
    name,
    {
      wash: tokenColour(`${name}-wash`),
      edge: tokenColour(`${name}-edge`),
      ink: tokenColour(`${name}-ink`),
    },
  ]),
);

const tracks = Object.fromEntries(
  EVENT_CATEGORIES.map((c) => [
    c,
    { wash: tokenColour(`track-${c}-wash`), ink: tokenColour(`track-${c}-ink`) },
  ]),
);

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  darkMode: 'media',
  theme: {
    extend: {
      colors: {
        white: tokenColour('surface'),
        surface: tokenColour('surface'),
        slate,
        ...layers,
        track: tracks,
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        serif: ['var(--font-serif)', 'ui-serif', 'Georgia', 'Cambria', 'serif'],
        mono: ['var(--font-mono)', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      fontSize: {
        // Display sizes for the editorial layer. Record pages use the default scale.
        display: ['clamp(2.25rem, 1.6rem + 2.6vw, 3.75rem)', { lineHeight: '1.05', letterSpacing: '-0.015em' }],
        title: ['clamp(1.75rem, 1.4rem + 1.4vw, 2.5rem)', { lineHeight: '1.12', letterSpacing: '-0.01em' }],
        standfirst: ['clamp(1.125rem, 1.05rem + 0.35vw, 1.375rem)', { lineHeight: '1.5' }],
        essay: ['1.1875rem', { lineHeight: '1.7' }],
      },
      maxWidth: {
        measure: '68ch',
      },
    },
  },
  plugins: [
    plugin(({ addBase }) => {
      addBase({
        ':root': cssVariables('light'),
        '@media (prefers-color-scheme: dark)': {
          ':root': cssVariables('dark'),
        },
        // Paper is white whatever the screen prefers. Declared last so it wins.
        '@media print': {
          ':root': cssVariables('light'),
        },
      });
    }),
  ],
};

export default config;
