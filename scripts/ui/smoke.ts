/**
 * Browser smoke test for the public site, against real loaded data.
 *
 * The CI build deliberately runs without credentials, so every page renders
 * its "not connected" state and the code paths that draw real records are
 * never exercised. That is how the map page shipped returning a 500 for every
 * visitor once sites existed. This runs the production build against the
 * pipeline load and checks three things for each page:
 *
 *   1. the HTTP status is what it should be (a bad id is a 404, not a 500);
 *   2. the page throws no uncaught error in the browser;
 *   3. axe finds no WCAG 2.2 A or AA violation.
 *
 * Run through scripts/test-ui.sh, which sets up the database and servers.
 *
 *   APP_URL=http://127.0.0.1:3000 REST_URL=http://127.0.0.1:3200/rest/v1 \
 *     tsx scripts/ui/smoke.ts
 *
 * CHROMIUM_PATH overrides the browser binary, for machines where Playwright's
 * own download is not available. SCREENSHOT_DIR, if set, saves a full-page
 * screenshot of every page that loads.
 */
import AxeBuilder from '@axe-core/playwright';
import { chromium, type Page } from 'playwright';

const APP_URL = process.env.APP_URL ?? 'http://127.0.0.1:3000';
const REST_URL = process.env.REST_URL ?? 'http://127.0.0.1:3200/rest/v1';
const WCAG_TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];
const NIL_ID = '00000000-0000-0000-0000-000000000000';

type Check = {
  path: string;
  status: 200 | 404;
  /** Text the tab title must contain. */
  title?: string;
  /** Text the tab title must not contain. */
  titleExcludes?: string;
  /** An element that must be on the page once it has settled. */
  selector?: string;
};

const failures: string[] = [];

async function firstRow<T>(schema: string, query: string): Promise<T | null> {
  const res = await fetch(`${REST_URL}/${query}`, {
    headers: { 'Accept-Profile': schema },
  });
  if (!res.ok) throw new Error(`${query}: ${res.status} ${await res.text()}`);
  const rows = (await res.json()) as T[];
  return rows[0] ?? null;
}

async function checks(): Promise<Check[]> {
  const site = await firstRow<{ id: string; name: string }>(
    'facts',
    'sites?select=id,name&order=name&limit=1',
  );
  if (!site) throw new Error('No sites loaded. Run scripts/test-load.sh first.');

  const list: Check[] = [
    { path: '/', status: 200 },
    { path: '/essays', status: 200 },
    // The map is drawn in the browser, so a 200 alone does not show it worked.
    { path: '/map', status: 200, selector: '.leaflet-container' },
    { path: '/list', status: 200 },
    { path: `/sites/${site.id}`, status: 200, title: site.name },

    // Malformed ids used to reach Postgres and come back as a 500.
    { path: '/sites/not-an-id', status: 404 },
    { path: '/entities/not-an-id', status: 404 },
    { path: '/essays/not-an-id', status: 404 },
    { path: '/case-studies/not-an-id', status: 404 },
    { path: `/sites/${NIL_ID}`, status: 404 },
    { path: '/no-such-page', status: 404 },
  ];

  // An entity without the major flag has no public profile, and its name must
  // not leak through the page title either.
  const minor = await firstRow<{ id: string; name: string }>(
    'facts',
    'entities?select=id,name&major_flag=eq.false&limit=1',
  );
  if (minor) {
    list.push({ path: `/entities/${minor.id}`, status: 404, titleExcludes: minor.name });
  }

  return list;
}

async function run(page: Page, check: Check): Promise<void> {
  const before = failures.length;
  const fail = (what: string) => failures.push(`${check.path}: ${what}`);
  const errors: string[] = [];
  const onError = (error: Error) => errors.push(error.message);
  page.on('pageerror', onError);

  const response = await page.goto(`${APP_URL}${check.path}`, {
    waitUntil: 'networkidle',
  });
  const status = response?.status();
  if (status !== check.status) fail(`expected ${check.status}, got ${status}`);

  const title = await page.title();
  if (check.title && !title.includes(check.title)) {
    fail(`title "${title}" does not include "${check.title}"`);
  }
  if (check.titleExcludes && title.includes(check.titleExcludes)) {
    fail(`title "${title}" names an unpublished record`);
  }

  if (check.selector && (await page.locator(check.selector).count()) === 0) {
    fail(`nothing matches ${check.selector}`);
  }

  for (const message of errors) fail(`uncaught error in the browser: ${message}`);
  page.off('pageerror', onError);

  const { violations } = await new AxeBuilder({ page }).withTags(WCAG_TAGS).analyze();
  for (const v of violations) {
    const where = v.nodes.map((n) => n.target.join(' ')).slice(0, 3).join(', ');
    fail(`axe ${v.impact ?? ''} ${v.id} on ${v.nodes.length} node(s): ${where}`);
  }

  console.log(`${failures.length > before ? 'FAIL' : 'ok  '} ${status} ${check.path}`);
}

async function main(): Promise<void> {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || undefined,
  });

  try {
    for (const width of [1280, 390]) {
      console.log(`\nViewport ${width}px`);
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      // Map tiles are a third-party service with a usage policy, and they are
      // not what is under test. Refusing them keeps CI off OpenStreetMap.
      await context.route('**/tile.openstreetmap.org/**', (route) => route.abort());
      const page = await context.newPage();
      for (const check of await checks()) {
        await run(page, check);
        if (process.env.SCREENSHOT_DIR && check.status === 200) {
          const name = check.path.replace(/\//g, '_') || '_';
          await page.screenshot({
            path: `${process.env.SCREENSHOT_DIR}/${width}${name}.png`,
            fullPage: true,
          });
        }
      }
      await context.close();
    }
  } finally {
    await browser.close();
  }

  if (failures.length > 0) {
    console.error(`\n${failures.length} UI check(s) failed:`);
    for (const f of failures) console.error(`  ${f}`);
    process.exit(1);
  }
  console.log('\nAll UI checks passed.');
}

main().catch((error: unknown) => {
  console.error(error);
  process.exit(1);
});
