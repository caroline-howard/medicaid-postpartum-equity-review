from __future__ import annotations

import pandas as pd

from common import DATA, ensure_dirs, read_csv_if_exists, write_csv


COLUMNS = [
    "record_id",
    "citation",
    "source_type",
    "year",
    "state_or_states",
    "population",
    "policy_feature",
    "study_design",
    "data_source",
    "outcomes",
    "equity_focus",
    "key_finding",
    "limitations",
    "program_evaluation_implication",
    "quality_or_relevance_note",
    "include_in_final_synthesis",
]


def main() -> None:
    ensure_dirs()
    full_text = read_csv_if_exists(DATA / "manual" / "full_text_review.csv")
    rows = []
    if not full_text.empty:
        included = full_text[full_text.get("include_in_evidence_table", "").astype(str).str.lower().isin(["yes", "true", "1"])]
        for _, row in included.iterrows():
            rows.append({"record_id": row.get("record_id", ""), "citation": row.get("citation", "")})
    evidence = pd.DataFrame(rows, columns=["record_id", "citation"]) if rows else pd.DataFrame(columns=["record_id", "citation"])
    for column in COLUMNS:
        if column not in evidence.columns:
            evidence[column] = ""
    write_csv(evidence[COLUMNS], DATA / "outputs" / "evidence_table.csv")


if __name__ == "__main__":
    main()
