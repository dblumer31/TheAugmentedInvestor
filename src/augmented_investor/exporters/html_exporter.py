"""HTML export for final or review-ready issues."""

from __future__ import annotations

from html import escape

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
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            f"  <title>{escape(draft.Title)}</title>",
            "</head>",
            "<body>",
            f"  <h1>{escape(draft.Title)}</h1>",
            f"  <p><strong>Subject:</strong> {escape(draft.SubjectLine)}</p>",
            f"  <p><strong>Subtitle:</strong> {escape(draft.Subtitle)}</p>",
            f"  <p><strong>Lede:</strong> {escape(draft.Lede)}</p>",
            '  <article class="issue-body">',
            draft.Body,
            "  </article>",
            SourceHtml,
            FactCheckHtml,
            "</body>",
            "</html>",
            "",
        ]
    )


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
    return "  <section><h2>Sources</h2><ul>" + "".join(items) + "</ul></section>"


def _render_research_source(source) -> str:
    """Render one research source as an HTML list item."""

    if source.Url:
        return f'<li><a href="{escape(source.Url)}">{escape(source.Publication)}</a></li>'
    return f"<li>{escape(source.Publication)}</li>"


def _render_fact_check(report: FactCheckReport) -> str:
    """Render fact-check status as a compact review section."""

    return (
        "  <section><h2>Fact Check</h2>"
        f"<p><strong>Overall score:</strong> {escape(str(report.OverallScore))}</p>"
        f"<p>{escape(report.Summary or 'No summary provided.')}</p>"
        f"<p><strong>Flags:</strong> {len(report.Flags)}</p>"
        "</section>"
    )
