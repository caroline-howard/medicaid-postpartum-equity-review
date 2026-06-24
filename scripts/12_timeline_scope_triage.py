from __future__ import annotations

from collections import Counter

import pandas as pd

from common import DATA, ensure_dirs, normalize_text, read_csv_if_exists, require_columns, write_csv


SCREENING_CSV = DATA / "manual" / "screening_decisions.csv"
REPORT_PATH = DATA / "outputs" / "timeline_scope_triage_report.md"

ELIGIBLE_FIRST_PASS = {"include_for_full_text", "maybe"}

TIMING_TERMS = [
    "2021",
    "2022",
    "2023",
    "2024",
    "2025",
    "American Rescue Plan",
    "American Rescue Plan Act",
    "ARPA",
    "Rescue Plan",
    "post-2021",
    "after 2021",
]

COVERAGE_EXTENSION_TERMS = [
    "12-month",
    "twelve-month",
    "12 months",
    "twelve months",
    "1 year",
    "one year",
    "extended postpartum coverage",
    "postpartum coverage extension",
    "postpartum Medicaid extension",
    "postpartum Medicaid coverage extension",
    "postpartum eligibility extension",
    "continuous postpartum coverage",
    "postpartum continuous coverage",
]

POLICY_MECHANISM_TERMS = [
    "Medicaid",
    "CHIP",
    "state plan amendment",
    "SPA",
    "Section 1115",
    "1115 waiver",
    "waiver",
    "state adoption",
    "implementation",
    "state policy",
    "federal policy",
    "CMS",
    "Medicaid agency",
]

OUTCOME_TERMS = [
    "access",
    "access to care",
    "coverage continuity",
    "continuity of coverage",
    "continuity of care",
    "insurance continuity",
    "insurance churn",
    "churn",
    "redetermination",
    "postpartum visit",
    "postpartum care",
    "behavioral health",
    "mental health",
    "morbidity",
    "mortality",
    "equity",
    "disparities",
    "racial",
    "ethnic",
    "rural",
    "low-income",
    "immigrant",
    "vulnerable",
]

MEDICAID_CHIP_TERMS = ["Medicaid", "CHIP"]
POSTPARTUM_TERMS = ["postpartum", "post-partum", "postnatal", "after delivery", "after childbirth"]
GENERAL_EXTENSION_TERMS = ["coverage", "eligibility", "extension", "continuous coverage", "churn", "redetermination"]

TRIAGE_COLUMNS = [
    "timeline_scope_score",
    "timeline_scope_tier",
    "timeline_scope_matched_terms",
    "automation_narrowing_suggestion",
    "automation_narrowing_note",
]

TIER_ORDER = {
    "tier_1_strong_match": 1,
    "tier_2_possible_match": 2,
    "tier_3_background_context": 3,
    "tier_4_likely_out_of_scope": 4,
}

SUGGESTION_BY_TIER = {
    "tier_1_strong_match": "prioritize_for_human_review",
    "tier_2_possible_match": "possible_retain",
    "tier_3_background_context": "likely_background_only",
    "tier_4_likely_out_of_scope": "likely_exclude_after_narrowing",
}

NOTE_BY_TIER = {
    "tier_1_strong_match": "Mentions Medicaid/CHIP, postpartum, 12-month or extended postpartum coverage, and a state/federal policy mechanism.",
    "tier_2_possible_match": "Mentions Medicaid/CHIP and postpartum with extension, coverage, eligibility, or continuity language, but timing or 12-month policy language is less explicit.",
    "tier_3_background_context": "May provide maternal health, Medicaid, equity, or policy context but does not clearly address post-2021 12-month postpartum Medicaid extension adoption or implementation.",
    "tier_4_likely_out_of_scope": "Does not clearly address 12-month postpartum Medicaid coverage extension, post-2021 state adoption, or implementation.",
}


def matched_terms(normalized: str, terms: list[str]) -> list[str]:
    padded = f" {normalized} "
    matches = []
    for term in terms:
        normalized_term = normalize_text(term)
        if normalized_term and f" {normalized_term} " in padded:
            matches.append(term)
    return matches


def cap_points(matches: list[str], weight: int, cap: int) -> int:
    return min(len(matches) * weight, cap)


def score_record(row: pd.Series) -> dict[str, str]:
    text = f"{row.get('title', '')} {row.get('abstract', '')}"
    normalized = normalize_text(text)
    matches = {
        "timing": matched_terms(normalized, TIMING_TERMS),
        "coverage_extension": matched_terms(normalized, COVERAGE_EXTENSION_TERMS),
        "policy_mechanism": matched_terms(normalized, POLICY_MECHANISM_TERMS),
        "outcome": matched_terms(normalized, OUTCOME_TERMS),
        "medicaid_chip": matched_terms(normalized, MEDICAID_CHIP_TERMS),
        "postpartum": matched_terms(normalized, POSTPARTUM_TERMS),
        "general_extension": matched_terms(normalized, GENERAL_EXTENSION_TERMS),
    }

    has_medicaid_chip = bool(matches["medicaid_chip"])
    has_postpartum = bool(matches["postpartum"])
    has_timing = bool(matches["timing"])
    has_coverage_extension = bool(matches["coverage_extension"])
    has_policy_mechanism = bool(matches["policy_mechanism"])
    has_general_extension = bool(matches["general_extension"])
    has_context = any(matches[group] for group in ["outcome", "policy_mechanism", "medicaid_chip", "postpartum"])

    score = 0
    score += 2 if has_medicaid_chip else 0
    score += 2 if has_postpartum else 0
    score += cap_points(matches["timing"], weight=1, cap=3)
    score += cap_points(matches["coverage_extension"], weight=3, cap=6)
    score += cap_points(matches["policy_mechanism"], weight=2, cap=6)
    score += cap_points(matches["outcome"], weight=1, cap=4)
    if has_coverage_extension and has_policy_mechanism:
        score += 4
    if has_timing and has_coverage_extension:
        score += 2

    if has_medicaid_chip and has_postpartum and has_coverage_extension and has_policy_mechanism:
        tier = "tier_1_strong_match"
    elif has_medicaid_chip and has_postpartum and (has_coverage_extension or has_general_extension):
        tier = "tier_2_possible_match"
    elif has_context:
        tier = "tier_3_background_context"
    else:
        tier = "tier_4_likely_out_of_scope"

    matched_parts = []
    for group in ["timing", "coverage_extension", "policy_mechanism", "outcome", "medicaid_chip", "postpartum", "general_extension"]:
        if matches[group]:
            matched_parts.append(f"{group}: {', '.join(matches[group])}")

    return {
        "timeline_scope_score": str(score),
        "timeline_scope_tier": tier,
        "timeline_scope_matched_terms": " | ".join(matched_parts),
        "automation_narrowing_suggestion": SUGGESTION_BY_TIER[tier],
        "automation_narrowing_note": NOTE_BY_TIER[tier],
    }


