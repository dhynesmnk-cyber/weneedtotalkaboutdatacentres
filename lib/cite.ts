import { formatDate } from '@/lib/format';
import { SITE_NAME, siteUrl } from '@/lib/site';

/**
 * A plain reference to a page: title, publication, both dates and the address.
 * Dates are the ones the page itself shows, so a citation never claims more
 * currency than the page does.
 */
export function pageCitation(input: {
  title: string;
  path: string;
  publishDate?: string | null;
  dataAsOfDate?: string | null;
}): string {
  const parts = [`“${input.title}”`, SITE_NAME];
  const published = formatDate(input.publishDate);
  const asOf = formatDate(input.dataAsOfDate);
  if (published) parts.push(`published ${published}`);
  if (asOf) parts.push(`data as at ${asOf}`);
  return `${parts.join(', ')}. ${new URL(input.path, siteUrl()).toString()}`;
}
