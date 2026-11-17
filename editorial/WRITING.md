# Writing guide

How essays and story cards for *We need to talk about data centres* are written.
Agents draft from this guide. The author edits and approves at `/admin`.

This guide adapts a writing brief the author built for another publication, at
the author's direction of 2026-11-17. The evidence rules, the dry tone, the
analogy ration, the bans and the self-check carry over unchanged in substance.
Five things are changed for this site:
- **Voice.** The site writes as "we", not "I".
- **Author.** There is no author biography.
- **Readers.** Journalists and researchers come first.
- **Structure.** The skeleton fits the essay sections the checker already
  enforces.
- **Ending.** The paste-ready ending is put to an institution, not a vendor.

The project's hard rules (`CLAUDE.md`) sit above everything here. Where this
guide and a hard rule seem to disagree, the hard rule wins.

## 1. Role

We write essays and story cards for *We need to talk about data centres*, a
public observatory of Australian AI data centres with a separate editorial layer.

- **Readers.** Journalists and researchers first, then any reader who wants to
  check what they have been told (docs/DELIVERY-PLAN.md, decision 1).
- **The promise.** The site sets what the public is told against what the
  public record shows. It judges a data centre deal, a policy or a claim on
  the evidence, as it would any other use of public land, power, water or
  money.
- **Who decides.** Agents draft in full. Only the author approves, and
  approval is the publication step (`CLAUDE.md`). Add nothing about the author
  beyond what a page already says.

## 2. Voice

One voice, two parents.

- **The spine is investigative.** Exact numbers. Dated, verbatim quotes. A
  company's, department's or minister's own words turned into evidence. A blunt
  claim up front. Explicit honesty where the evidence runs out.
- **The delivery is a warm, curious explainer.** Address one smart reader who
  has never opened a planning document. Walk the mechanism in sequence, keep
  momentum, and answer the reader's next question before they ask it.

We are on the reader's side against spin and sloppy evidence, whoever it comes
from: industry, government or consultants. Never against the reader.

Write in the first person plural: "we", "our records", "this observatory". The
record pages stay neutral, because they are data.

## 3. Heat: dry bite (fixed)

Contempt is carried by the dated quote, never stated by the writer.

> Model line: "The NSW rules call it 'phantom demand'. The briefing's own page,
> dated 21 November 2025, says AWS commissioned it."

- **Banned:**
  - profanity;
  - mockery of anyone, and in any case no person by name (section 8);
  - telling readers they are being robbed;
  - adjectives doing the work of evidence ("shameless", "staggering").
- **Cut emotion the evidence already proves.** If a sentence states an
  emotion the evidence already proves, cut the sentence and keep the evidence.

## 4. Evidence rules (non-negotiable)

1. **Invent nothing.** Never invent or alter a quote, date, price, percentage,
   clause or condition number, project name or statistic. Use only material the
   research database holds, cited by its source id: `[SRC_ID]`. A claim that
   cannot be cited is cut, not softened into an uncited one.
2. **Every quote is verifiable.**
   - It is verbatim and dated.
   - It is attributed to an institution, or to a person by their public role.
   - It is located, so a reader can verify it in two minutes. The citation
     links to the source record, which holds the document, its archive and the
     quoted passage.
   - In the text, a condition or clause number may be named ("condition B20")
     when the reader needs it. Page numbers, file formats and error codes stay
     in the hunt log and the source record.
3. **Prices and percentages.** They appear as before and after, each with its
   date and source, never as a bare percentage.
4. **Three registers, kept apart:**
   - what the records show, in the record sections;
   - what we infer, marked "our read";
   - what we cannot know, in "Where the data is too thin".

   Where evidence runs out, say so plainly and stop.
5. **Their language is evidence, not vocabulary.** A company's, department's or
   industry body's own language is quoted and dated, never adopted. "Phantom
   demand", "sovereign capability" and "AI factory" appear in quotation marks,
   with their source.
6. **Predictions.** State the basis and hedge explicitly, or decline to predict.
7. **Shorten, never pad.** If the evidence cannot support the claim, weaken the
   claim or shorten the piece.
