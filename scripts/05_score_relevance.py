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
        scored.append(updated)
    write_csv(pd.DataFrame(scored), DATA / "processed" / "scored_records.csv")


if __name__ == "__main__":
    main()
