from __future__ import annotations

import pandas as pd

from common import DATA, ensure_dirs, read_csv_if_exists, require_columns, write_csv


SCREENING_COLUMNS = [
    "record_id",
    "title",
    "abstract",
    "year",
    "journal",
    "doi",
    "pmid",
    "url",
    "source_database",
    "relevance_score",
    "automation_suggestion",
    "automation_screening_tier",
    "automation_exclusion_candidate",
    "automation_exclusion_reason",
    "automation_confidence_note",
    "validation_sample_flag",
    "human_title_abstract_decision",
    "human_title_abstract_exclusion_reason",
    "full_text_needed",
    "notes",
]

PRESERVE_SCREENING_COLUMNS = [
    "human_title_abstract_decision",
    "human_title_abstract_exclusion_reason",
    "full_text_needed",
    "notes",
    "validation_sample_flag",
]

FULL_TEXT_COLUMNS = [
    "record_id",
    "citation",
    "full_text_retrieved",
    "retrieval_notes",
    "human_full_text_decision",
    "full_text_exclusion_reason",
    "study_or_report_type",
    "include_in_evidence_table",
    "notes",
]


def citation(row: pd.Series) -> str:
    pieces = [row.get("authors", ""), f"({row.get('year', '')})." if row.get("year", "") else "", row.get("title", ""), row.get("journal", "")]
    return " ".join(str(piece).strip() for piece in pieces if str(piece).strip())


def main() -> None:
    ensure_dirs()
    records = read_csv_if_exists(DATA / "processed" / "scored_records.csv")
    if records.empty:
        records = read_csv_if_exists(DATA / "processed" / "deduplicated_records.csv")
    require_columns(records, ["record_id", "title", "abstract"], "scored_records.csv or deduplicated_records.csv")
    existing_screening = read_csv_if_exists(DATA / "manual" / "screening_decisions.csv")
    existing_by_id = existing_screening.set_index("record_id") if "record_id" in existing_screening.columns else pd.DataFrame()
    screening = pd.DataFrame()
    for column in SCREENING_COLUMNS:
        screening[column] = records[column] if column in records.columns else ""
    if not existing_by_id.empty:
        for column in PRESERVE_SCREENING_COLUMNS:
            if column in existing_by_id.columns:
                screening[column] = screening["record_id"].map(existing_by_id[column]).fillna(screening[column])
    candidate_mask = screening["automation_exclusion_candidate"].astype(str).str.upper().eq("TRUE")
    stale_auto_mask = (
        screening["human_title_abstract_decision"].fillna("").astype(str).str.lower().eq("automation_exclude")
        & ~candidate_mask
    )
    screening.loc[stale_auto_mask, "human_title_abstract_decision"] = ""
    screening.loc[stale_auto_mask, "human_title_abstract_exclusion_reason"] = ""
    screening.loc[stale_auto_mask, "notes"] = ""
    blank_human_mask = screening["human_title_abstract_decision"].fillna("").astype(str).str.strip().eq("")
    auto_mask = candidate_mask & blank_human_mask
    screening.loc[auto_mask, "human_title_abstract_decision"] = "automation_exclude"
    screening.loc[auto_mask, "human_title_abstract_exclusion_reason"] = screening.loc[auto_mask, "automation_exclusion_reason"]
    screening.loc[auto_mask, "notes"] = "Automation-coded exclusion candidate; requires validation sampling."
    write_csv(screening, DATA / "manual" / "screening_decisions.csv")

    existing_full_text = read_csv_if_exists(DATA / "manual" / "full_text_review.csv")
    existing_full_text_by_id = existing_full_text.set_index("record_id") if "record_id" in existing_full_text.columns else pd.DataFrame()
    full_text = pd.DataFrame({"record_id": records["record_id"], "citation": records.apply(citation, axis=1)})
    for column in FULL_TEXT_COLUMNS:
        if column not in full_text.columns:
            full_text[column] = ""
    if not existing_full_text_by_id.empty:
        for column in FULL_TEXT_COLUMNS:
            if column in ["record_id", "citation"]:
                continue
            if column in existing_full_text_by_id.columns:
                full_text[column] = full_text["record_id"].map(existing_full_text_by_id[column]).fillna(full_text[column])
    write_csv(full_text[FULL_TEXT_COLUMNS], DATA / "manual" / "full_text_review.csv")


if __name__ == "__main__":
    main()
