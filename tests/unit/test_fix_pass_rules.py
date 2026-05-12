"""Unit tests for deterministic fix-pass repairability helpers."""

from __future__ import annotations

from augmented_investor.models.common import ClaimType
from augmented_investor.models.fact_check import (
    ActualSourceQuality,
    FactCheckCategory,
    FactCheckFlag,
    RequiredSourceQuality,
    Severity,
    TriageBucket,
    VerificationStatus,
)
from augmented_investor.pipeline.fix_pass_rules import action_label_for_flag, partition_fixable_flags


def _flag(category: FactCheckCategory, triage: TriageBucket, claim_type: ClaimType) -> FactCheckFlag:
    """Return a fact-check flag fixture."""

    return FactCheckFlag(
        category=category,
        severity=Severity.Warning,
        excerpt="Example claim",
        issue="Issue",
        suggestion="Suggestion",
        claimType=claim_type,
        requiredSourceQuality=RequiredSourceQuality.Any,
        actualSourceQuality=ActualSourceQuality.BlogOrSubstack,
        verificationStatus=VerificationStatus.Unsupported,
        triage=triage,
        addendumQuery="new evidence",
    )


def test_source_quality_research_addendum_flags_remain_repairable_for_removal():
    """Source-quality addendum flags can be softened or removed by Fix Pass."""

    SourceFlag = _flag(
        FactCheckCategory.OverreliesOnBlogOrSubstack,
        TriageBucket.NeedsResearchAddendum,
        ClaimType.Valuation,
    )
    NonSourceFlag = _flag(
        FactCheckCategory.MissingCounterargument,
        TriageBucket.NeedsResearchAddendum,
        ClaimType.EditorialInterpretation,
    )

    Partition = partition_fixable_flags([SourceFlag, NonSourceFlag])

    assert Partition.RepairableFlags == [SourceFlag]
    assert Partition.SkippedFlags == [NonSourceFlag]


def test_action_labels_match_fix_pass_audit_vocabulary():
    """Action labels should match the story's required audit vocabulary."""

    assert (
        action_label_for_flag(
            _flag(
                FactCheckCategory.WeakSourceForQuantClaim,
                TriageBucket.NeedsResearchAddendum,
                ClaimType.MarketReturn,
            )
        )
        == "softened weak-source quant"
    )
    assert (
        action_label_for_flag(
            _flag(
                FactCheckCategory.CitationPresentButClaimUnproven,
                TriageBucket.GeneralizeOrRemoveUnsupportedSpecificity,
                ClaimType.CompanyFinancial,
            )
        )
        == "generalized claim"
    )
    assert (
        action_label_for_flag(
            _flag(
                FactCheckCategory.MissingUrl,
                TriageBucket.FixableWithExistingResearch,
                ClaimType.EditorialInterpretation,
            )
        )
        == "marked source-limited"
    )
