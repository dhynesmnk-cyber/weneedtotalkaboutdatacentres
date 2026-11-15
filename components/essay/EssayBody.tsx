import Markdown, { type Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { ReactNode } from 'react';
import { remarkCallouts, remarkCitations, slugify } from '@/lib/editorial/markdown';

/** What a citation number needs to render: its position and what it points at. */
export type CitationIndex = Record<string, { n: number; title: string }>;

function textOf(children: ReactNode): string {
  if (typeof children === 'string' || typeof children === 'number') return String(children);
  if (Array.isArray(children)) return children.map(textOf).join('');
  if (children && typeof children === 'object' && 'props' in children) {
    return textOf((children as { props: { children?: ReactNode } }).props.children);
  }
  return '';
}

/**
 * Renders an essay's Markdown, with numbered citations linking into the source
 * panel. Used by the public essay page and by the editor's preview, so the
 * editor approves exactly what readers will see.
 *
 * No raw HTML is rendered, and links keep react-markdown's URL filter, so a
 * body cannot put script or markup on the page.
 */
export function EssayBody({
  markdown,
  citations,
  anchor = 'sources',
}: {
  markdown: string;
  citations: CitationIndex;
  /** The source panel's id; entries are `${anchor}-${n}`. */
  anchor?: string;
}) {
  const components: Components = {
    sup({ node, children, ...props }) {
      const id = (node?.properties?.dataCite as string | undefined) ?? undefined;
      if (!id) return <sup {...props}>{children}</sup>;
      const entry = citations[id];
      if (!entry) {
        return (
          <sup className="cite cite-unknown" title={`${id} is not a source the record holds`}>
            [?]
          </sup>
        );
      }
      return (
        <sup className="cite">
          <a href={`#${anchor}-${entry.n}`} aria-label={`Source ${entry.n}: ${entry.title}`}>
            {entry.n}
          </a>
        </sup>
      );
    },
    a({ node, href, children, ...props }) {
      const question = node?.properties?.dataQuestion as string | undefined;
      if (question) {
        return (
          <a href={href} className="question-ref" title={`Open research question ${question}`}>
            <span className="sr-only">open research question </span>
            {children}
          </a>
        );
      }
      const external = typeof href === 'string' && /^https?:\/\//.test(href);
      return (
        <a
          href={href}
          {...props}
          {...(external ? { rel: 'noopener noreferrer', target: '_blank' } : {})}
        >
          {children}
          {external && <span className="sr-only"> (opens in a new tab)</span>}
        </a>
      );
    },
    h2({ node: _node, children, ...props }) {
      return (
        <h2 id={slugify(textOf(children))} {...props}>
          {children}
        </h2>
      );
    },
    h3({ node: _node, children, ...props }) {
      return (
        <h3 id={slugify(textOf(children))} {...props}>
          {children}
        </h3>
      );
    },
  };

  return (
    <Markdown
      remarkPlugins={[remarkGfm, remarkCallouts, remarkCitations]}
      skipHtml
      components={components}
    >
      {markdown}
    </Markdown>
  );
}
