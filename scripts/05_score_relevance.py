from __future__ import annotations

import pandas as pd

from common import DATA, ensure_dirs, normalize_text, read_csv_if_exists, require_columns, write_csv


TERM_GROUPS = {
    "medicaid_chip": ["medicaid", "chip", "children health insurance", "children s health insurance"],
    "postpartum": ["postpartum", "post partum", "postnatal", "pregnancy", "pregnant", "maternal", "after delivery", "after childbirth"],
    "coverage_policy": ["coverage", "eligibility", "extension", "continuous coverage", "churn", "redetermination", "waiver", "state plan", "section 1115", "insurance continuity"],
    "outcomes": ["access", "continuity", "behavioral health", "morbidity", "mortality", "equity", "disparities", "postpartum visit", "emergency department", "ed use", "care coordination"],
    "us_state_policy": ["united states", "u s", "state", "medicaid agency", "section 1115", "cms", "federal", "county"],
}

POLICY_TERMS = [
    "policy",
    "policies",
    "waiver",
    "section 1115",
    "state plan",
    "eligibility",
    "redetermination",
    "extension",
    "continuous coverage",
    "churn",
]

CLINICAL_ONLY_TERMS = [
    "randomized trial",
    "clinical trial",
    "biomarker",
    "laboratory",
    "pathophysiology",
    "pharmacokinetic",
    "neonatal intensive care",
    "ultrasound",
    "cesarean",
    "hemorrhage",
    "preterm",
]

NON_US_TERMS = [
    "canada",
    "australia",
    "united kingdom",
    "england",
    "europe",
    "india",
    "china",
    "brazil",
    "ghana",
    "kenya",
    "ethiopia",
    "nigeria",
    "south africa",
]

INSURANCE_CONNECTION_TERMS = [
    "insurance",
    "insured",
    "uninsured",
    "coverage",
    "payer",
    "payor",
    "public insurance",
    "affordable care act",
    "aca",
]


def score_text(text: str) -> tuple[int, dict[str, int]]:
    normalized = normalize_text(text)
    details = {}
    total = 0
    for group, terms in TERM_GROUPS.items():
        hits = sum(1 for term in terms if normalize_text(term) in normalized)
        details[f"{group}_hits"] = hits
        total += min(hits, 3)
    return total, details


def suggestion(score: int) -> str:
    if score >= 8:
        return "likely_include"
    if score >= 4:
        return "maybe"
    return "likely_exclude"


def has_any(normalized: str, terms: list[str]) -> bool:
    return any(normalize_text(term) in normalized for term in terms)


def bool_text(value: bool) -> str:
    return "TRUE" if value else "FALSE"


def automation_classification(text: str, score: int) -> dict[str, str]:
    normalized = normalize_text(text)
    flags = {
        "has_medicaid_chip": has_any(normalized, TERM_GROUPS["medicaid_chip"]),
        "has_postpartum_pregnancy": has_any(normalized, TERM_GROUPS["postpartum"]),
        "has_coverage_policy": has_any(normalized, TERM_GROUPS["coverage_policy"]),
        "has_access_outcome_equity": has_any(normalized, TERM_GROUPS["outcomes"]),
        "has_us_context": has_any(normalized, TERM_GROUPS["us_state_policy"]) or has_any(normalized, TERM_GROUPS["medicaid_chip"]),
        "has_clinical_only_terms": has_any(normalized, CLINICAL_ONLY_TERMS),
        "has_policy_terms": has_any(normalized, POLICY_TERMS),
    }
    has_insurance_connection = flags["has_medicaid_chip"] or has_any(normalized, INSURANCE_CONNECTION_TERMS)
    core_flags = [
        flags["has_medicaid_chip"],
        flags["has_postpartum_pregnancy"],
        flags["has_coverage_policy"],
        flags["has_access_outcome_equity"],
    ]
    missing_count = len([flag for flag in core_flags if not flag])
    reason = ""
    tier = "tier_2_maybe"

    if (
        (not flags["has_medicaid_chip"] and not has_insurance_connection)
        or (
            not flags["has_postpartum_pregnancy"]
            and not flags["has_coverage_policy"]
            and not flags["has_access_outcome_equity"]
        )
        or (
            flags["has_clinical_only_terms"]
            and not flags["has_policy_terms"]
            and not flags["has_coverage_policy"]
            and not flags["has_access_outcome_equity"]
        )
    ):
        tier = "tier_4_obvious_exclude"
        if not flags["has_medicaid_chip"] and not has_insurance_connection:
            reason = "missing_medicaid_chip"
        elif not flags["has_postpartum_pregnancy"]:
            reason = "missing_postpartum_pregnancy"
        elif flags["has_clinical_only_terms"]:
            reason = "clinical_only_no_policy_or_coverage"
        else:
            reason = "other"
    elif all(core_flags):
        tier = "tier_1_likely_include"
    elif flags["has_medicaid_chip"] and flags["has_postpartum_pregnancy"]:
        tier = "tier_2_maybe"
        if not flags["has_coverage_policy"]:
            reason = "missing_coverage_policy"
        elif not flags["has_access_outcome_equity"]:
            reason = "missing_access_outcome_equity"
    elif any(core_flags) and missing_count >= 2:
        tier = "tier_3_likely_exclude"
        if not flags["has_postpartum_pregnancy"]:
            reason = "missing_postpartum_pregnancy"
        elif not flags["has_coverage_policy"]:
            reason = "missing_coverage_policy"
        elif not flags["has_access_outcome_equity"]:
            reason = "missing_access_outcome_equity"
        elif not flags["has_us_context"]:
            reason = "not_us_based"
        else:
            reason = "other"

    if not flags["has_us_context"] and has_any(normalized, NON_US_TERMS) and tier != "tier_4_obvious_exclude":
        tier = "tier_3_likely_exclude"
        reason = "not_us_based"

    confidence_note = {
        "tier_1_likely_include": "Contains all four core concepts; prioritize for manual screening.",
        "tier_2_maybe": "Contains Medicaid/CHIP and postpartum/pregnancy but is missing one adjacent concept; manual screening needed.",
        "tier_3_likely_exclude": "Missing multiple core concepts; quick human check recommended if time allows.",
        "tier_4_obvious_exclude": "Clear automation exclusion candidate; validate through sampled human review.",
    }[tier]

    return {
        **{name: bool_text(value) for name, value in flags.items()},
        "automation_screening_tier": tier,
        "automation_exclusion_candidate": bool_text(tier == "tier_4_obvious_exclude"),
        "automation_exclusion_reason": reason if tier == "tier_4_obvious_exclude" else "",
        "automation_confidence_note": confidence_note,
    }


def main() -> None:
    ensure_dirs()
    records = read_csv_if_exists(DATA / "processed" / "deduplicated_records.csv")
    require_columns(records, ["record_id", "title", "abstract"], "deduplicated_records.csv")
    scored = []
    for _, row in records.iterrows():
        text = f"{row.get('title', '')} {row.get('abstract', '')}"
        score, details = score_text(text)
        updated = row.to_dict()
        updated.update(details)
        updated["relevance_score"] = score
        updated["automation_suggestion"] = suggestion(score)
        updated.update(automation_classification(text, score))
        scored.append(updated)
    write_csv(pd.DataFrame(scored), DATA / "processed" / "scored_records.csv")


if __name__ == "__main__":
    main()
