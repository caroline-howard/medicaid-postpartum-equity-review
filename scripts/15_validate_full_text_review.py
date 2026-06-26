from __future__ import annotations

from datetime import datetime

from common import DATA, ensure_dirs, read_csv_if_exists


FULL_TEXT_CSV = DATA / "manual" / "full_text_review.csv"
FINAL_EVIDENCE_CSV = DATA / "outputs" / "final_evidence_table.csv"
REPORT_PATH = DATA / "outputs" / "full_text_validation_report.md"

EXPECTED_FULL_TEXT_RECORDS = 32
EXPECTED_INCLUDED = 28
EXPECTED_EXCLUDED = 4

VALID_DECISIONS = {"include_core_evidence", "exclude"}
EXTRACTION_FIELDS = [
    "study_design",
    "data_years",
    "data_source",
    "state_or_scope",
    "population",
    "medicaid_policy_mechanism",
    "outcomes",
    "equity_focus",
    "main_findings",
    "limitations",
]


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def main() -> None:
    ensure_dirs()
    full_text = read_csv_if_exists(FULL_TEXT_CSV)
    evidence = read_csv_if_exists(FINAL_EVIDENCE_CSV)

    failures: list[str] = []
    warnings: list[str] = []

    required_columns = ["record_id", "full_text_decision", "full_text_exclusion_reason"]
    missing_required = [column for column in required_columns if column not in full_text.columns]
    if missing_required:
        failures.append(f"{FULL_TEXT_CSV} is missing required columns: {', '.join(missing_required)}.")

    missing_extraction_columns = [column for column in EXTRACTION_FIELDS if column not in full_text.columns]
    if missing_extraction_columns:
        failures.append(
            f"{FULL_TEXT_CSV} is missing extraction columns: {', '.join(missing_extraction_columns)}."
        )

    if len(full_text) != EXPECTED_FULL_TEXT_RECORDS:
        failures.append(f"Expected {EXPECTED_FULL_TEXT_RECORDS} full-text records, found {len(full_text)}.")

    if not missing_required:
        decisions = full_text["full_text_decision"].map(clean)
        reasons = full_text["full_text_exclusion_reason"].map(clean)

        invalid_decisions = sorted(set(decisions) - VALID_DECISIONS)
        if invalid_decisions:
            failures.append(f"Invalid full_text_decision values found: {', '.join(invalid_decisions)}.")

        blank_decisions = int(decisions.eq("").sum())
        if blank_decisions:
            failures.append(f"{blank_decisions} full-text records have blank full_text_decision values.")

        include_mask = decisions.eq("include_core_evidence")
        exclude_mask = decisions.eq("exclude")
        included_count = int(include_mask.sum())
        excluded_count = int(exclude_mask.sum())

        if included_count != EXPECTED_INCLUDED:
            failures.append(f"Expected {EXPECTED_INCLUDED} included core evidence records, found {included_count}.")
        if excluded_count != EXPECTED_EXCLUDED:
            failures.append(f"Expected {EXPECTED_EXCLUDED} excluded full-text records, found {excluded_count}.")

        excluded_without_reason = full_text.loc[exclude_mask & reasons.eq(""), "record_id"].map(clean).tolist()
        if excluded_without_reason:
            failures.append(
                f"{len(excluded_without_reason)} excluded records are missing full_text_exclusion_reason: "
                + ", ".join(excluded_without_reason)
            )

        included_with_reason = full_text.loc[include_mask & reasons.ne(""), "record_id"].map(clean).tolist()
        if included_with_reason:
            warnings.append(
                f"{len(included_with_reason)} included records have full-text exclusion reasons filled: "
                + ", ".join(included_with_reason)
            )

        if not missing_extraction_columns:
            missing_extraction: dict[str, list[str]] = {}
            included = full_text.loc[include_mask].copy()
            for column in EXTRACTION_FIELDS:
                missing_ids = included.loc[included[column].map(clean).eq(""), "record_id"].map(clean).tolist()
                if missing_ids:
                    missing_extraction[column] = missing_ids
            if missing_extraction:
                for column, record_ids in missing_extraction.items():
                    failures.append(
                        f"Included records missing {column}: {len(record_ids)} "
                        f"({', '.join(record_ids[:10])}{'...' if len(record_ids) > 10 else ''})."
                    )

        if "record_id" in evidence.columns:
            evidence_ids = set(evidence["record_id"].map(clean))
            included_ids = set(full_text.loc[include_mask, "record_id"].map(clean))
            missing_from_evidence = sorted(included_ids - evidence_ids)
            extra_in_evidence = sorted(evidence_ids - included_ids)
            if missing_from_evidence:
                failures.append(f"{len(missing_from_evidence)} included records are missing from final_evidence_table.csv.")
            if extra_in_evidence:
                failures.append(f"{len(extra_in_evidence)} records in final_evidence_table.csv are not included core evidence.")
        else:
            failures.append(f"{FINAL_EVIDENCE_CSV} is missing record_id.")

    if len(evidence) != EXPECTED_INCLUDED:
        failures.append(f"Expected {EXPECTED_INCLUDED} final evidence table records, found {len(evidence)}.")

    decision_counts = (
        full_text.get("full_text_decision", [])
        if "full_text_decision" in full_text.columns
        else []
    )
    reason_counts = (
        full_text.get("full_text_exclusion_reason", [])
        if "full_text_exclusion_reason" in full_text.columns
        else []
    )
    status = "PASS" if not failures else "FAIL"
    lines = [
        "# Full-Text Validation Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Status: {status}",
        "",
        "## Expected Counts",
        "",
        f"- Full-text records assessed: {EXPECTED_FULL_TEXT_RECORDS}",
        f"- Included core evidence: {EXPECTED_INCLUDED}",
        f"- Excluded after full text: {EXPECTED_EXCLUDED}",
        "",
        "## Decision Counts",
        "",
    ]
    if hasattr(decision_counts, "map"):
        counts = decision_counts.map(clean).value_counts().to_dict()
        for key in ["include_core_evidence", "exclude", ""]:
            label = "(blank)" if key == "" else key
            lines.append(f"- {label}: {counts.get(key, 0)}")

    lines.extend(["", "## Exclusion Reason Counts", ""])
    if hasattr(reason_counts, "map"):
        counts = reason_counts.map(clean).value_counts().to_dict()
        for key in ["unable_to_access_full_text", "medicaid_only_payer_or_data_source", ""]:
            label = "(blank)" if key == "" else key
            lines.append(f"- {label}: {counts.get(key, 0)}")

    lines.extend(["", "## Checks", ""])
    if failures:
        for failure in failures:
            lines.append(f"- FAIL: {failure}")
    else:
        lines.append("- PASS: Full-text review has no blank decisions.")
        lines.append("- PASS: Excluded records have populated full-text exclusion reasons.")
        lines.append("- PASS: Included records have populated extraction fields.")
        lines.append("- PASS: Final evidence table contains exactly the included core evidence records.")

    if warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in warnings:
            lines.append(f"- {warning}")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH} with status {status}.")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
