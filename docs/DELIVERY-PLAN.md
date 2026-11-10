# DELIVERY-PLAN.md

Status: proposed 2026-11-10, awaiting the author's go-ahead. Nothing in it is
built yet. It turns the author's answers to ten scoping questions into four
releases: site polish and a CMS, essays, research on how the industry shapes
the narrative, and the "What if…?" policy pages.

## Context

The observatory is built and loaded: 93 sites, 248 sources, 94 research
questions and 19 cited story cards in `editorial/stories/`. Three things are
missing:

- **The site looks like a scaffold.** It uses system fonts and one narrow
  column, has no dark mode and no mobile menu, has no loading states, and shows
  developer setup text to the public (`components/NotConnected.tsx`).
- **There is nowhere to write or publish essays.** `editorial.essays` is empty.
  Nothing can write to it (`0012_service_role_read.sql` grants SELECT only),
  sign-in is off, and bodies render as plain text (`app/essays/[id]/page.tsx:71`).
- **The research has stalled.** Every batch an agent can do is done (Batches
  0–5). Of the 94 questions, 20 are resolved and 35 wait on FOI, GIPA, paid
  searches or browser downloads. Nothing yet covers what the author most wants
  to show: how politicians and lobbyists shape the narrative.

The aim is a resource for **journalists and researchers first**. It has a
neutral, cited record; a clearly separate editorial layer of essays; a
"Where we stand" page; and a "What if…?" section setting out a pro-human model
for Australian data centres.

## Decisions from the author (10 questions, 2026-11-10)

| # | Question | Answer |
| --- | --- | --- |
| 1 | Primary reader | Journalists and researchers |
| 2 | Stance | Neutral record, labelled opinion, plus a "Where we stand" page |
| 3 | What if | One page per proposal: Australian rules now (cited), overseas precedent (cited), the argument (labelled opinion) |
| 4 | Narrative evidence | All four: who met whom, money to parties, claims against the record, inquiry submissions |
| 5 | CMS | Hybrid: agent drafts go into git and load as unapproved rows; the author edits and approves at a private `/admin` |
| 6 | Drafting | Full essay drafts by the agent. The author edits and approves |
| 7 | Legal | Institutions only. People appear by role until legal review is arranged |
| 8 | Human steps | The author does the 21 free downloads (`docs/requests/DOWNLOADS.md`). No FOI, GIPA or paid searches for now |
| 9 | Look | Editorial magazine for essays; record pages stay dense |
| 10 | First release | Foundation plus the first essay. The rest rolls out in batches |

## Hard-rule handling (CLAUDE.md)

- **No agent publishes.** Unchanged. Agents write drafts. Approval is a
  database function: it takes the approver from the signed-in editor's token,
  accepts no approver argument, and cannot be executed by `anon` or
  `service_role`. No agent ever holds editor credentials.
- **Rule changes the author has chosen.**
  - `docs/SUBAGENTS.md` writer_support says "Never final prose". It becomes
    "agents draft in full; only the author approves".
  - `docs/UX.md` step 4 "Draft (human author)" and `docs/UX-PLAN.md:47`
    "No new CMS" are updated to match.
  - `supabase/config.toml` says "no public sign-in". That stays true:
    `enable_signup=false`, and the one editor is invited.
- **An existing leak gets fixed.** `0004_rls.sql:45-46`
  (`citations_public_read using (true)`) lets the public read citation rows of
  unapproved essays. Once drafts exist, it must only serve citations whose
  parent record is visible.
- **People are kept out.** The pipeline's `lobbying.person` column
  (`data-pipeline/schema/01_schema.sql:763`) holds named individuals, and so
  do some `notes` fields. The loader never publishes either, and the new
  influence tables have no column for a person's name.
- **Inference stays out.** Matching a donor to a company is a *proposed* link
  that a human confirms. A claim-vs-record verdict is editorial: it goes in an
  `editorial` table behind approval, never in `facts`.
- **Conflict of interest.** The drafting agent is Claude, made by Anthropic, and
  Anthropic is the Western Downs tenant (ST-016, RG-012). `/about` carries a
  standing disclosure. Any piece touching ST-016, RG-012 or frontier labs
  carries it at the top, and the checker enforces this.

---

## Release 1: foundation and the first essay (four PRs on `claude/bold-goldberg-0ek4ml`)

### PR 1: design system and site shell (UX-PLAN Phase 0, G1–G3)