8. **Gaps stay gaps.** A missing value is a gap, never an inference. Never fill
   one figure from a neighbouring one that looks similar: an IT load is not a
   site total, and a contract is not a capacity.

## 5. Analogy rules

At most one analogy per concept. It must do explanatory work:

1. It maps at least two specific details onto the mechanism.
2. The reader can draw a correct inference from it, which the literal steps
   then confirm.
3. **Deletion test.** If removing it loses only flavour, cut it.
4. Follow it at once with the literal, plain-language sequence of what happens.
   No metaphors inside that sequence.
5. If the analogy breaks at a point that matters to the argument, say where.

**Model.** A consent condition that must be met "prior to the commencement of
operation" works like the final inspection on a new house. The builder can
finish every room, but nobody moves in until the inspector signs off.
- **The literal sequence.**
  1. The consent lets the applicant build.
  2. One condition requires that, before the data centre operates, the
     applicant must show the Planning Secretary that all its electricity is
     matched by firmed renewable supply [SRC_NSWPORTAL_CONSENTS].
  3. Until the Secretary is satisfied, it may not operate.
- **Where it breaks.** An inspector walks through the house. The record does
  not show how the Department checks the evidence it is given, or whether it
  does [RG-061].

**Banned:**
- decorative labels ("the gold rush of the cloud");
- an analogy in the opening claim or in "Our view";
- stacked analogies.

## 6. Structure

**Two tiers, one skeleton.**
- **The brief** is the default: 600 to 1,000 words, one claim, one company,
  deal or mechanism.
- **The deep dive** runs 2,000 to 3,500 words. Use it only when the essay's
  plan asks for one and the evidence supports it. Otherwise write the brief and
  say in the pull request why.

The checker enforces the essay sections (editorial/essays/README.md). The
skeleton fits inside them:

| Skeleton | Where it goes |
| --- | --- |
| **Headline**: a blunt, defensible claim, never a question | `title` |
| **Standfirst**: the claim and the stakes in one or two sentences | `standfirst` |
| **Highlights**: three facts, with numbers or dates where the evidence has them | Up to three `> [!FIGURE]` callouts, the first one inside the opening section |
| **Opening**: the claim as the public meets it, quoted, then our claim and the stakes, inside 100 words. No warm-up, no scene-setting | `## The common perception` |
| **Evidence**: dated, verbatim quotes, figures, conditions, in short passages with plain subheads (`###`). Quote their words back at them | `## What the records show` |
| **Mechanism**: the literal sequence, with at most one rationed analogy | Inside `## What the records show` |
| **For journalists and researchers**: the records to request, the ids to cite, how to check our work. A general reader can skip it. In a brief, one paragraph | `### For journalists and researchers`, the last part of `## What to watch next` |
| **Uncertainty**: what the evidence does not show, and what would settle it, by question id | `## Where the data is too thin` |
| **Ending**: our argument, then **one paste-ready artefact** (see below), then stop | `## Our view` |

The paste-ready artefact is something a reader can send under their own name.
The usual forms are:
- a question for a named institution, put in writing;
- the wording of a records request;
- a condition a reader can check;
- a number to ask for.

The institution is a minister's office, a department, a council, an operator or
a utility, addressed by role. The artefact is set as a block quote. After it,
stop: no recap and no inspirational close.

A **position** piece (`/where-we-stand`) and a **proposal** ("What if…?") keep
their own sections (editorial/essays/README.md). They follow every other part
of this guide.

**Story cards** stay raw material for the essays, in their own format
(editorial/stories/README.md): drama, not mechanics; the hunt is the story; 150
to 300 words of hunt. Sections 2 to 5, 8 and 9 of this guide apply to them too.

## 7. Signature moves (rationed)

1. **The quote-back.** Let their sentence convict them, then add at most one dry
   line. No more than two such lines per piece.
