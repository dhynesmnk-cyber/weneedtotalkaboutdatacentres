/**
 * The site's identity and public address.
 *
 * The masthead names the publication; the strapline says what kind of thing
 * it is. Record pages keep their neutral labels beneath it.
 */

export const SITE_NAME = 'We need to talk about data centres';
export const SITE_STRAPLINE = 'An observatory of Australian AI data centres';
export const SITE_DESCRIPTION =
  'A public record of Australian AI data centre sites, the entities behind them, '
  + 'and what is known and not known about each, with essays kept separate from the record.';

/**
 * The absolute base URL, for canonical links, Open Graph images and the
 * sitemap. `SITE_URL` is set per deployment; Netlify supplies `URL` for the
 * production site and `DEPLOY_PRIME_URL` for previews.
 */
export function siteUrl(env: Record<string, string | undefined> = process.env): URL {
  const raw = env.SITE_URL || env.DEPLOY_PRIME_URL || env.URL || 'http://localhost:3000';
  try {
    return new URL(raw);
  } catch {
    return new URL('http://localhost:3000');
  }
}