**Fonts and tokens**
- Self-hosted fonts via `next/font/local` in `app/fonts/` (OFL licences
  committed, so the build fetches nothing):
  - **Newsreader** (serif, optical sizes) for headlines and essay body text;
  - **Inter** (tabular figures) for interface text and record pages;
  - **IBM Plex Mono** for record ids.
- New `lib/design/tokens.ts` is the single source of the tokens:
  - fact, editorial, gap and a new `defect` colour (replacing the raw `red-*`
    classes in 4 files), each in light and dark;
  - a six-colour, colour-blind-safe timeline track palette (G2);
  - type scale (display, title, heading, body, essay, meta), spacing, focus
    ring and motion.

  `tailwind.config.ts` exposes the tokens as CSS variables, with
  `darkMode: 'media'`. `app/globals.css` sets `color-scheme: light dark`.
  `tests/tokens.test.ts` asserts at least 4.5:1 contrast for every ink/wash and
  text/surface pair, in both modes.

**Layout and navigation**
- `Container` (record, essay and wide widths) and `PageHeader` (kicker, title,
  standfirst, DateStamp). These fix the inconsistent h1/h2 sizes.
- `components/PrimaryNav.tsx` splits into two labelled groups, so the two
  layers show in the navigation:
  - **The record**: Map, Sites and entities, What's known, Open questions;
  - **Analysis**: Essays, What if…?
- A disclosure menu below `md`, with touch targets of at least 44px.
- Footer: About, Where we stand, How to read, Data.

**Shared components and fixes**
- `EventItem` replaces the three copies (`app/page.tsx:293`,
  `app/sites/[id]/page.tsx:169`, `app/entities/[id]/page.tsx:117`).
- A `.link` class replaces about 40 repeated link class strings.
- `FieldRow`/`FieldList`, `Breadcrumb` and `EmptyStateMessage`.
- `loading.tsx` for root, map, list, sites and research.
- `NotConnected` says "The record is temporarily unavailable" to the public;
  the setup steps show only in development.
- `SourcePanel`:
  - heading ids from `useId`;
  - per-entry `id="source-n"` anchors;
  - "(opens in a new tab)" for screen readers.
- `GapBadge`: pass `sourceHref`.
- Checkboxes: `accent-fact-ink`.
- `SiteMap`: responsive height, and the marker colour comes from the token.

