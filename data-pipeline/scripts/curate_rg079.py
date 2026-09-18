#!/usr/bin/env python3
"""
RG-079: the determination layer for the 20 signed NSW data centre consents.

Inputs (all archived, offline):
  * exports/nsw_planning/nsw_dc_consent_conditions.csv - the battery, regenerated 2026-09-18
    from pypdf extractions of the sha256-verified consent PDFs (scripts/reextract_consents.py +
    scripts/consent_condition_audit.py --offline). Carries the cover-page execution block per
    instrument: determination date, signatory, delegation, file reference.
  * exports/nsw_planning/reextraction_report.json - per-document parse detail.
  * data/raw/nsw_planning/nodes/*.json - portal node metadata (field_date_of_determination_mp,
    field_determination_authority) - the registration date, which can lag the signing date.
  * data/raw/nsw_planning/planner_assignments.json - case officer per project (63 slugs).

Outputs:
  * exports/nsw_planning/nsw_dc_consent_determinations.csv - WHO decided WHAT, WHEN, UNDER WHICH
    DELEGATION, and how strict the resulting conditions are (documented strictness index).
  * data/packs/rg079_determinations.json - loadable pack: case_handling rows (signatories for
    every consent, fixing the five '(unparsed)' case_ids), metrics, two regulatory events
    (the 2026-08-18 delegation; the Project Apollo determination), RG-079 resolved, RG-073/074
    advanced, RG-084/085 opened.

Strictness index (reproducible, documented):
  generator hours cap present: +1; cap below the 200-hour template: +2 (i.e. 3 total)
  NOx mass cap +2; stack height +1; annual emissions testing +1; Tier standard +1
  PUE +1; WUE +1; renewable/PPA condition +1; recycled or non-potable water +1
  diesel storage cap +1; installed genset cap +1; battery storage +1; Guidelines cited +2
  Excluded: website disclosure (19/20, no discrimination), noise limits (19/20),
  demand_response (documented false positive - the template PROHIBITS diesel load curtailment),
  all_times_matching, clean_air_regulation (boilerplate POEO references).

Run:  python3 scripts/curate_rg079.py
      python3 scripts/load_pack.py data/packs/rg079_determinations.json --dry-run --allow-missing-source
"""
from __future__ import annotations

import csv
import glob
import json
import os
from collections import Counter, defaultdict
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATTERY = os.path.join(ROOT, "exports", "nsw_planning", "nsw_dc_consent_conditions.csv")
REPORT = os.path.join(ROOT, "exports", "nsw_planning", "reextraction_report.json")
NODES = os.path.join(ROOT, "data", "raw", "nsw_planning", "nodes")
ASSIGN = os.path.join(ROOT, "data", "raw", "nsw_planning", "planner_assignments.json")
OUT_CSV = os.path.join(ROOT, "exports", "nsw_planning", "nsw_dc_consent_determinations.csv")
OUT_PACK = os.path.join(ROOT, "data", "packs", "rg079_determinations.json")

TODAY = "2026-09-18"
GUIDELINES_EFFECTIVE = "2026-08-17"     # NSW Data Centre Guidelines took effect
SRC = "SRC_NSWPORTAL_CONSENTS"          # registered by the rg060 pack (load order matters)

# case_id corrections for existing case_handling rows written with '(unparsed)' case_ids by the
# consultancy-layer curation, before the Schedule 1 parse existed.
ROLE_BY_SLUG = {  # existing rows keep their officer_role; match keys must be exact
    "51-huntingwood-drive-data-centre": "delegate_signatory",
    "digico-syd1-data-centre-expansion": "delegate_signatory",
    "nextdc-s4-data-centre-horsley-park": "delegate_signatory",
    "project-apollo-data-centre-macquarie-park": "acting_director",
    "project-pluto-data-centre": "delegate_signatory",
    "station-road-data-centre-expansion": "delegate_signatory",
}


