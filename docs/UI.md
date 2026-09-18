# UI.md

## Principles
- Clarity over density. General readers see a guided narrative first.
- Fact and opinion are visually distinct at all times.
- Everything is dated. Show publish date and data as of date.
- Gaps are visible. A gap badge is better than a blank or a guess.

## Pages
- Home and Timeline: track selector for planning, construction, media,
  political, community and financial events. Combine tracks as needed.
- Essay hub: date ordered list of video essays with embeds and written analysis.
- Map: single Leaflet point layer, popup shows name, operator, status, capacity.
- List: sortable index of sites and entities with status and capacity.
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

## Gap presentation
A gap badge always states why a value is missing, never just that it is. The four
reasons in SPEC.md map to reader facing wording:

- unknown: "Not yet researched"
- not_disclosed: "Not disclosed"
- not_applicable: "Not applicable"
- withheld: "Withheld in source"

Where a gap cites a source, the badge links into the SourcePanel like any other
claim. A gap is a finding and is presented as one.

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