**Site metadata**
- `app/icon.svg`, `opengraph-image.tsx` (labelled "Record" or "Essay ·
  Opinion"), `metadataBase` from `SITE_URL`.
- `app/robots.ts` (blocks `/admin`) and `app/sitemap.ts`.

### PR 2: CMS (database, auth, admin)

**Migrations**
- **`0014_editor_auth.sql`**
  - `editorial.editors(email)` allow-list. RLS on, no grants. The row is
    inserted by hand and the email is never committed.
  - `editorial.is_editor()` (SECURITY DEFINER, `search_path=''`) checks the
    token's email against the allow-list.
  - `editorial.approvals` audit log.
- **`0015_essay_fields.sql`**
  - `editorial.essays` gains:
    - `kind` (`essay | position | proposal`), `slug`, `standfirst`;
    - `data_as_of_date` (UX.md requires both dates);
    - `conflict`, `named_parties`, `story_cards`, `proposal_no`;
    - provenance: `source_file`, `source_sha256`, `edited_in_admin_at`,
      `last_edited_by`.
  - An approved row must have a `data_as_of_date`.
  - `editorial.essay_revisions` snapshots the body on every update.
  - Reuse the essays table rather than add a pages table: one approval gate,
    one RLS surface, one citation enum.
- **`0016_essay_citations.sql`**
  - A trigger on the body:
    - extracts the `[SRC_X]` markers;
    - resolves them against `facts.sources.pipeline_id`;
    - rewrites the essay's `facts.citations` rows;
    - **rejects the save on any unknown id**.
  - Replace `citations_public_read` so that editorial citations are visible
    only when their parent row is.
- **`0017_editor_rls.sql`**
  - The editor (signed in as `authenticated` and passing `is_editor()`) may
    read everything and insert/update unapproved rows.
  - A column-level UPDATE grant leaves out `approved_*`.
  - `editorial.approve_essay(id, publish_date, expected_updated_at, legal_ack)`:
    - requires the editor, the row unchanged since it was loaded, at least 5
      distinct cited sources, the opinion heading, and `legal_ack` when
      `named_parties` is not empty;
    - sets `approved_by` from the token's email and `approved_at = now()`;
    - logs the approval.
  - `retract_essay`.
  - EXECUTE on both functions for `authenticated` only.
  - The new tables go into `lib/backup/tables.ts`.

**Auth**
- `lib/supabase/editor.ts` builds a `@supabase/ssr` `createServerClient` from
  cookies (httpOnly; no browser client).
- `middleware.ts` gates `/admin/:path*` as an early rejection; the database
  check is the real authority.
- Magic-link sign-in at `/admin/sign-in` with `shouldCreateUser:false`. The
  reply is always the same, so it does not reveal which addresses are allowed.
- `/admin/auth/callback` completes the sign-in.
- `noindex` and `no-store` on every admin page. The `service_role` key is
  never imported under `app/`.

**Editor pages**
- `/admin` lists drafts and published pieces.
- `/admin/essays/[id]`:
  - a Markdown textarea with a live preview, rendered by the same components
    as the public page;
  - a checker panel running the shared rules;
  - Save (optimistic lock), Approve (publish date, legal acknowledgement) and
    Retract;
  - the revision diff.
- Approve and Retract call `revalidateTag(RECORD_CACHE_TAG)`.

### PR 3: rendering, checker and loader

**Rendering**
- Markdown with `react-markdown` + `remark-gfm`, with raw HTML off, an element
  whitelist, and links limited to http(s) and internal paths.
- Pure, unit-tested remark plugins in `lib/editorial/markdown/`:
  - `[SRC_X]` becomes a numbered `InlineCitation` linking to `#source-n`;
  - `> [!PULLQUOTE]` and `> [!FIGURE] value | caption [SRC_X]` become callouts.

**Essay page redesign** (`app/essays/[id]/page.tsx`, plus `/essays/[slug]`)
- Hero:
  - kicker, Newsreader display title, standfirst;
  - DateStamp with the publish date and the data-as-of date;
  - a conflict box when one applies.
- YouTube embed and a sticky `SectionNav`.
- `PullQuote` and `FigureCallout`: fact styling before the divider, editorial
  styling after it.
- `FactOpinionDivider` before "Our view".
- Related sites and events from `related_ids` (UI.md:50).
- A "Cite this page" `CitationChip` on essay, site and entity pages.
- A print stylesheet.

**Draft file format** (`editorial/essays/ES-nnn-slug.md`, documented in a new
`README.md`)
- Front matter mirrors the table, plus `story_cards`, `questions` and
  `sources`. Any `approved_*` key is forbidden.
- Sections by kind:
  - **essay**: The common perception, What the records show, Where the data is
    too thin, What to watch next, Our view;
  - **proposal**: Australia's rules now, Elsewhere, What it would take, Our
    proposal;
  - **position**: Our view, plus an optional cited "What it rests on".

**Checker** (`lib/editorial/rules.ts`, shared by the CLI and the admin panel;
helpers factored out of `scripts/editorial/story-cards.ts`;
`scripts/editorial/essays.ts`; `tests/essays.test.ts`)
- Every block before the opinion heading cites a source.
- Every number is cited.
- At least 5 distinct sources.
- The declared sources equal the cited ones.
- Story cards and question ids exist.
- A conflict disclosure where ST-016, RG-012 or Anthropic is touched.
- A **name screen**: personal names drawn at check time from the pipeline
  (never committed as a list).

**Loader** (`scripts/editorial/load-essays.ts`, `npm run load:essays`)
- Emits a reviewed SQL artefact of draft rows only, with ids from
  `uuidV5('essay:ES-nnn')`.
- Upserts only `where approved_at is null and edited_in_admin_at is null`.
- Asserts that no loaded row is approved.
- `load-pipeline.ts` is unchanged, and its "touched no editorial" test stays.
- **Which copy wins:** once the author edits a draft in `/admin`, the database
  row is the source of truth. The git file stays as the agent's proposal, for
  audit. A later agent revision of an edited draft is skipped and reported,
  never merged automatically.

### PR 4: content (all drafts; the author approves)

- **ES-001 "Six in seven"** (flagship, from ST-011, line M4).
  - The clearest case of how the narrative is made: an industry-commissioned
    figure travelled through peak bodies into NSW guidelines without
    disclosure.
  - Every party is an institution, and the people involved appear only by
    role.
  - It has 8 sources, needs no downloads, and fits the four-part essay
    structure in `docs/UX.md:179-181`.
- **ES-000 "Where we stand"** (`kind=position`, `/where-we-stand`).
  - Drafted close to the author's own words.
  - Factual premises are cited or worded as opinion. "Frontier labs are
    desperate for cash and compute" needs a source or opinion phrasing.
- **`/about`.** Method, the conflict disclosure and corrections. A static page
  with no figures.

### What the author does to ship Release 1
1. Apply migrations 0014–0017 to the hosted database.
2. Insert your editor email into `editorial.editors`.
3. In Supabase Auth, set the redirect URLs (production and deploy previews) and
   custom SMTP.
4. Set `EDITOR_EMAIL` and `SITE_URL` on Netlify.
5. Apply the essay load artefact.
6. Read, edit and approve in `/admin`.

---

## Release 2: data utility, downloads and the first essay batch

**Data for journalists (UX-PLAN E2)**
- `app/data/{sites,entities,sources,research}.csv/route.ts` on a new
  `lib/csv.ts`:
  - formula-injection guard;
  - a `<field>_gap` column instead of a blank;
  - unit tests.
- A `/data` page with the licence (the author decides which) and an as-of date.
- A `/case-studies` index, and essay links on site pages (D1).

**Downloads** (the author saves each file to the folder `DOWNLOADS.md` names)
- New `data-pipeline/scripts/manifest.py <file> --url …` writes the
  `.meta.json` beside it.
- The agent then works each download: hunt log, pack, rebuild, card update,
  `load:pipeline` artefact.
- Order:
  1. 8–10 (diaries, lobbyist registers: RG-070, RG-077), which strengthen
     ES-001;
  2. 1–3 and 6 (super and Future Fund: RG-004, RG-094);
  3. 17–18 (inquiries: RG-015, 016, 041, 066);
  4. 15 (RG-012);
  5. 13, 14 and 16 (C3);
  6. 7 (RG-005);
  7. 11 (RG-074);
  8. 19–21 (C1).
- Download 4 (ASX) needs your decision on ASX's terms first.

**Parked questions (Batch 7)**
- Triage all 34 parked questions.
- Power and water go first (RG-008, 010, 017, 018, 019, 042, 044, 045), because
  they feed What-if proposals 2 and 4.
- Questions blocked only by FOI, GIPA or paid searches stay open and say so;
  nothing is guessed.

**Essays**
- ES-002, M2 "Already in your super", after downloads 1–3 and 6.
- ES-003, M1 "Who is really applying" (ST-003 to ST-006).
- ES-004, M3 "What the public gives" (ST-009, ST-010).

**Docs.** `docs/RESEARCH-PLAN.md` gets corrected counts (20/42/32), Batch 5
marked merged, and Batches 6 and 7 added.

## Release 3: how the industry shapes the narrative

**Upstream** (`data-pipeline/schema/03_influence.sql`)
- New `donations` and `statements` tables.
- A role-only `actor_role` on `lobbying`.

**Migrations**
- `0018` adds the `citable_record` values first, as a separate migration (the
  0013 lesson).
- `0019` adds:
  - `facts.influence`: actor and lobbyist entity, office such as "NSW Minister
    for Planning", channel, date, instrument, position quote;
  - `facts.donations`: donor entity (nullable), donor name as disclosed,
    party, jurisdiction, financial year, amount (a gap when withheld);
  - `facts.statements`: speaker office, venue, date, verbatim quote.

  None of them has a column for a person's name.
- `0020`: `editorial.claim_checks` (the verdict, behind approval).

**Loader**
- `lib/ingestion/transform.ts` and `vocabulary.ts`: `person` and `notes` are
  never published.
- The name screen rejects rows.
- Donor-to-company matches load as proposed links.

**Parsers** for manually collected exports (pure, no network, following
`scripts/ingestion/parse-capacity-csv.ts`)
- NSW and Commonwealth lobbyist registers, NSW ministers' diaries, AEC and
  state donation returns, inquiry submissions.
- Fixtures and unit tests for each.
- Individual donors are counted and dropped.

**SPEC and questions**
- `docs/SPEC.md` gains a "Manually collected sources" table for you to approve.
  No scrapers.
- New questions from RG-101:
  - lobbyist clients;
  - donations by operators, parents and landholders;
  - property-developer donation bans;
  - quantified ministerial claims against the record;
  - government-cited figures commissioned by industry;
  - inquiry asks by company.
- The revolving door is deferred until legal review, because it is about
  people.

**UI**
- `ClaimVsRecord` (UX-PLAN D3): the statement in fact styling, the records
  beside it, the verdict in editorial styling.
- `/influence` with Meetings, Registers, Donations and Submissions.

**Essays**
- ES-005, C1 "Who gets heard".
- ES-006, C2 "Did anyone check" (roles only).
- ES-007, a follow-up on who met whom.

## Release 4: What if…? and the remaining essays

**Data**
- `0021`: `facts.instruments` (laws and policies, Australian and overseas), each
  sourced before anything is said about it.
- Candidate precedents to verify: Singapore's moratorium and its green data
  centre pilot, Ireland's grid-connection policy, Germany's Energy Efficiency
  Act (PUE and renewables), Dutch hyperscale limits, Article 12 of the EU
  Energy Efficiency Directive, Frankfurt zoning.

**Pages**
- `/what-if` and `/what-if/[slug]`: five `kind=proposal` pieces, one per
  proposal, each with a precedent table.
- Each proposal is stress-tested against the record, as in `findings_memo.md`
  §7. For example:
  - design WUE in NSW environmental impact statements already averages about
    1.0;
  - the binding water failure is recycled-water infrastructure sequencing (S7);
  - recycled water and demand response are already partly NSW policy.

  Those parts are framed as enforcement and quantification, which strengthens
  the case rather than weakening it.
- Proposal 5 (First Nations governance): consider First Nations consultation
  before you approve it.

**Essays**
- ES-008, M5 "The OpenAI deal".
- ES-009, C3 Palantir and sovereignty.
- ES-010, C3 "The tenant", with the Anthropic disclosure prominent.

---

## Documents to update (in the PR that changes the behaviour)
- **`CLAUDE.md`**: stack (Supabase Auth, one invited editor), layout
  (`editorial/essays`, `middleware.ts`), rules (agents draft and only the author
  approves; people by role until legal review), review dates.
- **`docs/SUBAGENTS.md`**: writer_support, reviewer and researcher roles.
- **`docs/UX-PLAN.md`**: status table and decision #6. **`docs/UX.md`**: essay
  steps 3–4.
- **`docs/SPEC.md`**: essay columns, the citation trigger, influence tables,
  manual-source table.
- **`docs/REVIEW.md`**: conflict disclosure, roles only, `/admin` gating, editor
  RLS tests.
- **`docs/DEPLOYMENT.md`** and **`docs/SUPABASE_SETUP.md`**: env vars, redirect
  URLs, SMTP, allow-list SQL.
- **Also**: `.env.example`, `README.md` (migration count, routes),
  `editorial/essays/README.md`.

## Verification
- **`npm run lint`, `npm run typecheck`, `npm test`.** New tests cover token
  contrast, CSV, essay rules, the remark plugins, the essay loader's output,
  the parsers and the nav.
- **`npm run test:rls`.** First add `auth.jwt()`/`auth.uid()` stubs to
  `scripts/test-rls.sh` (and to the load and UI scripts). Then assert:
  - **anon:** the existing self-publish refusals still pass; anon cannot see
    the citations of an unpublished piece.
  - **non-editor:** cannot read, update or approve.
  - **editor:**
    - can update a draft;
    - gets error 42501 writing `approved_by`;
    - cannot edit an approved row;
    - is refused approval with fewer than 5 sources;
    - an approval records the editor's email.
  - **service_role:** cannot execute `approve_essay`.
  - **citation trigger:** rejects an unknown `SRC_` id.
- **`npm run test:load`.** Apply the essay artefact after the pipeline load and
  assert:
  - drafts stay unapproved;
  - citations are derived;
  - rows edited in admin are skipped.
- **`npm run test:ui`.**
  - Add `/about`, `/where-we-stand`, `/admin/sign-in` and `/data`.
  - Approve a fixture essay in the test database.
  - Run axe in light and dark.
- **`npm run build`** with no credentials.
- **By hand, on a Netlify deploy preview:**
  - magic-link sign-in, edit, preview, approve, the essay live at once,
    retract;
  - the phone menu;
  - dark mode on the map;
  - a screen-reader pass over the inline citations;
  - print.
