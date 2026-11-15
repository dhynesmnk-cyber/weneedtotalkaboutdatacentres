/**
 * Extract a YouTube embed URL from a stored video id.
 *
 * Accepts an id only, not a full URL, so that a pasted tracking-laden link
 * cannot end up in an iframe src. Returns null for anything that is not a
 * plausible id.
 */
export function youtubeEmbedUrl(youtubeId: string | null): string | null {
  if (!youtubeId) return null;
  if (!/^[A-Za-z0-9_-]{11}$/.test(youtubeId)) return null;
  return `https://www.youtube-nocookie.com/embed/${youtubeId}`;
}
