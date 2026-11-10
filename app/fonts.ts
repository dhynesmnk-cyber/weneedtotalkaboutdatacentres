import localFont from 'next/font/local';

/**
 * Self-hosted type, loaded from the @fontsource packages so a build fetches
 * nothing from a font service and a reader's browser asks no third party for
 * anything. All three families are under the SIL Open Font Licence, which
 * ships in each package.
 *
 * - Newsreader: the editorial voice. Headlines and essay body text. A variable
 *   font with an optical-size axis, so display sizes are drawn for display.
 * - Inter: the record. Interface text, tables and figures.
 * - IBM Plex Mono: record ids and source ids.
 */

export const serif = localFont({
  src: [
    { path: '../node_modules/@fontsource-variable/newsreader/files/newsreader-latin-opsz-normal.woff2', style: 'normal' },
    { path: '../node_modules/@fontsource-variable/newsreader/files/newsreader-latin-opsz-italic.woff2', style: 'italic' },
  ],
  weight: '200 800',
  variable: '--font-serif',
  display: 'swap',
  fallback: ['Georgia', 'Cambria', 'serif'],
});

export const sans = localFont({
  src: [
    { path: '../node_modules/@fontsource-variable/inter/files/inter-latin-opsz-normal.woff2', style: 'normal' },
    { path: '../node_modules/@fontsource-variable/inter/files/inter-latin-opsz-italic.woff2', style: 'italic' },
  ],
  weight: '100 900',
  variable: '--font-sans',
  display: 'swap',
  fallback: ['system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
});

export const mono = localFont({
  src: [
    { path: '../node_modules/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2', weight: '400', style: 'normal' },
    { path: '../node_modules/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2', weight: '500', style: 'normal' },
  ],
  variable: '--font-mono',
  display: 'swap',
  fallback: ['ui-monospace', 'Menlo', 'monospace'],
});
