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
    "human_title_abstract_decision",
    "human_title_abstract_exclusion_reason",
    "full_text_needed",
    "notes",
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
    screening = pd.DataFrame()
    for column in SCREENING_COLUMNS:
        screening[column] = records[column] if column in records.columns else ""
    write_csv(screening, DATA / "manual" / "screening_decisions.csv")
    full_text = pd.DataFrame({"record_id": records["record_id"], "citation": records.apply(citation, axis=1)})
    for column in FULL_TEXT_COLUMNS:
        if column not in full_text.columns:
            full_text[column] = ""
    write_csv(full_text[FULL_TEXT_COLUMNS], DATA / "manual" / "full_text_review.csv")


if __name__ == "__main__":
    main()
