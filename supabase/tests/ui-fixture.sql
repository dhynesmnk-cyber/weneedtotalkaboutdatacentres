-- Published pieces for the browser test (scripts/test-ui.sh) to render.
--
-- Test-only, in a throwaway database. The text says what it is and states no
-- finding: it exists so the essay page, its citations, callouts and both
-- colour schemes are drawn and checked for accessibility. It cites the first
-- five sources the load holds, so the citation trigger (0016) accepts it.

\set ON_ERROR_STOP on

insert into editorial.essays
  (title, slug, kind, standfirst, body, data_as_of_date, publish_date, approved_by, approved_at)
select
  'Browser test essay',
  'ui-test-essay',
  'essay',
  'A fixture for the accessibility test. It is not content and states no finding.',
  -- One escape string, continued across lines: only the first piece may
  -- carry the E prefix, and the rest inherit it.
  format(E'## The common perception\nThis paragraph stands in for a claim [%1$s].\n\n'
          '## What the records show\nA first record [%2$s]. A second [%3$s].\n\n'
          '> [!PULLQUOTE]\n> A pull quote, drawn for the test [%1$s].\n\n'
          '> [!FIGURE] 1 in 1\n> A figure, drawn for the test [%4$s]\n\n'
          '## Where the data is too thin\nAn open question stands here [RG-001].\n\n'
          '## What to watch next\nA last record [%5$s].\n\n'
          '## Our view\nThis paragraph stands in for an argument.\n',
         ids[1], ids[2], ids[3], ids[4], ids[5]),
  current_date - 30,
  current_date - 1,
  'browser test',
  now()
from (
  select array_agg(pipeline_id order by pipeline_id) as ids
  from (
    select pipeline_id from facts.sources
     where pipeline_id is not null
     order by pipeline_id
     limit 5
  ) first_five
) s;

insert into editorial.essays
  (title, kind, body, data_as_of_date, publish_date, approved_by, approved_at, conflict)
values
  ('Browser test position', 'position',
   E'## Our view\nThis paragraph stands in for a position.\n',
   current_date - 30, current_date - 1, 'browser test', now(),
   'A fixture disclosure, drawn so the disclosure box is checked too.');
