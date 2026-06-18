from __future__ import annotations

import pandas as pd

from common import CONFIG, DATA, ensure_dirs, read_csv_if_exists, read_yaml, write_csv


COUNT_COLUMNS = [
    "records_identified_databases",
    "records_identified_registers",
    "duplicate_records_removed",
    "records_marked_ineligible_by_automation",
    "records_removed_other_reasons",
    "records_screened",
    "records_excluded_human",
    "reports_sought_for_retrieval",
    "reports_not_retrieved",
    "reports_assessed_for_eligibility",
    "reports_excluded_wrong_population",
    "reports_excluded_wrong_policy_or_intervention",
    "reports_excluded_not_medicaid_or_chip",
    "reports_excluded_not_postpartum",
    "reports_excluded_not_us_based",
    "reports_excluded_no_relevant_outcome",
    "reports_excluded_background_only",
    "reports_excluded_opinion_without_data_or_policy_detail",
    "reports_excluded_other",
    "studies_included",
    "reports_of_included_studies",
    "record_volume_flag",
    "record_volume_note",
]


def count_value(series: pd.Series, value: str) -> int:
    return int(series.fillna("").astype(str).str.lower().eq(value).sum())


def yes_count(series: pd.Series) -> int:
    return int(series.fillna("").astype(str).str.lower().isin(["yes", "true", "1"]).sum())


def volume_flag(records_identified: int) -> tuple[str, str]:
    guidance = read_yaml(CONFIG / "search_terms.yaml").get("record_volume_guidance", {})
    narrow = int(guidance.get("potentially_too_narrow_threshold_combined_pubmed_openalex", 50))
    broad = int(guidance.get("potentially_too_broad_threshold_combined_pubmed_openalex", 750))
    if records_identified < narrow:
        return "potentially_too_narrow", "Fewer than 50 PubMed records retrieved for the main search; consider broader search terms."
    if records_identified > broad:
        return "potentially_too_broad", "More than 750 PubMed records retrieved for the main search; consider narrower terms or additional filters."
    return "within_practical_check_range", "Use targets only as quality checks; final inclusion depends on documented human decisions."


def main() -> None:
    ensure_dirs()
    search_log = read_csv_if_exists(DATA / "outputs" / "search_log.csv")
    deduped = read_csv_if_exists(DATA / "processed" / "deduplicated_records.csv")
    duplicates = read_csv_if_exists(DATA / "processed" / "duplicates_removed.csv")
    screening = read_csv_if_exists(DATA / "manual" / "screening_decisions.csv")
    full_text = read_csv_if_exists(DATA / "manual" / "full_text_review.csv")
    evidence = read_csv_if_exists(DATA / "outputs" / "evidence_table.csv")

    if "source" in search_log.columns:
        main_search_log = search_log[search_log["source"].fillna("").astype(str).str.lower().eq("pubmed")]
    else:
        main_search_log = search_log
    records_identified = int(pd.to_numeric(main_search_log.get("downloaded_count", pd.Series(dtype=int)), errors="coerce").fillna(0).sum())
    screening_decisions = screening.get("human_title_abstract_decision", pd.Series(dtype=str)).fillna("").astype(str).str.lower()
    automation_excluded = count_value(screening_decisions, "automation_exclude")
    screened = max((len(screening) if not screening.empty else len(deduped)) - automation_excluded, 0)
    full_text_decisions = full_text.get("human_full_text_decision", pd.Series(dtype=str)).fillna("").astype(str).str.lower()
    exclusion_reasons = full_text.get("full_text_exclusion_reason", pd.Series(dtype=str)).fillna("").astype(str).str.lower()
    flag, note = volume_flag(records_identified)

    counts = {
        "records_identified_databases": records_identified,
        "records_identified_registers": 0,
        "duplicate_records_removed": max(records_identified - len(deduped), 0),
        "records_marked_ineligible_by_automation": automation_excluded,
        "records_removed_other_reasons": 0,
        "records_screened": screened,
        "records_excluded_human": count_value(screening_decisions, "exclude"),
        "reports_sought_for_retrieval": yes_count(screening.get("full_text_needed", pd.Series(dtype=str))),
        "reports_not_retrieved": count_value(full_text.get("full_text_retrieved", pd.Series(dtype=str)), "no"),
        "reports_assessed_for_eligibility": int(full_text_decisions.ne("").sum()),
        "reports_excluded_wrong_population": count_value(exclusion_reasons, "wrong_population"),
        "reports_excluded_wrong_policy_or_intervention": count_value(exclusion_reasons, "wrong_policy_or_intervention"),
        "reports_excluded_not_medicaid_or_chip": count_value(exclusion_reasons, "not_medicaid_or_chip"),
        "reports_excluded_not_postpartum": count_value(exclusion_reasons, "not_postpartum"),
        "reports_excluded_not_us_based": count_value(exclusion_reasons, "not_us_based"),
        "reports_excluded_no_relevant_outcome": count_value(exclusion_reasons, "no_relevant_outcome"),
        "reports_excluded_background_only": count_value(exclusion_reasons, "background_only"),
        "reports_excluded_opinion_without_data_or_policy_detail": count_value(exclusion_reasons, "opinion_without_data_or_policy_detail"),
        "reports_excluded_other": count_value(exclusion_reasons, "other"),
        "studies_included": int(full_text_decisions.isin(["include_core_evidence"]).sum()),
        "reports_of_included_studies": len(evidence),
        "record_volume_flag": flag,
        "record_volume_note": note,
    }
    write_csv(pd.DataFrame([counts], columns=COUNT_COLUMNS), DATA / "outputs" / "prisma_counts.csv")


if __name__ == "__main__":
    main()
