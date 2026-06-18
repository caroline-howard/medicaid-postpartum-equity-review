from __future__ import annotations

import sys

import pandas as pd

from common import DATA, read_csv_if_exists, require_columns


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def main() -> None:
    errors: list[str] = []
    pubmed = read_csv_if_exists(DATA / "raw" / "pubmed_records.csv")
    screening = read_csv_if_exists(DATA / "manual" / "screening_decisions.csv")
    sample = read_csv_if_exists(DATA / "manual" / "automation_exclusion_validation_sample.csv")
    prisma = read_csv_if_exists(DATA / "outputs" / "prisma_counts.csv")
    require_columns(screening, ["record_id", "human_title_abstract_decision", "automation_exclusion_reason", "validation_sample_flag"], "screening_decisions.csv")
    require_columns(sample, ["record_id", "human_validation_decision"], "automation_exclusion_validation_sample.csv")
    require_columns(prisma, ["records_marked_ineligible_by_automation"], "prisma_counts.csv")

    decisions = screening["human_title_abstract_decision"].fillna("").astype(str).str.lower()
    auto_mask = decisions.eq("automation_exclude")
    include_mask = decisions.eq("include_for_full_text")
    if (auto_mask & include_mask).any():
        fail("A record is both automation_exclude and include_for_full_text.", errors)

    missing_reason = screening.loc[auto_mask, "automation_exclusion_reason"].fillna("").astype(str).str.strip().eq("")
    if missing_reason.any():
        fail("One or more automation_exclude records are missing automation_exclusion_reason.", errors)

    prisma_count = int(pd.to_numeric(prisma.loc[0, "records_marked_ineligible_by_automation"], errors="coerce"))
    if prisma_count != int(auto_mask.sum()):
        fail(
            f"PRISMA automation count is {prisma_count}, but screening has {int(auto_mask.sum())} automation_exclude records.",
            errors,
        )

    sampled_ids = set(sample["record_id"].fillna("").astype(str))
    flagged_ids = set(
        screening.loc[
            screening["validation_sample_flag"].fillna("").astype(str).str.upper().eq("TRUE"),
            "record_id",
        ].fillna("").astype(str)
    )
    if sampled_ids != flagged_ids:
        fail("validation_sample_flag does not match automation_exclusion_validation_sample.csv record IDs.", errors)

    if len(pubmed) != len(screening):
        fail(f"Screening file has {len(screening)} records but PubMed raw file has {len(pubmed)} records.", errors)
    if "pmid" in pubmed.columns and "pmid" in screening.columns:
        pubmed_pmids = set(pubmed["pmid"].fillna("").astype(str))
        screening_pmids = set(screening["pmid"].fillna("").astype(str))
        if pubmed_pmids != screening_pmids:
            fail("Screening PMID set does not match the original PubMed candidate set.", errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        sys.exit(1)
    print("Automation screening validation passed.")


if __name__ == "__main__":
    main()
