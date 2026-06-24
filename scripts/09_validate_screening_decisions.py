from __future__ import annotations

from datetime import datetime

from common import DATA, ensure_dirs, read_csv_if_exists, require_columns


SCREENING_CSV = DATA / "manual" / "screening_decisions.csv"
BASELINE_CSV = DATA / "processed" / "deduplicated_records.csv"
REPORT_PATH = DATA / "outputs" / "screening_validation_report.md"
EXPECTED_RECORD_COUNT = 211
EXPECTED_NARROWED_RETAINED_COUNT = 32
EXPECTED_RETAINED_ROLE_COUNTS = {
    "post_2021_policy_implementation_evidence": 16,
    "pre_2021_baseline_problem_evidence": 14,
    "service_specific_medicaid_access_policy": 2,
}

VALID_DECISIONS = {"", "include_for_full_text", "maybe", "exclude"}
VALID_EXCLUSION_REASONS = {
    "",
    "wrong_population",
    "wrong_policy_or_intervention",
    "not_medicaid_or_chip",
    "not_postpartum",
    "not_us_based",
    "no_relevant_outcome",
    "background_only",
    "opinion_without_data_or_policy_detail",
    "duplicate",
    "other",
}
VALID_NARROWED_DECISIONS = {"", "retain_for_full_text", "background_only", "exclude_after_narrowing", "unsure_second_pass"}
VALID_NARROWED_REASONS = {
    "",
    "directly_about_12_month_postpartum_medicaid_extension",
    "state_adoption_or_implementation",
    "access_or_continuity_outcome",
    "equity_or_disparity_relevance",
    "not_empirical_study",
    "policy_or_commentary_only",
    "evidence_synthesis_not_primary_study",
    "broad_maternal_health_policy_only",
    "not_12_month_extension",
    "not_post_2021_relevant",
    "pre_2015_cohort",
    "not_medicaid_postpartum_policy",
    "outside_final_empirical_scope",
    "background_context_only",
    "other",
}


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def main() -> None:
    ensure_dirs()
    screening = read_csv_if_exists(SCREENING_CSV)
    baseline = read_csv_if_exists(BASELINE_CSV)
    require_columns(
        screening,
        [
            "record_id",
            "human_title_abstract_decision",
            "human_title_abstract_exclusion_reason",
            "narrowed_screening_decision",
            "narrowed_screening_reason",
            "evidence_role",
        ],
        str(SCREENING_CSV),
    )
    require_columns(baseline, ["record_id"], str(BASELINE_CSV))

    failures: list[str] = []
    warnings: list[str] = []

    if len(screening) != EXPECTED_RECORD_COUNT:
        failures.append(f"Expected {EXPECTED_RECORD_COUNT} screening records, found {len(screening)}.")
    if len(baseline) != EXPECTED_RECORD_COUNT:
        failures.append(f"Expected {EXPECTED_RECORD_COUNT} baseline deduplicated records, found {len(baseline)}.")

    screening_ids = set(screening["record_id"].map(clean))
    baseline_ids = set(baseline["record_id"].map(clean))
    missing_ids = sorted(baseline_ids - screening_ids)
    extra_ids = sorted(screening_ids - baseline_ids)
    if missing_ids:
        failures.append(f"{len(missing_ids)} baseline records are missing from screening_decisions.csv.")
    if extra_ids:
        failures.append(f"{len(extra_ids)} extra records appear in screening_decisions.csv.")

    duplicate_ids = screening["record_id"][screening["record_id"].duplicated()].map(clean).tolist()
    if duplicate_ids:
        failures.append(f"{len(duplicate_ids)} duplicate record_id values found in screening_decisions.csv.")

    invalid_decisions = []
    invalid_reasons = []
    excludes_without_reason = []
    non_excludes_with_reason = []
    invalid_narrowed_decisions = []
    invalid_narrowed_reasons = []
    narrowed_excludes_without_reason = []

    for index, row in screening.iterrows():
        row_number = index + 2
        record_id = clean(row["record_id"])
        decision = clean(row["human_title_abstract_decision"])
        reason = clean(row["human_title_abstract_exclusion_reason"])
        label = f"row {row_number} ({record_id})"

        if decision not in VALID_DECISIONS:
            invalid_decisions.append(f"{label}: {decision}")
        if reason not in VALID_EXCLUSION_REASONS:
            invalid_reasons.append(f"{label}: {reason}")
        if decision == "exclude" and not reason:
            excludes_without_reason.append(label)
        if decision in {"include_for_full_text", "maybe"} and reason:
            non_excludes_with_reason.append(label)

        narrowed_decision = clean(row["narrowed_screening_decision"])
        narrowed_reason = clean(row["narrowed_screening_reason"])
        if narrowed_decision not in VALID_NARROWED_DECISIONS:
            invalid_narrowed_decisions.append(f"{label}: {narrowed_decision}")
        if narrowed_reason not in VALID_NARROWED_REASONS:
            invalid_narrowed_reasons.append(f"{label}: {narrowed_reason}")
        if narrowed_decision == "exclude_after_narrowing" and not narrowed_reason:
            narrowed_excludes_without_reason.append(label)

    if invalid_decisions:
        failures.append(f"{len(invalid_decisions)} invalid title/abstract decisions found.")
    if invalid_reasons:
        failures.append(f"{len(invalid_reasons)} invalid exclusion reasons found.")
    if excludes_without_reason:
        failures.append(f"{len(excludes_without_reason)} excluded records are missing exclusion reasons.")
    if non_excludes_with_reason:
        failures.append(f"{len(non_excludes_with_reason)} include/maybe records have exclusion reasons filled in.")
    if invalid_narrowed_decisions:
        failures.append(f"{len(invalid_narrowed_decisions)} invalid narrowed screening decisions found.")
    if invalid_narrowed_reasons:
        failures.append(f"{len(invalid_narrowed_reasons)} invalid narrowed screening reasons found.")
    if narrowed_excludes_without_reason:
        warnings.append(f"{len(narrowed_excludes_without_reason)} narrowed exclusions are missing narrowed reasons.")

    blank_decisions = int((screening["human_title_abstract_decision"].map(clean) == "").sum())
    decision_counts = screening["human_title_abstract_decision"].map(clean).value_counts().to_dict()
    reason_counts = screening["human_title_abstract_exclusion_reason"].map(clean).value_counts().to_dict()
    narrowed_decision_counts = screening["narrowed_screening_decision"].map(clean).value_counts().to_dict()
    narrowed_reason_counts = screening["narrowed_screening_reason"].map(clean).value_counts().to_dict()
    retained = screening[screening["narrowed_screening_decision"].map(clean).eq("retain_for_full_text")]
    retained_role_counts = retained["evidence_role"].map(clean).value_counts().to_dict()
    blank_narrowed = int((screening["narrowed_screening_decision"].map(clean) == "").sum())

    if len(retained) != EXPECTED_NARROWED_RETAINED_COUNT:
        failures.append(f"Expected {EXPECTED_NARROWED_RETAINED_COUNT} narrowed empirical retained records, found {len(retained)}.")
    for role, expected_count in EXPECTED_RETAINED_ROLE_COUNTS.items():
        actual_count = retained_role_counts.get(role, 0)
        if actual_count != expected_count:
            failures.append(f"Expected {expected_count} retained `{role}` records, found {actual_count}.")
    if blank_narrowed:
        failures.append(f"{blank_narrowed} records still have blank narrowed screening decisions after empirical freeze.")

    if blank_decisions:
        warnings.append(f"{blank_decisions} records do not yet have a human title/abstract decision.")

    status = "PASS" if not failures else "FAIL"
    lines = [
        "# Screening Validation Report",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"Status: {status}",
        "",
        "## Record Counts",
        "",
        f"- Expected screening records: {EXPECTED_RECORD_COUNT}",
        f"- Screening records found: {len(screening)}",
        f"- Baseline deduplicated records found: {len(baseline)}",
        f"- Records marked ineligible by automation: 0",
        "",
        "## Decision Counts",
        "",
    ]
    for key in ["", "include_for_full_text", "maybe", "exclude"]:
        label = "(blank)" if key == "" else key
        lines.append(f"- {label}: {decision_counts.get(key, 0)}")

    lines.extend(["", "## Exclusion Reason Counts", ""])
    for key in [""] + sorted(VALID_EXCLUSION_REASONS - {""}):
        label = "(blank)" if key == "" else key
        lines.append(f"- {label}: {reason_counts.get(key, 0)}")

    lines.extend(["", "## Narrowed Empirical Screening Counts", ""])
    for key in ["", "retain_for_full_text", "background_only", "exclude_after_narrowing", "unsure_second_pass"]:
        label = "(blank)" if key == "" else key
        lines.append(f"- {label}: {narrowed_decision_counts.get(key, 0)}")

    lines.extend(["", "## Narrowed Exclusion Reason Counts", ""])
    for key in [""] + sorted(VALID_NARROWED_REASONS - {""}):
        label = "(blank)" if key == "" else key
        lines.append(f"- {label}: {narrowed_reason_counts.get(key, 0)}")

    lines.extend(["", "## Retained Evidence Role Counts", ""])
    for role in [
        "post_2021_policy_implementation_evidence",
        "pre_2021_baseline_problem_evidence",
        "service_specific_medicaid_access_policy",
        "broad_maternal_health_background_only",
        "medicaid_only_payer_or_data_source_exclude",
        "",
    ]:
        label = "(blank)" if role == "" else role
        lines.append(f"- {label}: {retained_role_counts.get(role, 0)}")

    lines.extend(["", "## Checks", ""])
    if failures:
        for failure in failures:
            lines.append(f"- FAIL: {failure}")
    else:
        lines.append("- PASS: Screening record count remains 211.")
        lines.append("- PASS: No records were deleted from the deduplicated baseline.")
        lines.append("- PASS: All completed decisions are valid.")
        lines.append("- PASS: Every excluded record has an exclusion reason.")
        lines.append("- PASS: Include/maybe records do not have exclusion reasons filled in.")
        lines.append("- PASS: Narrowed empirical screening decisions are complete.")
        lines.append("- PASS: Narrowed empirical retained count is 32.")
        lines.append("- PASS: Retained evidence role counts match the frozen empirical evidence map.")

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
