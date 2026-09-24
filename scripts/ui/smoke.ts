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
import { chromium, type BrowserContext, type Page, type Request } from 'playwright';

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
  /** An element that must not be on the page. */
  absent?: string;
};

const failures: string[] = [];

/**
 * How long a page gets to go quiet after `load`, and what counts as slow.
 *
 * Pages are not awaited with Playwright's `networkidle`. In a production
 * build Next.js prefetches every link in view, so one prefetch that never
 * settles holds the network open and fails the page with a bare 30 s
 * timeout that names nothing. That happened once: .gitignore kept
 * app/coverage/ out of the repository, the nav's prefetch of /coverage never
 * completed in CI, and the home page timed out. Instead each page waits for
 * its own requests to settle, up to a cap, and anything still pending or slow
 * is printed by URL, which is how that cause was found.
 */
const SETTLE_MS = 10_000;
const SLOW_MS = 3_000;
const inFlight = new Map<Request, number>();
const slow: string[] = [];

function trackRequests(context: BrowserContext): void {
  context.on('request', (request) => inFlight.set(request, Date.now()));
  const done = (request: Request) => {
    const started = inFlight.get(request);
    if (started === undefined) return;
    inFlight.delete(request);
    const ms = Date.now() - started;
    if (ms > SLOW_MS) slow.push(`${ms} ms  ${request.method()} ${request.url()}`);
  };
  context.on('requestfinished', done);
  context.on('requestfailed', done);
}

