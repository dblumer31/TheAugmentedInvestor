"""Markdown export for final or review-ready issues."""

from __future__ import annotations

import re

from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import FactCheckReport
from augmented_investor.models.research import ResearchBrief


def export_markdown(
    draft: DraftIssue,
    research: ResearchBrief | None = None,
    fact_check: FactCheckReport | None = None,
) -> str:
    """Render a draft and review metadata as Markdown."""

    Sections = [
        f"# {draft.Title}",
        f"**Subject:** {draft.SubjectLine}",
        f"**Subtitle:** {draft.Subtitle}",
        "",
        draft.Lede,
        "",
        _body_to_markdown(draft.Body),
    ]
    Sources = _render_sources(draft, research)
    if Sources:
        Sections.extend(["", "## Sources", "", Sources])
    if fact_check is not None:
        Sections.extend(["", "## Fact Check", "", _render_fact_check(fact_check)])
    return "\n".join(Sections).strip() + "\n"


def _body_to_markdown(body: str) -> str:
    """Convert the simple HTML emitted by the writer into readable Markdown."""

    Markdown = body.replace("</p>", "\n\n").replace("<br>", "\n").replace("<br />", "\n")
    Markdown = re.sub(r"<h([1-6])>(.*?)</h\1>", _heading_replacement, Markdown)
    Markdown = re.sub(r"<li>(.*?)</li>", r"- \1\n", Markdown)
    Markdown = re.sub(r"</?(ul|ol)>", "", Markdown)
    Markdown = re.sub(r"<[^>]+>", "", Markdown)
    return re.sub(r"\n{3,}", "\n\n", Markdown).strip()


def _heading_replacement(match: re.Match[str]) -> str:
    """Return Markdown heading syntax for an HTML heading tag."""

    Level = int(match.group(1))
    Text = match.group(2)
    return f"{'#' * Level} {Text}\n"


def _render_sources(draft: DraftIssue, research: ResearchBrief | None) -> str:
    """Render sources from research first, then draft source names."""

    if research and research.SourceList:
        return _render_research_sources(research)
    return "\n".join(f"- {Source}" for Source in draft.SourcesUsed)


def _render_research_sources(research: ResearchBrief) -> str:
    """Render research source entries."""

    return "\n".join(_render_research_source(Source) for Source in research.SourceList)


def _render_research_source(source) -> str:
    """Render one research source entry."""

    if source.Url:
        return f"- {source.Publication} ({source.Url})"
    return f"- {source.Publication}"


def _render_fact_check(report: FactCheckReport) -> str:
    """Render a concise fact-check status block."""

    Lines = [
        f"- Overall score: {report.OverallScore}",
        f"- Summary: {report.Summary or 'No summary provided.'}",
    ]
    if report.Flags:
        Lines.append(f"- Flags: {len(report.Flags)}")
    return "\n".join(Lines)