def strictness(r: dict) -> int:
    pts = 0
    h = (r.get("generator_hours_cap") or "").strip()
    if h:
        pts += 1
        try:
            if h.isdigit() and int(h) < 200:
                pts += 2
        except ValueError:
            pass
    pts += 2 if r.get("nox_mass_cap") else 0
    for k in ("stack_height", "annual_emissions_testing", "tier_standard", "pue", "wue",
              "renewable_ppa_additionality", "recycled_or_nonpotable_water",
              "diesel_storage_cap", "installed_genset_cap", "battery_storage"):
        pts += 1 if (r.get(k) or "").strip() else 0
    pts += 2 if (r.get("guidelines_cited") or "").strip() else 0
    return pts


def acting_flag(title: str) -> int:
    return 1 if (title or "").strip().lower().startswith(("a/", "acting")) else 0


def main() -> int:
    rows = list(csv.DictReader(open(BATTERY, encoding="utf-8")))
    assert len(rows) == 20, f"expected 20 battery rows, got {len(rows)}"
    report = {x["project"]: x for x in json.load(open(REPORT))["results"]}
    assignments = json.load(open(ASSIGN, encoding="utf-8"))

    nodes = {}
    for f in glob.glob(os.path.join(NODES, "*.json")):
        if f.endswith(".meta.json"):
            continue
        j = json.load(open(f, encoding="utf-8"))
        g = lambda k: (j.get(k) or [{}])[0].get("value")  # noqa: E731
        nodes[os.path.basename(f)[:-5]] = {
            "dod": str(g("field_date_of_determination_mp") or "")[:10],
            "auth": str(g("field_determination_authority") or ""),
        }

    det_rows = []
    for r in rows:
        slug_u = r["project"]                       # battery slug (underscores)
        slug = slug_u.replace("_", "-")             # portal/case_handling slug (hyphens)
        rep = report.get(slug_u, {})
        ex, sg = rep.get("execution", {}), rep.get("signatory", {})
        off = assignments.get(slug, [None, None, None])
        det = r["determination_date"]
        reg = r["determination_date_portal"]
        gap_days = ""
        if det and reg and len(det) == 10 and len(reg) == 10:
            gap_days = (date.fromisoformat(reg) - date.fromisoformat(det)).days
        era = "post_guidelines" if det >= GUIDELINES_EFFECTIVE else "pre_guidelines"
        auth = r["consent_authority"] or ""
        if slug == "talavera-road-data-centre-campus-expansion":
            auth = "NSW Independent Planning Commission"
        det_rows.append({
            "project": slug, "case_id": r["case_id"],
            "determination_date": det, "date_source": r["date_source"],
            "registered_portal": reg, "signed_to_registered_days": gap_days,
            "determination_authority_portal": r["determination_authority_portal"],
            "consent_authority": auth,
            "signatory_name": r["signatory_name"], "signatory_title": r["signatory_title"],
            "acting": acting_flag(r["signatory_title"]),
            "delegation_of": r["delegation_of"], "delegation_executed": r["delegation_executed"],
            "file_ref": r["file_ref"],
            "case_officer": off[0] or "", "case_officer_case_id": off[1] or "",
            "era": era, "strictness_index": strictness(r),
            "guidelines_cited": (r.get("guidelines_cited") or "").strip(),
            "parse_note": ex.get("parse_note", ""),
        })

    det_rows.sort(key=lambda d: d["determination_date"])
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(det_rows[0].keys()))
        w.writeheader()
        w.writerows(det_rows)
    print(f"wrote {OUT_CSV} ({len(det_rows)} determinations)")

    # ---- officer-effect analysis (RG-079) ----------------------------------------
    by_officer = defaultdict(list)
    for d in det_rows:
        by_officer[d["case_officer"] or "(unknown)"].append(d)
    sign_counts = Counter(d["signatory_name"] for d in det_rows)
    deleg_counts = Counter(d["delegation_executed"] or "(none/IPC determination)" for d in det_rows)
    post = [d for d in det_rows if d["era"] == "post_guidelines"]
    pre = [d for d in det_rows if d["era"] == "pre_guidelines"]
    idx = lambda ds: [d["strictness_index"] for d in ds]  # noqa: E731
    mean = lambda xs: round(sum(xs) / len(xs), 2) if xs else 0  # noqa: E731

    top2 = {"Shaun Williams", "Patrick Copas"}
    n_top2 = sum(len(v) for k, v in by_officer.items() if k in top2)
    n_post_top2 = sum(1 for d in post if d["case_officer"] in top2)
    # era-trend control: the index rewards provisions (PUE/WUE/renewable/recycled water) that
    # only became standard in instruments from late 2024, so compare the post-Guidelines pair
    # against the RECENT pre-Guidelines cohort, not the 2019-2023 instruments.
    recent = [d for d in pre if d["determination_date"] >= "2024-12-01"]
    print("\n=== officer x determinations (battery of 20) ===")
    for o, ds in sorted(by_officer.items(), key=lambda kv: -len(kv[1])):
        print(f"  {o:22s} n={len(ds):2d}  strictness mean={mean(idx(ds)):5.2f} "
              f"range={min(idx(ds))}-{max(idx(ds))}  eras={Counter(d['era'] for d in ds)}")
    print("\n=== signatories ===")
    for s, n in sign_counts.most_common():
        print(f"  {s:26s} {n}")
    print("\n=== delegation regimes ===")
    for g, n in sorted(deleg_counts.items()):
        print(f"  executed {g:22s} {n}")
    print(f"\npost-guidelines determinations: {len(post)} "
          f"({', '.join(d['project'] for d in post)})")
    print(f"strictness: post mean={mean(idx(post))} vs pre mean={mean(idx(pre))} "
          f"(pre range {min(idx(pre))}-{max(idx(pre))})")
    print(f"recent pre-guidelines cohort (>=2024-12): n={len(recent)} mean={mean(idx(recent))} "
          f"range={min(idx(recent))}-{max(idx(recent))}")

    # ---- pack ---------------------------------------------------------------------
    ch_updates, ch_inserts = [], []
    for d in det_rows:
        slug = d["project"]
        notes_bits = [f"Signed as {d['signatory_title'] or 'signatory'}." if d["signatory_title"] else "",
                      f"Determination date from {d['date_source']}." if d["date_source"] else "",
                      f"Portal registration {d['registered_portal']}"
                      + (f" ({d['signed_to_registered_days']} days after signing)."
                         if d["signed_to_registered_days"] not in ("", 0) else "."),
                      d["parse_note"]]
        notes = " ".join(b for b in notes_bits if b)
        base = dict(officer_name=d["signatory_name"], acting=d["acting"],
                    consent_authority=d["consent_authority"],
                    delegation_date=d["delegation_executed"] or None,
                    decision_date=d["determination_date"] or None,
                    file_reference=d["file_ref"] or None, notes=notes,
                    fact_status="VERIFIED", confidence="high", as_of_date=TODAY,
                    source_id=SRC)
        if slug in ROLE_BY_SLUG:
            # match WITHOUT case_id: apply_update never SETs a column it matches on, and the
            # whole point here is to replace the '(unparsed)' case_id. (slug, role) is unique
            # across the consultancy-layer rows.
            ch_updates.append(dict(match=dict(project_slug=slug,
                                              officer_role=ROLE_BY_SLUG[slug]),
                                   set=dict(case_id=d["case_id"], **base),
                                   add_sources=[SRC]))
        elif slug == "roberts-road-data-centre":
            ch_updates.append(dict(match=dict(case_id="SSD-10330", project_slug=slug,
                                              officer_role="delegate_signatory"),
                                   set=base, add_sources=[SRC]))
        elif slug == "glendenning-road-data-centre":
            continue  # consultancy-layer row already complete (decision/delegation/file)
        else:
            role = ("determination_authority"
                    if slug == "talavera-road-data-centre-campus-expansion"
                    else "delegate_signatory")
            # prefer the portal assignment's canonical case_id (SSD-8662, SSD-59416728-Mod-1)
            # over the battery's flattened parse (SSD8662, SSD-59416728)
            cid = d["case_officer_case_id"] or d["case_id"]
            ins = dict(case_id=cid, project_slug=slug, officer_role=role, **base)
            if slug == "talavera-road-data-centre-campus-expansion":
                ins["notes"] = ("PUBLISHED INSTRUMENT CARRIES UNFILLED TEMPLATE PLACEHOLDERS: the "
                                "signature block reads '[Name of Commissioner]' three times with "
                                "'Member of the Commission' titles - the IPC determination as "
                                "published does not name who decided it. Cover year-only date "
                                "('Sydney 2023 File: EF21/10619'); registered determination "
                                "2024-01-19 (portal, authority IPC-N). RG-085.")
            if slug == "dci-poplars-data-centre-project-0":
                ins["notes"] += (" Cover page also records: 'Condition A9 amended on 28 November "
                                 "2025 pursuant to agreement of Council on 2 December 2025 and the "
                                 "Applicant on 24 November 2025' - a post-determination amendment "
                                 "written into the published instrument.")
            if slug == "project-echidna-data-centre-eastern-creek":
                ins["notes"] += (" Only consent in the sample signed as delegate of the NSW "
                                 "Independent Planning Commission rather than the Minister.")
            ch_inserts.append(ins)

    metrics = []

    def M(name, value, notes, unit="count"):
        metrics.append(dict(as_of="2026-09", scope="NSW", metric_name=name, value=float(value),
                            unit=unit, basis="actual", notes=notes, fact_status="VERIFIED",
                            confidence="high", as_of_date=TODAY, source_id=SRC))

    M("consents_with_determination_date", len(det_rows),
      f"All {len(det_rows)} signed consents in the battery now carry a determination date: "
      f"{sum(1 for d in det_rows if d['date_source'].startswith('instrument'))} parsed from the "
      f"instrument's own cover-page execution line, "
      f"{sum(1 for d in det_rows if d['date_source'] == 'portal-node-metadata')} from portal node "
      f"metadata because the execution date is an image stamp absent from the text layer (Dicker "
      f"Data, Lane Cove West; Talavera Road's cover carries the year only). RG-079's blocker is "
      f"cleared.")
    M("consents_determined_post_guidelines", len(post),
      f"{len(post)} of 20 consents were determined on or after {GUIDELINES_EFFECTIVE}, when the NSW "
      f"Data Centre Guidelines took effect: " + "; ".join(
          f"{d['project']} ({d['determination_date']}, officer {d['case_officer']}, signed by "
          f"{d['signatory_name']})" for d in post) + ".")
    M("post_guidelines_consents_citing_guidelines",
      sum(1 for d in post if d["guidelines_cited"]),
      "Neither post-Guidelines consent cites the NSW Data Centre Guidelines. Across all 20 "
      "instruments the citation count is zero (battery column guidelines_cited). The Guidelines "
      "are guidance, not a mandatory instrument, and the first two determinations after they took "
      "effect do not reference them.")
    M("consents_signed_under_delegation_2026_08_18", deleg_counts.get("2026-08-18", 0),
      "Consents signed under the ministerial delegation executed 18 August 2026 - ONE DAY AFTER "
      "the Guidelines took effect: Project Apollo (2026-09-02) and Glendenning Road (signed "
      "2026-09-14, registered 2026-09-16), both by Joanna Bakopanos, A/Director Industry "
      "Assessments. Verified from the instruments' own cover pages ('As delegate of the Minister "
      "for Planning and Public Spaces under delegation executed on 18 August 2026').")
    M("consents_signed_under_delegation_2022_03_09", deleg_counts.get("2022-03-09", 0),
      f"{deleg_counts.get('2022-03-09', 0)} of 20 instruments were signed under the single "
      f"ministerial delegation executed 9 March 2022 - the standing regime from 2022 until the "
      f"18 August 2026 delegation. Full regime distribution: "
      + "; ".join(f"{k}: {v}" for k, v in sorted(deleg_counts.items())) + ".")
    M("distinct_consent_signatories", len(sign_counts),
      "Five signature blocks across 20 instruments: "
      + "; ".join(f"{k} {v}" for k, v in sign_counts.most_common())
      + ". The Talavera Road block is the unfilled template placeholder '[Name of Commissioner]' "
        "(RG-085). One A/Director signs 45% of the sample and both post-Guidelines consents.")
    M("determined_consents_officered_by_top_two", n_top2,
      f"Shaun Williams ({len(by_officer.get('Shaun Williams', []))}) and Patrick Copas "
      f"({len(by_officer.get('Patrick Copas', []))}) are the case officers for {n_top2} of the 20 "
      f"determined consents ({round(100*n_top2/20)}%), mirroring their 65% share of the 63-project "
      f"live pipeline (v_case_officer_load). Both post-Guidelines determinations sit with them "
      f"({n_post_top2} of {len(post)}): Glendenning=Williams, Project Apollo=Copas.")
    M("officers_who_managed_and_signed_sample_consents", 1,
      "Joanna Bakopanos appears on BOTH sides of the record: case planner for the Talavera Road "
      "campus expansion (SSD-24299707, planner_assignments.json) and, as A/Director Industry "
      "Assessments, signatory of 9 of the 20 determined consents including both post-Guidelines "
      "determinations. Not evidence of impropriety - assessment and determination are separate "
      "functions and the Talavera determination was the IPC's - but the same small office both "
      "manages and signs the pipeline, which is the structural point RG-079 was opened to test.")
    M("mean_strictness_index_post_guidelines", mean(idx(post)),
      f"Documented strictness index (formula in scripts/curate_rg079.py). The two post-Guidelines "
      f"consents score {', '.join('%d (%s)' % (d['strictness_index'], d['project']) for d in post)} - at "
      f"or above the top of the pre-Guidelines distribution (mean {mean(idx(pre))}, range "
      f"{min(idx(pre))}-{max(idx(pre))} across 18). BUT the index rewards provisions that only "
      f"became standard in late-2024 instruments, so the honest control is the recent "
      f"pre-Guidelines cohort (determined from 2024-12 onward, n={len(recent)}): mean "
      f"{mean(idx(recent))}, range {min(idx(recent))}-{max(idx(recent))}. Project Apollo ties the "
      f"cohort top (NEXTDC S4, determined 2025-12-24 on proponent commitments); Glendenning "
      f"exceeds it on air-quality conditions (170-hour cap, NOx mass cap, 45 m stacks, annual "
      f"testing) that RG-026/RG-060 attribute to site-specific assessment, not to the Guidelines "
      f"- which NEITHER consent cites. Reading: the tightening trend predates 17 August 2026 and "
      f"continues through it; the Guidelines added no citable requirement to either instrument.",
      unit="index")

    events = [
        dict(event_date="2026-08-18", regulator_id="ENT_NSW_DPHI", event_type="other",
             summary="A ministerial delegation for Industry Assessments was executed on 18 August "
                     "2026 - one day after the NSW Data Centre Guidelines took effect. Every "
                     "determination after that date in the sample (Project Apollo 2026-09-02; "
                     "Glendenning Road signed 2026-09-14) was made by Joanna Bakopanos, A/Director "
                     "Industry Assessments, under this new delegation, replacing the delegation of "
                     "9 March 2022 under which the previous twelve instruments in the sample were "
                     "signed.",
             outcome="New delegation regime in force from 18 August 2026.",
             notes="Verified from the cover pages of the two signed instruments ('As delegate of "
                   "the Minister for Planning and Public Spaces under delegation executed on 18 "
                   "August 2026, I approve...'), archived with SHA-256 manifests under "
                   "data/raw/nsw_planning/consents/. The delegation instrument itself has not been "
                   "sighted; its existence and date are established by the consents signed under "
                   "it.",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
        dict(event_date="2026-09-02", regulator_id="ENT_NSW_DPHI", site_id="SITE_PROJECT_APOLLO",
             event_type="determination",
             summary="Project Apollo Data Centre, Macquarie Park (SSD-74069708; Schedule 1 "
                     "applicant Goodman Property Services (Aust) Pty Limited) was determined - the "
                     "FIRST consent determined after the NSW Data Centre Guidelines took effect. "
                     "Signed by Joanna Bakopanos, Acting Director Industry Assessments, under the "
                     "delegation executed 18 August 2026. File EF24/11318.",
             outcome="Approved. 135 MW total power cap; 185 MW installed back-up; 187-hour "
                     "generator cap; 2,000 t diesel; PUE, WUE, renewable supply and "
                     "recycled/non-potable water provisions; NOx mass cap absent; the Guidelines "
                     "are not cited.",
             notes="Case officer Patrick Copas - one of the two officers who hold 65% of the live "
                   "pipeline. Determination date verified from the instrument cover ('Sydney 2 "
                   "September 2026'-form execution line, parsed 2026-09-02) and portal node "
                   "metadata (field_date_of_determination_mp 2026-09-02).",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
    ]

    off_table = "\n".join(
        f"  {o}: n={len(ds)}, mean {mean(idx(ds))}, range {min(idx(ds))}-{max(idx(ds))}"
        for o, ds in sorted(by_officer.items(), key=lambda kv: -len(kv[1])))
    gaps = [
        dict(match=dict(id=79),
             set=dict(status="resolved", resolved_date=TODAY,
                      notes="RESOLVED 2026-09-18. determination_date is now populated on all 20 "
                            "consents (18 from the instruments' own cover-page execution lines, 2 "
                            "from portal node metadata where the date is an image stamp), "
                            "unblocking the officer-effect test. Matrix: "
                            "exports/nsw_planning/nsw_dc_consent_determinations.csv. FINDING: at "
                            "n=20 no officer effect is detectable, and the evidence says condition "
                            "stringency is TEMPLATE-DOMINATED, not officer-driven: the 200-hour "
                            "generator cap appears in 14 of the 17 consents that carry any cap; "
                            "website disclosure in 19 of 20; the Guidelines are cited in 0 of 20 "
                            "including both post-Guidelines determinations. Officer portfolios "
                            "overlap completely on the documented strictness index:\n" + off_table +
                            "\nWithin-officer variation exceeds between-officer variation "
                            "(Williams' own portfolio spans the sample's strictest air-quality "
                            "consent, Glendenning, to consents with no PUE/WUE/renewable "
                            "provisions), and strictness is era-confounded: index scores rise "
                            "steeply with determination date because PUE/WUE/renewable/recycled-"
                            "water provisions only became standard in instruments from late 2024, "
                            "so officer portfolios that happen to hold recent cases score higher "
                            "(Williams mean 6.56 over nine cases, eight of them pre-Guidelines but "
                            "mostly recent; Copas 4.50 over six spanning 2019-2026). Where "
                            "conditions DO depart from template - NEXTDC S4's "
                            "5.5 t/yr NOx cap including testing, Glendenning's 170 hours, Pluto "
                            "173, Apollo 187 - the record attributes them to proponent EIS "
                            "commitments (RG-061's mechanism) or site-specific assessment, not to "
                            "the case officer. Structural finding retained: Williams+Copas officer "
                            "15 of 20 determined consents and both post-Guidelines determinations, "
                            "and the same office (Industry Assessments, Bakopanos signing as "
                            "A/Director) both manages and signs the pipeline; the new delegation "
                            "under which the post-Guidelines consents were signed was executed one "
                            "day after the Guidelines took effect (2026-08-18). LIMITATION: n=20 "
                            "with 2 post-Guidelines observations cannot support statistical "
                            "inference; internal condition-setting records are only reachable via "
                            "the RG-007 FOI route.",
                      fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
             add_sources=[SRC]),
        dict(match=dict(id=74),
             set=dict(status="in_progress",
                      notes="ADVANCED 2026-09-18. All 20 Schedule 1 applicants now parse "
                            "(RG-065): SEVEN consents are held by consultancies or an architectural "
                            "practice - ARUP Pty Ltd (Turner Road), ARUP Australia Pty Ltd "
                            "(Echidna), Cundall Johnston and Partners (Davis Road consent AND Mod "
                            "1), Lehr Consultants (Glendenning Road, Station Road), Greenbox "
                            "Architecture (Lane Cove West). Cross-referenced against the tracked "
                            "gov_contracts table: NONE of these firms appears - the tracked "
                            "contract population is TCS-weighted (Transport for NSW, RBA, "
                            "Melbourne Water, DCS, Defence, PM&C, NSWEC), so the overlap question "
                            "cannot be answered from it. REMAINING: pull DPHI, IPC and "
                            "Planning-portfolio contracts from AusTender and buy.nsw by AGENCY "
                            "(not by supplier) and test whether Arup/Cundall/Lehr/Greenbox - or "
                            "the firms authoring the technical appendices under RG-073 - hold "
                            "assessment-side work.",
                      fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
             add_sources=[SRC]),
        dict(match=dict(id=73),
             set=dict(notes="ADVANCED 2026-09-18. The consultancy applicants of record are now "
                            "established for all 20 consents (see RG-074 note): firms holding "
                            "consents in their own name are Arup (two distinct legal entities), "
                            "Cundall, Lehr and Greenbox. Appendix-level authorship still requires "
                            "opening the 6,866 archived attachments; filenames alone remain "
                            "insufficient evidence of authorship.",
                      as_of_date=TODAY, source_id=SRC),
             add_sources=[SRC]),
        dict(id=84, pillar="A", priority=4, retrieval_method="manual_review", status="open",
             opened=TODAY,
             question="Are SITE_MACQUARIE_PARK_DC (Macquarie Park Data Centre, SSD-10467, "
                      "applicant Stockland Trust Management Limited, determined 2021-05-28) and "
                      "SITE_STOCKLAND_MP (Stockland Macquarie Park Stage 1, under construction) "
                      "the same project at different stages, or distinct consents?",
             why_it_matters="Double-counting or splitting a Stockland Macquarie Park project "
                            "distorts the Sydney pipeline MW totals; a second Stockland entity "
                            "(Stockland Development Pty Limited) also holds the Khartoum Road "
                            "consent, so the group's NSW data centre position is currently spread "
                            "across at least three site rows and two legal entities.",
             target_source="The SSD-10467 consent (archived), Stockland project pages, NSW "
                           "Planning Portal node for the Stage 1 record",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
        dict(id=85, pillar="C", priority=3, retrieval_method="regulator_request", status="open",
             opened=TODAY,
             question="Who actually decided the Talavera Road Data Centre Campus Expansion "
                      "(SSD-24299707)? The published IPC consent carries '[Name of Commissioner]' "
                      "template placeholders in its signature block and only a year ('Sydney 2023') "
                      "in its execution line, while the portal registered the determination on "
                      "2024-01-19.",
             why_it_matters="A published determination instrument that does not name its "
                            "decision-maker fails the basic accountability test the rest of the "
                            "sample passes, and it is the only IPC determination in the battery - "
                            "the one consent NOT decided under ministerial delegation. The "
                            "signing-to-registration gap (2023 instrument, January 2024 "
                            "registration) is also the largest in the sample.",
             target_source="IPC determination records and published decisions list for "
                           "SSD-24299707; GIPA request to IPC if not published",
             fact_status="VERIFIED", confidence="high", as_of_date=TODAY, source_id=SRC),
    ]

    pack = {
        "pack_id": "rg079-determinations-2026-09",
        "prepared_by": "scripts/curate_rg079.py from exports/nsw_planning/"
                       "nsw_dc_consent_conditions.csv + reextraction_report.json + archived nodes",
        "prepared_on": TODAY,
        "sources": [],   # SRC_NSWPORTAL_CONSENTS registered by rg060 pack (load-order dependent)
        "rows": {
            "case_handling": ch_updates + ch_inserts,
            "metrics": metrics,
            "regulatory_events": events,
            "research_gaps": gaps,
        },
    }
    os.makedirs(os.path.dirname(OUT_PACK), exist_ok=True)
    with open(OUT_PACK, "w", encoding="utf-8") as fh:
        json.dump(pack, fh, indent=1)
    print(f"\nwrote {OUT_PACK}: case_handling={len(ch_updates)} updates +{len(ch_inserts)} inserts, "
          f"metrics={len(metrics)}, events={len(events)}, gaps={len(gaps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
