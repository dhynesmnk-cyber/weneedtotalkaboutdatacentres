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
- Map: single point layer, popup shows name, operator, status, capacity.
- List: sortable index of sites and entities with status and capacity.
- Site profile: all site fields with gap badges, linked events, linked entities.
- Entity profile: major entities only, with auto linked sites and events.
- Case study: dated financial narrative with metric cards and source panel.
- Essay page: embed, body, related sites and events, source panel.

## Components
- TimelineTrackSelector
- SourcePanel (citations for the current record)
- GapBadge (explicit missing data marker)
- FactOpinionDivider (separates verified fact from editorial)
- DateStamp (publish and data as of dates)
- MapPointPopup

## Accessibility
- Target WCAG 2.2 AA.
- Full keyboard navigation for timeline and map alternatives.
- Sufficient colour contrast for badges and dividers.
- Respect reduced motion preferences.
