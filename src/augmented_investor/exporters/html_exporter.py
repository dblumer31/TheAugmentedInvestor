"""HTML export for final or review-ready issues."""

from __future__ import annotations

from html import escape
import re

from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import FactCheckReport
from augmented_investor.models.research import ResearchBrief


def export_html(
    draft: DraftIssue,
    research: ResearchBrief | None = None,
    fact_check: FactCheckReport | None = None,
) -> str:
    """Render a draft and review metadata as standalone HTML."""

    SourceHtml = _render_sources(draft, research)
    FactCheckHtml = _render_fact_check(fact_check) if fact_check else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(draft.Title)}</title>
  <style>
{_stylesheet()}
  </style>
</head>
<body>
  <main class="page">
    <header class="issue-header">
      <p class="eyebrow">The Augmented Investor</p>
      <h1>{escape(draft.Title)}</h1>
      <p class="subtitle">{escape(draft.Subtitle)}</p>
      <dl class="metadata">
        <div><dt>Subject</dt><dd>{escape(draft.SubjectLine)}</dd></div>
        <div><dt>Word Count</dt><dd>{draft.WordCount}</dd></div>
      </dl>
      <p class="lede">{escape(draft.Lede)}</p>
    </header>

    <article class="issue-body">
{_body_to_html(draft.Body)}
    </article>

    <aside class="review-panel">
{FactCheckHtml}
{SourceHtml}
    </aside>
  </main>
</body>
</html>
"""


def _stylesheet() -> str:
    """Return embedded CSS for a readable exported issue."""

    return """    :root {
      color-scheme: light;
      --bg: #f6f1e8;
      --paper: #fffdf8;
      --ink: #1f2933;
      --muted: #667085;
      --line: #ded7ca;
      --accent: #8a4b2a;
      --accent-soft: #f1dfd2;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Georgia, "Times New Roman", serif;
      line-height: 1.65;
    }

    .page {
      width: min(920px, calc(100% - 32px));
      margin: 40px auto;
      padding: 48px;
      background: var(--paper);
      border: 1px solid var(--line);
      box-shadow: 0 24px 60px rgb(31 41 51 / 12%);
    }

    .issue-header {
      border-bottom: 1px solid var(--line);
      padding-bottom: 28px;
      margin-bottom: 34px;
    }

    .eyebrow {
      margin: 0 0 12px;
      color: var(--accent);
      font-family: Arial, sans-serif;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.16em;
      text-transform: uppercase;
    }

    h1 {
      margin: 0;
      font-size: clamp(2.4rem, 6vw, 4.75rem);
      line-height: 0.95;
      letter-spacing: -0.05em;
    }

    .subtitle {
      max-width: 720px;
      margin: 18px 0 0;
      color: var(--muted);
      font-family: Arial, sans-serif;
      font-size: 1.18rem;
      line-height: 1.45;
    }

    .metadata {
      display: grid;
      gap: 10px;
      margin: 28px 0;
      padding: 18px;
      background: var(--accent-soft);
      border-radius: 14px;
      font-family: Arial, sans-serif;
    }

    .metadata div {
      display: grid;
      grid-template-columns: 110px 1fr;
      gap: 16px;
    }

    .metadata dt {
      color: var(--accent);
      font-size: 0.78rem;
      font-weight: 700;
      text-transform: uppercase;
    }

    .metadata dd {
      margin: 0;
    }

    .lede {
      margin: 0;
      font-size: 1.18rem;
      line-height: 1.7;
    }

    .issue-body {
      font-size: 1.08rem;
    }

    .issue-body h2 {
      margin: 2.1em 0 0.55em;
      font-size: 1.65rem;
      line-height: 1.2;
      letter-spacing: -0.02em;
    }

    .issue-body p {
      margin: 0 0 1.2em;
    }

    .review-panel {
      display: grid;
      gap: 18px;
      margin-top: 44px;
      padding-top: 28px;
      border-top: 1px solid var(--line);
      font-family: Arial, sans-serif;
      font-size: 0.95rem;
      line-height: 1.5;
    }

    .card {
      padding: 20px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: #fffaf0;
    }

    .card h2 {
      margin: 0 0 12px;
      font-size: 1rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .status {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-weight: 700;
    }

    .sources {
      columns: 2;
      padding-left: 1.2rem;
    }

    .sources li {
      break-inside: avoid;
      margin: 0 0 0.55rem;
    }

    a {
      color: var(--accent);
    }

    @media (max-width: 700px) {
      .page {
        width: auto;
        margin: 0;
        padding: 28px 20px;
        border: 0;
      }

      .metadata div {
        grid-template-columns: 1fr;
        gap: 2px;
      }

      .sources {
        columns: 1;
      }
    }"""


def _body_to_html(body: str) -> str:
    """Convert writer Markdown-style body text into article HTML."""

    if _looks_like_html(body):
        return _indent_body(body)
    Blocks = [Block.strip() for Block in re.split(r"\n\s*\n", body) if Block.strip()]
    return "\n".join(f"      {_block_to_html(Block)}" for Block in Blocks)


def _looks_like_html(body: str) -> bool:
    """Return true when the body already appears to contain HTML tags."""

    return bool(re.search(r"</?(p|h[1-6]|ul|ol|li|section|div|article)\b", body.strip()))


def _indent_body(body: str) -> str:
    """Indent existing body HTML inside the article tag."""

    return "\n".join(f"      {Line}" for Line in body.splitlines())


def _block_to_html(block: str) -> str:
    """Render one Markdown-ish block as HTML."""

    Heading = _bold_heading(block)
    if Heading:
        return f"<h2>{escape(Heading)}</h2>"
    return f"<p>{_inline_markup_to_html(block)}</p>"


def _bold_heading(block: str) -> str | None:
    """Extract a heading written as a standalone bold Markdown line."""

    Match = re.fullmatch(r"\*\*(.+?)\*\*", block.strip())
    if Match:
        return Match.group(1)
    return None


def _inline_markup_to_html(text: str) -> str:
    """Escape text and preserve simple emphasis used by generated drafts."""

    Escaped = escape(" ".join(text.splitlines()))
    Escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", Escaped)
    Escaped = re.sub(r"\*(.+?)\*", r"<em>\1</em>", Escaped)
    return Escaped


def _render_sources(draft: DraftIssue, research: ResearchBrief | None) -> str:
    """Render source metadata as an HTML list."""

    return _wrap_source_items(_source_items(draft, research))


def _source_items(draft: DraftIssue, research: ResearchBrief | None) -> list[str]:
    """Return source list item HTML."""

    if research and research.SourceList:
        return [_render_research_source(Source) for Source in research.SourceList]
    return [f"<li>{escape(Source)}</li>" for Source in draft.SourcesUsed]


def _wrap_source_items(items: list[str]) -> str:
    """Wrap source list items in a section."""

    if not items:
        return ""
    return '      <section class="card"><h2>Sources</h2><ul class="sources">' + "".join(items) + "</ul></section>"


def _render_research_source(source) -> str:
    """Render one research source as an HTML list item."""

    if source.Url:
        return f'<li><a href="{escape(source.Url)}">{escape(source.Publication)}</a></li>'
    return f"<li>{escape(source.Publication)}</li>"


def _render_fact_check(report: FactCheckReport) -> str:
    """Render fact-check status as a compact review section."""

    return (
        '      <section class="card"><h2>Fact Check</h2>'
        f'<p><span class="status">{escape(str(report.OverallScore))}</span></p>'
        f"<p>{escape(report.Summary or 'No summary provided.')}</p>"
        f"<p><strong>Flags:</strong> {len(report.Flags)}</p>"
        "</section>"
    )
