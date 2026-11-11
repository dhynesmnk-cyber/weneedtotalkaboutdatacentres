import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { EssayBody, type CitationIndex } from '@/components/essay/EssayBody';
import { slugify, splitCitations } from '@/lib/editorial/markdown';

const citations: CitationIndex = {
  SRC_A: { n: 1, title: 'Source A' },
  SRC_B: { n: 2, title: 'Source B' },
};

function render(markdown: string): string {
  return renderToStaticMarkup(<EssayBody markdown={markdown} citations={citations} />);
}

describe('essay citations', () => {
  it('numbers a source citation and links it to the source panel', () => {
    const html = render('A claim [SRC_A].');
    expect(html).toContain('<sup class="cite"><a href="#sources-1" aria-label="Source 1: Source A">1</a></sup>');
    // The space before the marker goes, so the number sits on the word.
    expect(html).toContain('A claim<sup');
    expect(html).not.toContain('[SRC_A]');
  });

  it('cites two sources side by side', () => {
    const html = render('Two claims [SRC_A] [SRC_B].');
    expect(html).toContain('href="#sources-1"');
    expect(html).toContain('href="#sources-2"');
  });

  it('marks a citation the record does not hold instead of hiding it', () => {
    const html = render('A claim [SRC_UNKNOWN].');
    expect(html).toContain('cite-unknown');
    expect(html).toContain('[?]');
  });

  it('links an open question to the research agenda', () => {
    const html = render('Nobody knows yet [RG-070].');
    expect(html).toContain('href="/research#RG-070"');
    expect(html).toContain('open research question');
  });

  it('leaves citations inside code alone', () => {
    const html = render('Write `[SRC_A]` to cite.');
    expect(html).toContain('<code>[SRC_A]</code>');
  });

  it('splits text around every citation', () => {
    const parts = splitCitations('one [SRC_A] two [RG-001] three');
    expect(parts.map((p) => p.type)).toEqual(['text', 'text', 'text', 'link', 'text']);
  });
});

describe('essay callouts', () => {
  it('renders a pull quote as an aside', () => {
    const html = render('> [!PULLQUOTE]\n> The rules never say who paid for it [SRC_A].');
    expect(html).toMatch(/^<aside class="pullquote">/);
    expect(html).not.toContain('[!PULLQUOTE]');
  });

  it('renders a figure with its value and a cited caption', () => {
    const html = render('> [!FIGURE] 6 in 7\n> Requests called phantom demand [SRC_A]');
    expect(html).toContain('<figure class="figure-callout">');
    expect(html).toContain('<p class="figure-value">6 in 7</p>');
    expect(html).toContain('<figcaption>Requests called phantom demand<sup class="cite">');
  });

  it('leaves an ordinary block quote as a quote', () => {
    expect(render('> Just a quote [SRC_A].')).toMatch(/^<blockquote>/);
  });
});

describe('essay safety and structure', () => {
  it('never renders raw HTML from the body', () => {
    const html = render('Hello <script>alert(1)</script> <img src=x onerror=alert(1)>');
    expect(html).not.toContain('<script');
    expect(html).not.toContain('<img');
  });

  it('drops a javascript: link', () => {
    expect(render('[click](javascript:alert(1))')).not.toContain('javascript:');
  });

  it('marks external links as opening in a new tab', () => {
    const html = render('[a report](https://example.org/report)');
    expect(html).toContain('rel="noopener noreferrer"');
    expect(html).toContain('(opens in a new tab)');
  });

  it('gives section headings anchors for the section navigation', () => {
    expect(render('## What to watch next')).toContain('<h2 id="what-to-watch-next">');
  });

  it('slugifies curly apostrophes and accents', () => {
    expect(slugify('Australia’s rules now')).toBe('australias-rules-now');
    expect(slugify('Québec fund')).toBe('quebec-fund');
  });
});
