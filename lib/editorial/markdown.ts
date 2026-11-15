/**
 * Remark plugins for essay bodies.
 *
 * An essay is Markdown with two additions, both chosen so the raw text still
 * reads sensibly in a pull request:
 *
 *   - Citations: [SRC_NSWGUIDE26] cites a source record; [RG-070] points at an
 *     open research question. Rendered as a numbered superscript linking to
 *     the source panel, and as a link to the open questions page.
 *   - Callouts: a block quote opening with [!PULLQUOTE] or [!FIGURE].
 *
 *       > [!PULLQUOTE]
 *       > The rules never say who commissioned it [SRC_NSWGUIDE26].
 *
 *       > [!FIGURE] 6 in 7
 *       > Connection requests the guidelines call phantom demand [SRC_NSWGUIDE26]
 *
 * Raw HTML is never rendered (react-markdown's skipHtml), so a body cannot
 * smuggle markup onto the page whoever wrote it.
 */

import type { Blockquote, Parent, PhrasingContent, Root, RootContent, Text } from 'mdast';

const CITATION = /\[(SRC_[A-Za-z0-9_]+)\]|\[(RG-\d{3})\]/g;

type AnyNode = Root | RootContent;

/**
 * Depth-first walk. The visitor runs before a node's children are visited, so
 * it may replace them; the walk then descends into the replacements.
 */
function walk(node: AnyNode, visit: (node: AnyNode) => void): void {
  visit(node);
  if ('children' in node) {
    for (const child of [...(node.children as AnyNode[])]) walk(child, visit);
  }
}

/** A citation marker as an inline node that renders as <sup data-cite="SRC_X">. */
function citeNode(id: string): PhrasingContent {
  return {
    type: 'text',
    value: '',
    data: { hName: 'sup', hProperties: { dataCite: id } },
  } as unknown as PhrasingContent;
}

/** A question marker as a link to the open questions page. */
function questionNode(id: string): PhrasingContent {
  return {
    type: 'link',
    url: `/research#${id}`,
    title: `Open research question ${id}`,
    children: [{ type: 'text', value: id }],
    data: { hProperties: { dataQuestion: id } },
  };
}

/** Split one text node into text and citation nodes. */
export function splitCitations(value: string): PhrasingContent[] {
  const out: PhrasingContent[] = [];
  let last = 0;
  for (const m of value.matchAll(CITATION)) {
    const at = m.index ?? 0;
    // Drop the space a writer leaves before a citation: "claim [SRC_X]." reads
    // as "claim¹." on the page.
    const before = value.slice(last, at).replace(/[ \t]+$/, '');
    if (before) out.push({ type: 'text', value: before });
    out.push(m[1] ? citeNode(m[1]) : questionNode(m[2]!));
    last = at + m[0].length;
  }
  const rest = value.slice(last);
  if (rest) out.push({ type: 'text', value: rest });
  return out;
}

/** Turn [SRC_X] and [RG-nnn] in running text into citation nodes. Code is left alone. */
export function remarkCitations() {
  return (tree: Root) => {
    walk(tree, (node) => {
      // Code and inline code have no children, so they are never rewritten.
      if (!('children' in node)) return;
      const parent = node as Parent;
      const next: AnyNode[] = [];
      let changed = false;
      for (const child of parent.children as AnyNode[]) {
        if (child.type === 'text' && CITATION.test((child as Text).value)) {
          CITATION.lastIndex = 0;
          next.push(...splitCitations((child as Text).value));
          changed = true;
        } else {
          next.push(child);
        }
        CITATION.lastIndex = 0;
      }
      if (changed) parent.children = next as Parent['children'];
    });
  };
}

const CALLOUT = /^\[!(PULLQUOTE|FIGURE)\][ \t]*/;

/** Block quotes marked [!PULLQUOTE] or [!FIGURE] become callouts. */
export function remarkCallouts() {
  return (tree: Root) => {
    walk(tree, (node) => {
      if (node.type !== 'blockquote') return;
      const quote = node as Blockquote;
      const first = quote.children[0];
      if (!first || first.type !== 'paragraph') return;
      const lead = first.children[0];
      if (!lead || lead.type !== 'text') return;
      const m = CALLOUT.exec(lead.value);
      if (!m) return;

      const kind = m[1] === 'PULLQUOTE' ? 'pullquote' : 'figure';
      lead.value = lead.value.slice(m[0].length);

      if (kind === 'pullquote') {
        if (!lead.value) first.children.shift();
        quote.data = { hName: 'aside', hProperties: { className: ['pullquote'] } };
        return;
      }

      // A figure: the rest of the first line is the value, everything after it the caption.
      const newline = lead.value.indexOf('\n');
      const figure = (newline === -1 ? lead.value : lead.value.slice(0, newline)).trim();
      lead.value = newline === -1 ? '' : lead.value.slice(newline + 1);
      if (!lead.value) first.children.shift();

      quote.data = { hName: 'figure', hProperties: { className: ['figure-callout'] } };
      quote.children = [
        {
          type: 'paragraph',
          data: { hName: 'p', hProperties: { className: ['figure-value'] } },
          children: [{ type: 'text', value: figure }],
        },
        {
          ...first,
          data: { hName: 'figcaption' },
        },
        ...quote.children.slice(1),
      ];
    });
  };
}

/** A heading's text as a URL fragment: "What to watch next" to "what-to-watch-next". */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[’']/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
