"""Unit tests for Markdown and HTML issue exporters."""

from __future__ import annotations

from augmented_investor.exporters.html_exporter import export_html
from augmented_investor.exporters.markdown_exporter import export_markdown
from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import FactCheckReport
from augmented_investor.models.research import ResearchBrief, ResearchSource
from augmented_investor.models.common import SourceQuality


def _draft() -> DraftIssue:
    """Return a draft fixture for export tests."""

    return DraftIssue(
        subjectLine="AI infrastructure",
        title="The Durability Question",
        subtitle="A contrarian read",
        lede="AI demand may last.",
        body="<p>Demand is durable.</p>",
        sourcesUsed=["Company filings"],
        wordCount=120,
    )


def _markdown_style_draft() -> DraftIssue:
    """Return a draft fixture shaped like live writer output."""

    return DraftIssue(
        subjectLine="AI infrastructure",
        title="The Durability Question",
        subtitle="A contrarian read",
        lede="AI demand may last.",
        body="**The Setup**\n\nDemand is durable.\n\n*Scenario analysis - Bull:* growth continues.",
        sourcesUsed=["Company filings"],
        wordCount=120,
    )


def _research() -> ResearchBrief:
    """Return a research fixture with a source list."""

    return ResearchBrief(
        topic="AI infrastructure",
        sourceList=[
            ResearchSource(
                publication="Company filings",
                url="https://example.com/filing",
                sourceQuality=SourceQuality.CompanyFilingOrIr,
                supports="Capex claim",
            )
        ],
    )


def _fact_check() -> FactCheckReport:
    """Return a clean fact-check fixture."""

    return FactCheckReport(
        flags=[],
        sourceQualitySummary={
            "weakSourceFlags": 0,
            "unverifiedQuantClaims": 0,
            "blogOnlyClaims": 0,
            "overallSourceQuality": "strong",
        },
        overallScore="clean",
        summary="Clean.",
    )


def test_markdown_export_includes_issue_source_and_fact_check_state():
    """Markdown export should replace clipboard text output."""

    Markdown = export_markdown(_draft(), _research(), _fact_check())

    assert "# The Durability Question" in Markdown
    assert "## Sources" in Markdown
    assert "Company filings" in Markdown
    assert "Fact Check" in Markdown
    assert "Clean." in Markdown


def test_html_export_escapes_metadata_and_includes_body():
    """HTML export should include review metadata and preserve body content."""

    Html = export_html(_draft(), _research(), _fact_check())

    assert "<h1>The Durability Question</h1>" in Html
    assert "<p>Demand is durable.</p>" in Html
    assert "Company filings" in Html
    assert "Fact Check" in Html


def test_html_export_renders_markdown_style_body_as_article_html():
    """Live writer Markdown-style bodies should render as readable HTML."""

    Html = export_html(_markdown_style_draft(), _research(), _fact_check())

    assert "<style>" in Html
    assert "<h2>The Setup</h2>" in Html
    assert "<p>Demand is durable.</p>" in Html
    assert "<em>Scenario analysis - Bull:</em>" in Html
    assert "**The Setup**" not in Html
