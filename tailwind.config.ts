import type { Config } from 'tailwindcss';

/**
 * Colour tokens are semantic, not decorative. The fact and editorial palettes
 * are deliberately different hue families so the two layers stay distinguishable
 * at a glance, per the fact/opinion separation rule in docs/UI.md.
 *
 * Contrast: every `*-ink` token is checked against its `*-wash` counterpart at
 * 4.5:1 or better for the WCAG 2.2 AA target.
 */
const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Fact layer: cool, neutral, evidential.
        fact: {
          wash: '#eef2f7',
          edge: '#c3cfdd',
          ink: '#24405e',
        },
        // Editorial layer: warm, clearly not the fact layer.
        editorial: {
          wash: '#fdf1e7',
          edge: '#e8c5a0',
          ink: '#7a4413',
        },
        // Gaps are a finding, not an error. Distinct from both layers.
        gap: {
          wash: '#f4f0fa',
          edge: '#cfc0e8',
          ink: '#4d3378',
        },
      },
      fontFamily: {
        sans: ['ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

export default config;
