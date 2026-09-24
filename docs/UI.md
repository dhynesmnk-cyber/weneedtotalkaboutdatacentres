# UI.md

## Principles
- Clarity over density. General readers see a guided narrative first.
- Fact and opinion are visually distinct at all times.
- Everything is dated. Show publish date and data as of date.
- Gaps are visible. A gap badge is better than a blank or a guess.

## Pages
- Home: leads with the record summary, then the timeline. The summary counts
  what the record holds (sites tracked; how many have an operator, a council,
  a total capacity and coordinates; sites by status) and is dated with the
  last pipeline load. It leads because the state of the record is the first
  finding a reader needs, and the timeline is empty until events are loaded.
- Timeline: track selector for planning, construction, media, political,
  community and financial events. Combine tracks as needed; at least one track
  is always selected. The selection lives in the URL.
- Coverage: for every site field, how many sites hold a value, how many carry
  a gap and why, and how many have neither. A table first. A stored value that
  itself says "unknown" is counted as an `unknown` gap, never as recorded.
- Essay hub: date ordered list of video essays with embeds and written analysis.
- Map: single Leaflet point layer, popup shows name, operator, status, capacity.
- List: index of sites and entities with status and capacity. Sortable by
  name, status, capacity and council; filterable by status and council. Sort
  and filters live in the URL, and the filter is a plain GET form, so it works
  without JavaScript. Sites missing the sort value always sort last.
- Site profile: all site fields with gap badges, linked events, linked entities.
- Entity profile: major entities only, with auto linked sites and events.
- Case study: dated financial narrative with metric cards and source panel.
- Essay page: embed, body, related sites and events, source panel.

## Components
- TimelineTrackSelector
- SourcePanel (citations for the current record)
- GapBadge (explicit missing data marker, renders the data_gaps reason)
- FactOpinionDivider (separates verified fact from editorial)
- DateStamp (publish and data as of dates)
- MapPointPopup

## Navigation
Overview, Essays, Map, Sites and entities, Coverage: SPEC.md's entry-point
order, then the coverage view. The current section is marked with
`aria-current`.

## Gap presentation
A gap badge always states why a value is missing, never just that it is. The four
reasons in SPEC.md map to reader facing wording:

- unknown: "Not yet researched"
- not_disclosed: "Not disclosed"
- not_applicable: "Not applicable"
- withheld: "Withheld in source"

Where a gap cites a source, the badge links into the SourcePanel like any other
claim. A gap is a finding and is presented as one.

The badge is the same everywhere a missing value is shown: the site record,
the index, and the map popup. A blank with no gap record shows the "No value
recorded" defect badge instead.

## Map
Leaflet, not MapLibre GL. v1 is a single point layer with popups, which needs no
vector tiles or WebGL, keeps the bundle small, and is the more forgiving base for
the keyboard navigable alternative and the WCAG 2.2 AA target below. MapLibre's
advantage is the GIS overlay path, and SPEC.md rules overlays out for v1. Revisit
if and when overlays enter scope.

## Accessibility
- Target WCAG 2.2 AA.
- Full keyboard navigation for timeline and map alternatives.
- Sufficient colour contrast for badges and dividers.
- Respect reduced motion preferences.