/** Load a page, then let its requests settle. Null if it would not load. */
async function open(page: Page, path: string, fail: (what: string) => void) {
  try {
    const response = await page.goto(`${APP_URL}${path}`, { waitUntil: 'load' });
    const deadline = Date.now() + SETTLE_MS;
    while (inFlight.size > 0 && Date.now() < deadline) await page.waitForTimeout(100);
    if (inFlight.size > 0) {
      console.warn(`  still in flight ${SETTLE_MS} ms after loading ${path}:`);
      for (const request of inFlight.keys()) console.warn(`    ${request.method()} ${request.url()}`);
    }
    return response;
  } catch (error) {
    fail(`did not load: ${error instanceof Error ? error.message.split('\n')[0] : error}`);
    return null;
  }
}

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
  const mappable = await firstRow<{ id: string }>(
    'facts',
    'sites?select=id&lat=not.is.null&lng=not.is.null&limit=1',
  );
  if (!mappable) {
    // Said on every run, not buried in a comment: the map component is where
    // the Phase 1 crash lived, and it is only drawn once a site has
    // coordinates. No coordinates are invented to force it.
    console.warn(
      'Note: no site has coordinates, so the map itself is not drawn or tested. ' +
        'It will be once the pipeline loads coordinates.',
    );
  }

  // The load asserts that every blank carries a gap record, so a page showing
  // an unexplained blank has lost gaps on the way, most likely to an unpaged
  // read truncated at the 1000-row limit.
  const UNEXPLAINED = '[data-unexplained]';

  const list: Check[] = [
    { path: '/', status: 200 },
    { path: '/coverage', status: 200, absent: UNEXPLAINED },
    { path: '/list?sort=capacity&dir=desc', status: 200, absent: UNEXPLAINED },
    { path: '/list?status=approved&sort=council', status: 200 },
    // A stale or hand-edited link still shows the index rather than failing.
    { path: '/list?sort=price&status=imagined&council=Nowhere', status: 200 },
    { path: '/essays', status: 200 },
    // The map is drawn in the browser, so a 200 alone does not show it
    // worked. With no coordinates recorded there is nothing to plot, and the
    // page must say so without loading a map at all.
    mappable
      ? { path: '/map', status: 200, selector: '.leaflet-container' }
      : { path: '/map', status: 200, selector: 'text=nothing to plot', absent: '.leaflet-container' },
    { path: '/list', status: 200, absent: UNEXPLAINED },
    { path: `/sites/${site.id}`, status: 200, title: site.name, absent: UNEXPLAINED },

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

  const response = await open(page, check.path, fail);
  if (!response) {
    page.off('pageerror', onError);
    console.log(`FAIL ${check.path}`);
    return;
  }
  const status = response.status();
  if (status !== check.status) fail(`expected ${check.status}, got ${status}`);

  const title = await page.title();
  if (check.title && !title.includes(check.title)) {
    fail(`title "${title}" does not include "${check.title}"`);
  }
  if (check.titleExcludes && title.includes(check.titleExcludes)) {
    fail(`title "${title}" names an unpublished record`);
  }

  // Waited for, not counted: a client-rendered element such as the map
  // arrives after `load`, once its code has been fetched and run.
  if (check.selector) {
    const found = await page
      .locator(check.selector)
      .first()
      .waitFor({ timeout: 15_000 })
      .then(() => true)
      .catch(() => false);
    if (!found) fail(`nothing matches ${check.selector}`);
  }
  if (check.absent && (await page.locator(check.absent).count()) > 0) {
    fail(`found ${check.absent}, which should not be there`);
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

/**
 * The timeline's track boxes: a press shows at once, the URL follows, and the
 * last selected track cannot be unticked (which used to re-select all six).
 */
async function timelineTracks(page: Page): Promise<void> {
  const fail = (what: string) => failures.push(`/ timeline tracks: ${what}`);
  if (!(await open(page, '/', fail))) return;

  // The press has to land after hydration: before it, the box is plain HTML
  // and toggles without React, which is not what is under test.
  const hydrated = await page
    .waitForFunction(
      () => {
        const box = document.querySelector('fieldset input[type=checkbox]');
        return box !== null && Object.keys(box).some((k) => k.startsWith('__reactFiber'));
      },
      undefined,
      { timeout: 15_000 },
    )
    .then(() => true)
    .catch(() => false);
  if (!hydrated) {
    fail('the track checkboxes never hydrated');
    return;
  }

  const boxes = page.getByRole('group', { name: 'Event tracks' }).getByRole('checkbox');
  const names = await boxes.evaluateAll((els) =>
    els.map((el) => el.parentElement?.textContent?.trim() ?? ''),
  );
  if (names.length < 2) {
    fail(`expected the track checkboxes, found ${names.length}`);
    return;
  }

  const first = page.getByLabel(names[0]!, { exact: true });
  await first.click();
  if (await first.isChecked()) fail('a press did not change the box until the server answered');
  await page.waitForURL(/tracks=/);

  for (const name of names.slice(1, -1)) {
    await page.getByLabel(name, { exact: true }).click();
    await page.waitForFunction(
      (n) => !new URLSearchParams(location.search).get('tracks')?.includes(n.toLowerCase()),
      name,
    );
  }
  const last = page.getByLabel(names.at(-1)!, { exact: true });
  if (!(await last.isChecked())) fail('the last track should still be selected');
  if (!(await last.isDisabled())) fail('the last selected track can be unticked');

  console.log(`${failures.some((f) => f.startsWith('/ timeline')) ? 'FAIL' : 'ok  '} timeline tracks`);
}

/**
 * A map point opens its popup, which names the site, states each field or its
 * gap, and links to the full record. Runs only once some site has coordinates;
 * axe runs again with the popup open, since it is not in the page until then.
 */
async function mapPopup(page: Page): Promise<void> {
  const fail = (what: string) => failures.push(`/map popup: ${what}`);
  const mappable = await firstRow<{ id: string }>(
    'facts',
    'sites?select=id&lat=not.is.null&lng=not.is.null&limit=1',
  );
  if (!mappable) return;
  if (!(await open(page, '/map', fail))) return;

  const point = page.locator('.leaflet-interactive').first();
  const drawn = await point
    .waitFor({ timeout: 15_000 })
    .then(() => true)
    .catch(() => false);
  if (!drawn) {
    fail('no map point was drawn');
  } else {
    await point.click({ force: true });
    const popup = page.locator('.leaflet-popup');
    const opened = await popup
      .waitFor({ timeout: 5_000 })
      .then(() => true)
      .catch(() => false);
    if (!opened) {
      fail('clicking a point opened no popup');
    } else {
      if ((await popup.getByRole('link', { name: 'Full site record' }).count()) === 0) {
        fail('the popup has no link to the site record');
      }
      const { violations } = await new AxeBuilder({ page }).withTags(WCAG_TAGS).analyze();
      for (const v of violations) fail(`axe ${v.impact ?? ''} ${v.id} with the popup open`);
    }
  }
  console.log(`${failures.some((f) => f.startsWith('/map popup')) ? 'FAIL' : 'ok  '} map popup`);
}

async function main(): Promise<void> {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || undefined,
  });

  try {
    for (const width of [1280, 390]) {
      console.log(`\nViewport ${width}px`);
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      trackRequests(context);
      // Map tiles are a third-party service with a usage policy, and they are
      // not what is under test. Refusing them keeps CI off OpenStreetMap.
      await context.route('**/tile.openstreetmap.org/**', (route) => route.abort());
      const page = await context.newPage();
      if (width === 1280) {
        await timelineTracks(page);
        await mapPopup(page);
      }
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

  if (slow.length > 0) {
    console.warn(`\n${slow.length} request(s) took longer than ${SLOW_MS} ms:`);
    for (const line of slow) console.warn(`  ${line}`);
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