2. **Our receipts.** These are first-hand, and come only from the hunt logs and
   story cards. What we asked for, what was locked, what came back:
   - "The file was locked."
   - "The register names a company and nothing else."
   - "The exchange showed us a robot check instead of the announcement."
3. **The honest stop.** "This record does not tell you X. Here is what would."
4. **Anticipation.** Name the reader's next question, then answer it from the
   evidence.
5. **One moment of visible interest per piece.** Say why a detail matters or
   surprised us, without hype.

## 8. Integrity

- **Receipts are real or absent.** First-hand material appears only when a hunt
  log, a story card or the author's own notes supply it, and only when it does
  evidential or explanatory work. Never invent a search, a refusal, a
  conversation or an anecdote. If a piece would be stronger with one, insert
  `[AUTHOR NOTE: what would help]` and carry on. The author fills or deletes it
  in `/admin`.
- **People by role, until legal review is arranged** (`CLAUDE.md`). No person
  is named in the text, the title, the standfirst or a quote's attribution.
  Every person referred to is listed in `named_parties` with "(by role)". The
  checker refuses a personal name the research holds. It cannot catch a name
  the research does not hold, so read for that too.
- **Conflict of interest.** These pieces are drafted with Claude, made by
  Anthropic, and Anthropic is a subject of the research (RG-012, ST-016). A
  piece touching Anthropic carries the disclosure in `conflict`, and the
  checker enforces it.
- **Fact and comment stay apart.** Comment belongs in "Our view" alone. A record
  section that argues is rewritten until it only shows.

## 9. Language and bans

- **Australian English.** Plain words. Define a technical term on first use in
  one sentence.
- **Sentence work.** Short sentences carry claims; longer ones carry mechanism.
- **Banned everywhere,** and the checker enforces those marked *:
  - em dashes*;
  - exclamation marks*;
  - "it's not X, it's Y" and its variants;
  - "delve"*, "landscape"*, "game-changer"*, "unlock"*, "seamless"*,
    "robust"*;
  - "in today's fast-paced world"*, "here's the thing"*, "let that sink in"*,
    "make no mistake"*, "at the end of the day"*;
  - an "imagine" or "picture this" opening*;
  - emoji;
  - industry vocabulary in our own voice: "supercharge"*, "transform"*,
    "AI-powered"*, "world-class"*, "cutting-edge"*, "future-proof"*. Each is
    allowed inside a quotation, with its source;
  - both-sides hedging when the evidence is one-sided;
  - moralising at the reader.
- **What the checker exempts, and what it misses.** It ignores quoted text,
  block quotes and capitalised words, so a quoted claim or a proper noun (the
  Digital Transformation Agency) passes. It therefore also misses a banned word
  that opens a sentence, which the review must catch.

## 10. Self-check before a pull request

Verify each of these:
- every quote is verbatim, attributed (by role), dated, and cites its source;
- every number cites its source, opinion included;
- the analogy ration and the deletion test are passed;
- the heat is dry bite;
- the headline claim is supported by the record sections alone;
- the piece ends with a paste-ready artefact;
- the word count is inside the tier. If it is over, cut commentary, not
  evidence;
- no banned pattern appears;
- the English is Australian;
- nobody is named;
- a conflict is disclosed where Anthropic is touched.

Then run `npm run check:essays` (or the card tests, for a card).

If a check fails, fix it before opening the pull request. If evidence is
missing, open no draft. Write a gap list instead, stating exactly which record
is needed, and add it to the essay's entry in docs/PUBLICATION-PLAN.md.

## Piece brief

Each essay starts from a brief, kept in its entry in docs/PUBLICATION-PLAN.md.

```text
Essay: ES-nnn, working title
Tier: brief | deep dive (and why the evidence supports it)
Claim (one sentence, the thing the records prove):
Who and what: institutions, companies, projects (people by role only)
Evidence: source ids, with the verbatim passage each is cited for
Story cards:
Our receipts (from hunt logs and cards only):
Reader action (the paste-ready artefact):
Known gaps (question ids, and what would settle each):
Conflict (does it touch Anthropic?):
Named parties (by role):
```
