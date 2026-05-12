"""Deterministic helpers for Fix Pass repairability and audit labels."""

from __future__ import annotations

from dataclasses import dataclass

from augmented_investor.models.common import ClaimType
from augmented_investor.models.fact_check import FactCheckCategory, FactCheckFlag, TriageBucket


SOURCE_QUALITY_CATEGORIES = {
    FactCheckCategory.WeakSourceForQuantClaim,
    FactCheckCategory.SourceQualityMismatch,
    FactCheckCategory.UnverifiedMarketReturn,
    FactCheckCategory.OverreliesOnBlogOrSubstack,
    FactCheckCategory.ExactQuoteMissing,
    FactCheckCategory.CitationPresentButClaimUnproven,
    FactCheckCategory.SourceDoesNotSupportClaim,
}


@dataclass(frozen=True)
class FixPassPartition:
    """Repairable and skipped fact-check flags for a fix pass."""

    RepairableFlags: list[FactCheckFlag]
    SkippedFlags: list[FactCheckFlag]


def partition_fixable_flags(flags: list[FactCheckFlag]) -> FixPassPartition:
    """Split fact-check flags into repairable and skipped groups."""

    RepairableFlags: list[FactCheckFlag] = []
    SkippedFlags: list[FactCheckFlag] = []
    for Flag in flags:
        if _is_repairable(Flag):
            RepairableFlags.append(Flag)
        else:
            SkippedFlags.append(Flag)
    return FixPassPartition(RepairableFlags=RepairableFlags, SkippedFlags=SkippedFlags)


def action_label_for_flag(flag: FactCheckFlag) -> str:
    """Return the required audit action label for a fact-check flag."""

    if flag.Category == FactCheckCategory.WeakSourceForQuantClaim:
        return "softened weak-source quant"
    if flag.Category in {
        FactCheckCategory.OverreliesOnBlogOrSubstack,
        FactCheckCategory.UnverifiedMarketReturn,
    }:
        return "softened weak-source quant"
    if flag.Category == FactCheckCategory.InvestmentAdvice:
        return "removed claim"
    if flag.Triage == TriageBucket.GeneralizeOrRemoveUnsupportedSpecificity:
        return "generalized claim"
    if flag.Category == FactCheckCategory.MissingUrl:
        return "marked source-limited"
    if flag.ClaimType in {ClaimType.MarketReturn, ClaimType.Valuation}:
        return "removed unsupported specificity"
    return "marked source-limited"


def addressed_flag_categories(flags: list[FactCheckFlag]) -> list[str]:
    """Return stable category values for repaired flags."""

    return [Flag.Category.value for Flag in flags]


def fix_pass_actions(flags: list[FactCheckFlag]) -> list[str]:
    """Return stable action labels for repaired flags."""

    return [action_label_for_flag(Flag) for Flag in flags]


def _is_repairable(flag: FactCheckFlag) -> bool:
    """Return true when Fix Pass can act without fabricating new evidence."""

    if flag.Triage != TriageBucket.NeedsResearchAddendum:
        return True
    return flag.Category in SOURCE_QUALITY_CATEGORIES
