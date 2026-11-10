import Link from 'next/link';

export const metadata = { title: 'Not found' };

/**
 * No such page or record.
 *
 * Also what a reader sees for a record that exists but is not published: an
 * entity without the major flag, or editorial not yet approved. The page does
 * not say which, because saying "this exists but you may not see it" would
 * itself publish something.
 */
export default function NotFound() {
  return (
    <div className="space-y-4">
      <h1 className="page-title">Not found</h1>
      <p className="max-w-2xl text-slate-700">
        There is no published page at this address. If you followed a link to a
        record, it may have been removed or never published.
      </p>
      <ul className="flex flex-wrap gap-x-5 gap-y-1 text-sm">
        <li>
          <Link href="/list" className="link">
            Browse all sites and entities
          </Link>
        </li>
        <li>
          <Link href="/" className="link">
            Go to the overview
          </Link>
        </li>
      </ul>
    </div>
  );
}
