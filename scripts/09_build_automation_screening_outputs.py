from __future__ import annotations

import math

import pandas as pd

from common import DATA, ensure_dirs, read_csv_if_exists, require_columns, write_csv


SAMPLE_COLUMNS = [
    "record_id",
    "title",
    "abstract",
    "automation_screening_tier",
    "automation_exclusion_reason",
    "human_validation_decision",
    "human_validation_notes",
]


def bool_series(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.upper().eq("TRUE")


def markdown_titles(df: pd.DataFrame, limit: int = 25) -> str:
    if df.empty:
        return "- None"
    rows = []
    for _, row in df.head(limit).iterrows():
        score = row.get("relevance_score", "")
        rows.append(f"- {row.get('record_id', '')}: {row.get('title', '')} (score: {score})")
    return "\n".join(rows)


def examples_by_reason(df: pd.DataFrame) -> str:
    if df.empty:
        return "- None"
    rows = []
    for reason, group in df.groupby("automation_exclusion_reason", dropna=False):
        label = reason or "missing_reason"
        rows.append(f"### {label}")
        for _, row in group.head(5).iterrows():
            rows.append(f"- {row.get('record_id', '')}: {row.get('title', '')}")
    return "\n".join(rows)


def main() -> None:
    ensure_dirs()
    screening_path = DATA / "manual" / "screening_decisions.csv"
    screening = read_csv_if_exists(screening_path)
    require_columns(
        screening,
        [
            "record_id",
            "title",
            "abstract",
            "relevance_score",
            "automation_screening_tier",
            "automation_exclusion_candidate",
            "automation_exclusion_reason",
            "human_title_abstract_decision",
        ],
        str(screening_path),
    )

    screening["validation_sample_flag"] = screening.get("validation_sample_flag", "")
    scores = pd.to_numeric(screening["relevance_score"], errors="coerce").fillna(0)
    automation_excluded = screening[
        screening["human_title_abstract_decision"].fillna("").astype(str).str.lower().eq("automation_exclude")
    ].copy()
    sample_size = min(len(automation_excluded), max(math.ceil(len(automation_excluded) * 0.10), 25)) if len(automation_excluded) else 0
    random_sample = automation_excluded.sample(n=sample_size, random_state=20260618) if sample_size else automation_excluded
    ambiguous = automation_excluded[
        (pd.to_numeric(automation_excluded["relevance_score"], errors="coerce").fillna(0) >= 4)
        | automation_excluded["automation_exclusion_reason"].fillna("").astype(str).eq("other")
        | automation_excluded["automation_confidence_note"].fillna("").astype(str).str.contains("manual|uncertain|ambiguous", case=False, regex=True)
    ]
    validation_sample = pd.concat([random_sample, ambiguous], ignore_index=True).drop_duplicates("record_id")
    validation_sample["human_validation_decision"] = ""
    validation_sample["human_validation_notes"] = ""
    write_csv(validation_sample[SAMPLE_COLUMNS], DATA / "manual" / "automation_exclusion_validation_sample.csv")

    screening.loc[
        screening["record_id"].isin(validation_sample["record_id"]),
        "validation_sample_flag",
    ] = "TRUE"
    screening.loc[
        ~screening["record_id"].isin(validation_sample["record_id"]),
        "validation_sample_flag",
    ] = "FALSE"
    write_csv(screening, screening_path)

    tier_counts = screening["automation_screening_tier"].value_counts().reindex(
        ["tier_1_likely_include", "tier_2_maybe", "tier_3_likely_exclude", "tier_4_obvious_exclude"],
        fill_value=0,
    )
    remaining_manual = len(screening) - len(automation_excluded)
    remaining_percent = (remaining_manual / len(screening) * 100) if len(screening) else 0
    sorted_screening = screening.assign(_score=scores).sort_values("_score", ascending=False)
    tier_1 = sorted_screening[sorted_screening["automation_screening_tier"].eq("tier_1_likely_include")]
    tier_2 = sorted_screening[sorted_screening["automation_screening_tier"].eq("tier_2_maybe")]

    report = f"""# Automation Screening Report

## Summary Counts

- Total records: {len(screening)}
- Tier 1 likely include: {tier_counts["tier_1_likely_include"]}
- Tier 2 maybe: {tier_counts["tier_2_maybe"]}
- Tier 3 likely exclude: {tier_counts["tier_3_likely_exclude"]}
- Tier 4 obvious exclude: {tier_counts["tier_4_obvious_exclude"]}
- Records marked automation_exclude: {len(automation_excluded)}
- Records still requiring manual screening: {remaining_manual}
- Percent still requiring manual screening: {remaining_percent:.1f}%
- Validation sample size: {len(validation_sample)}

## Manual Screening Burden

The estimated manual title/abstract screening burden after automation is {remaining_manual} records. Tier 1 and tier 2 records should be screened first. Tier 3 records should receive a quick human check if time allows. Automation-excluded records require validation sampling before they are treated as final exclusions.

## Top 25 Tier 1 Likely Include Titles

{markdown_titles(tier_1)}

## Top 25 Tier 2 Maybe Titles

{markdown_titles(tier_2)}

## Automation Exclude Examples By Reason

{examples_by_reason(automation_excluded)}

## Validation Warning

Automation-excluded records were coded by a rule-based script, not by human screening. Review `data/manual/automation_exclusion_validation_sample.csv` and mark each sampled record as `confirm_exclude`, `rescue_for_manual_screening`, or `unsure`.

## PRISMA Reporting

Records with `human_title_abstract_decision == automation_exclude` should be reported separately as `records_marked_ineligible_by_automation`. Human title/abstract exclusions remain separate as `records_excluded_human`. Final full-text inclusion decisions must be made by human review.
"""
    (DATA / "outputs" / "automation_screening_report.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