def markdown_table(rows: pd.DataFrame, columns: list[str]) -> list[str]:
    if rows.empty:
        return ["_None._"]
    output = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in rows.iterrows():
        values = [str(row.get(column, "")).replace("\n", " ").replace("|", "/") for column in columns]
        output.append("| " + " | ".join(values) + " |")
    return output


def write_report(df: pd.DataFrame, eligible: pd.DataFrame) -> None:
    tier_counts = eligible["timeline_scope_tier"].value_counts().to_dict()
    suggestion_counts = eligible["automation_narrowing_suggestion"].value_counts().to_dict()

    sorted_eligible = eligible.assign(
        _tier_order=eligible["timeline_scope_tier"].map(TIER_ORDER).fillna(9),
        _score=pd.to_numeric(eligible["timeline_scope_score"], errors="coerce").fillna(0),
    ).sort_values(["_tier_order", "_score", "record_id"], ascending=[True, False, True])

    top_strong = sorted_eligible.head(30)
    background = sorted_eligible[sorted_eligible["timeline_scope_tier"].eq("tier_3_background_context")].head(30)
    out_of_scope = sorted_eligible[sorted_eligible["timeline_scope_tier"].eq("tier_4_likely_out_of_scope")].head(30)

    term_counter: Counter[str] = Counter()
    for value in eligible["timeline_scope_matched_terms"].fillna(""):
        for group_part in str(value).split(" | "):
            if ": " not in group_part:
                continue
            _, terms = group_part.split(": ", 1)
            for term in terms.split(", "):
                if term:
                    term_counter[term] += 1

    lines = [
        "# Timeline Scope Triage Report",
        "",
        "This report ranks the 166 first-pass `include_for_full_text` or `maybe` records for narrowed second-pass screening around post-2021 state adoption and implementation of 12-month postpartum Medicaid coverage extensions.",
        "",
        "These are automation suggestions only. They do not make final inclusion, exclusion, narrowed screening, full-text, or synthesis decisions.",
        "",
        f"- Total records in screening file: {len(df)}",
        f"- Total second-pass eligible records: {len(eligible)}",
        "",
        "## Count By Timeline Scope Tier",
        "",
    ]
    for tier in TIER_ORDER:
        lines.append(f"- `{tier}`: {tier_counts.get(tier, 0)}")

    lines.extend(["", "## Count By Automation Narrowing Suggestion", ""])
    for suggestion in ["prioritize_for_human_review", "possible_retain", "likely_background_only", "likely_exclude_after_narrowing"]:
        lines.append(f"- `{suggestion}`: {suggestion_counts.get(suggestion, 0)}")

    table_columns = ["record_id", "year", "timeline_scope_score", "timeline_scope_tier", "automation_narrowing_suggestion", "title"]
    lines.extend(["", "## Top 30 Strongest Matches", ""])
    lines.extend(markdown_table(top_strong, table_columns))
    lines.extend(["", "## 30 Likely Background/Context Records", ""])
    lines.extend(markdown_table(background, table_columns))
    lines.extend(["", "## 30 Likely Out-Of-Scope Records", ""])
    lines.extend(markdown_table(out_of_scope, table_columns))
    lines.extend(["", "## Common Matched Terms", ""])
    if term_counter:
        for term, count in term_counter.most_common(30):
            lines.append(f"- `{term}`: {count}")
    else:
        lines.append("_No matched terms._")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    df = read_csv_if_exists(SCREENING_CSV)
    require_columns(df, ["record_id", "title", "abstract", "human_title_abstract_decision"], str(SCREENING_CSV))

    for column in TRIAGE_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    eligible_mask = df["human_title_abstract_decision"].fillna("").astype(str).isin(ELIGIBLE_FIRST_PASS)
    df.loc[~eligible_mask, TRIAGE_COLUMNS] = ""

    for index, row in df.loc[eligible_mask].iterrows():
        scored = score_record(row)
        for column, value in scored.items():
            df.at[index, column] = value

    write_csv(df, SCREENING_CSV)
    write_report(df, df.loc[eligible_mask].copy())
    print(f"Wrote timeline/scope triage for {int(eligible_mask.sum())} second-pass eligible records.")
    print(f"Wrote {REPORT_PATH}.")


if __name__ == "__main__":
    main()
