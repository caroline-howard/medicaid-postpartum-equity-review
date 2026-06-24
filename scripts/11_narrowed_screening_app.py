from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
SCREENING_CSV = ROOT / "data" / "manual" / "screening_decisions.csv"

ELIGIBLE_FIRST_PASS = {"include_for_full_text", "maybe"}
EMPIRICAL_EVIDENCE_ROLES = {
    "service_specific_medicaid_access_policy",
    "post_2021_policy_implementation_evidence",
    "pre_2021_baseline_problem_evidence",
}

NARROWED_DECISION_OPTIONS = [
    "",
    "retain_for_full_text",
    "background_only",
    "exclude_after_narrowing",
    "unsure_second_pass",
]

NARROWED_REASON_OPTIONS = [
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
]

EVIDENCE_ROLE_OPTIONS = [
    "",
    "pre_2021_baseline_problem_evidence",
    "post_2021_policy_implementation_evidence",
    "service_specific_medicaid_access_policy",
    "broad_maternal_health_background_only",
    "medicaid_only_payer_or_data_source_exclude",
]

PRE_2015_COHORT_NOTE = "Excluded after narrowing because the study data/cohort are entirely pre-2015."

REVIEW_QUEUE_OPTIONS = [
    "Remaining empirical review pool",
    "Suggested post-2021 policy/implementation evidence",
    "Suggested pre-2021 baseline problem evidence",
    "Suggested service-specific Medicaid access policy",
    "Audit: all pre-2021 suggested records",
    "Audit: all records",
]

REQUIRED_BASE_COLUMNS = [
    "record_id",
    "title",
    "abstract",
    "human_title_abstract_decision",
]

ENSURED_COLUMNS = [
    "publication_year",
    "year",
    "journal",
    "doi",
    "pmid",
    "url",
    "relevance_score",
    "timeline_scope_tier",
    "automation_suggestion",
    "narrowed_screening_decision_suggested",
    "narrowed_screening_reason_suggested",
    "evidence_role_suggested",
    "evidence_role_suggestion_confidence",
    "evidence_role_suggestion_reason",
    "narrowed_screening_decision",
    "narrowed_screening_reason",
    "narrowed_notes",
    "evidence_role",
]

ROLE_HELP = {
    "pre_2021_baseline_problem_evidence": "Pre-2021 data showing the baseline problem, such as Medicaid loss after 60 days, insurance churn, uninsurance, readmission while uninsured, or postpartum access gaps.",
    "post_2021_policy_implementation_evidence": "ARPA 12-month extension, FFCRA continuous coverage, unwinding, state adoption, or implementation of extended postpartum coverage.",
    "service_specific_medicaid_access_policy": "Medicaid postpartum service coverage or reimbursement, such as LARC, oral health, lactation, contraception, behavioral health, OUD care, or billing/implementation issues.",
    "broad_maternal_health_background_only": "Broad maternal health article with only a brief Medicaid/postpartum coverage connection.",
    "medicaid_only_payer_or_data_source_exclude": "Medicaid is only a payer, claims source, covariate, subgroup, or sample descriptor.",
}


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def write_screening_csv(df: pd.DataFrame, path: Path = SCREENING_CSV) -> None:
    temp_path = path.with_suffix(".csv.tmp")
    df.to_csv(temp_path, index=False)
    temp_path.replace(path)


def ensure_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    updated = df.copy()
    changed = False
    for column in ENSURED_COLUMNS:
        if column not in updated.columns:
            updated[column] = ""
            changed = True
    return updated.fillna(""), changed


def read_screening_csv(path: Path = SCREENING_CSV, persist_missing_columns: bool = True) -> pd.DataFrame:
    if not path.exists():
        st.error(f"Screening CSV not found: {path}")
        st.stop()
    df = pd.read_csv(path, dtype=str).fillna("")
    missing = [column for column in REQUIRED_BASE_COLUMNS if column not in df.columns]
    if missing:
        st.error(f"screening_decisions.csv is missing required columns: {', '.join(missing)}")
        st.stop()
    df, changed = ensure_columns(df)
    if changed and persist_missing_columns:
        write_screening_csv(df, path)
    return df


def app_records(df: pd.DataFrame) -> pd.DataFrame:
    view = df.copy()
    view["_strong_order"] = view["timeline_scope_tier"].map(clean).ne("tier_1_strong_match").astype(int)
    view["_score"] = pd.to_numeric(view["relevance_score"], errors="coerce").fillna(0)
    return view.sort_values(["_strong_order", "_score", "record_id"], ascending=[True, False, True]).drop(
        columns=["_strong_order", "_score"]
    )


def queue_records(records: pd.DataFrame, queue: str) -> pd.DataFrame:
    blank_decision = records["narrowed_screening_decision"].map(clean).eq("")
    suggested_role = records["evidence_role_suggested"].map(clean)
    if queue == "Remaining empirical review pool":
        return records[blank_decision & suggested_role.isin(EMPIRICAL_EVIDENCE_ROLES)]
    role_filters = {
        "Suggested post-2021 policy/implementation evidence": "post_2021_policy_implementation_evidence",
        "Suggested pre-2021 baseline problem evidence": "pre_2021_baseline_problem_evidence",
        "Suggested service-specific Medicaid access policy": "service_specific_medicaid_access_policy",
    }
    if queue in role_filters:
        return records[blank_decision & suggested_role.eq(role_filters[queue])]
    if queue == "Audit: all pre-2021 suggested records":
        return records[suggested_role.eq("pre_2021_baseline_problem_evidence")]
    return records


def dashboard_counts(records: pd.DataFrame) -> dict[str, int]:
    retained = records["narrowed_screening_decision"].map(clean).eq("retain_for_full_text")
    return {
        "total": len(records),
        "retained": int(retained.sum()),
        "background": int(records["narrowed_screening_decision"].map(clean).eq("background_only").sum()),
        "excluded": int(records["narrowed_screening_decision"].map(clean).eq("exclude_after_narrowing").sum()),
        "blank": int(records["narrowed_screening_decision"].map(clean).eq("").sum()),
        "retained_missing_role": int((retained & records["evidence_role"].map(clean).eq("")).sum()),
    }


def set_current_record(record_id: str) -> None:
    st.session_state.narrowed_current_record_id = record_id


def current_position(records: pd.DataFrame) -> int:
    record_ids = records["record_id"].astype(str).tolist()
    current = st.session_state.get("narrowed_current_record_id", "")
    if current in record_ids:
        return record_ids.index(current)
    if record_ids:
        set_current_record(record_ids[0])
        return 0
    return -1


def move_by(delta: int, records: pd.DataFrame) -> None:
    if records.empty:
        return
    position = current_position(records)
    next_position = min(max(position + delta, 0), len(records) - 1)
    set_current_record(str(records.iloc[next_position]["record_id"]))


def next_unscreened(records: pd.DataFrame) -> None:
    if records.empty:
        return
    record_ids = records["record_id"].astype(str).tolist()
    current = st.session_state.get("narrowed_current_record_id", "")
    start = record_ids.index(current) + 1 if current in record_ids else 0
    for offset in range(len(records)):
        candidate = record_ids[(start + offset) % len(records)]
        row = records[records["record_id"].astype(str).eq(candidate)].iloc[0]
        if clean(row["narrowed_screening_decision"]) == "":
            set_current_record(candidate)
            return


def save_current_record(
    df: pd.DataFrame,
    record_id: str,
    narrowed_decision: str,
    narrowed_reason: str,
    narrowed_notes: str,
    evidence_role: str,
    path: Path = SCREENING_CSV,
) -> None:
    if narrowed_decision not in NARROWED_DECISION_OPTIONS:
        raise ValueError("Invalid narrowed screening decision.")
    if narrowed_reason not in NARROWED_REASON_OPTIONS:
        raise ValueError("Invalid narrowed screening reason.")
    if evidence_role not in EVIDENCE_ROLE_OPTIONS:
        raise ValueError("Invalid evidence role.")

    updated, _ = ensure_columns(df)
    mask = updated["record_id"].astype(str).eq(str(record_id))
    if not mask.any():
        raise ValueError(f"Could not find record_id {record_id}.")

    updated.loc[mask, "narrowed_screening_decision"] = clean(narrowed_decision)
    updated.loc[mask, "narrowed_screening_reason"] = clean(narrowed_reason)
    updated.loc[mask, "narrowed_notes"] = "" if narrowed_notes is None else str(narrowed_notes)
    updated.loc[mask, "evidence_role"] = clean(evidence_role)
    write_screening_csv(updated, path)


def copy_suggested_role_for_record(df: pd.DataFrame, record_id: str, path: Path = SCREENING_CSV) -> str:
    updated, _ = ensure_columns(df)
    mask = updated["record_id"].astype(str).eq(str(record_id))
    if not mask.any():
        raise ValueError(f"Could not find record_id {record_id}.")
    suggestion = clean(updated.loc[mask, "evidence_role_suggested"].iloc[0])
    if not suggestion:
        raise ValueError("No suggested evidence role is available for this record.")
    updated.loc[mask, "evidence_role"] = suggestion
    write_screening_csv(updated, path)
    return suggestion


def mark_pre_2015_cohort_for_record(df: pd.DataFrame, record_id: str, path: Path = SCREENING_CSV) -> None:
    updated, _ = ensure_columns(df)
    mask = updated["record_id"].astype(str).eq(str(record_id))
    if not mask.any():
        raise ValueError(f"Could not find record_id {record_id}.")

    updated.loc[mask, "narrowed_screening_decision"] = "exclude_after_narrowing"
    updated.loc[mask, "narrowed_screening_reason"] = "pre_2015_cohort"
    updated.loc[mask, "narrowed_notes"] = PRE_2015_COHORT_NOTE
    write_screening_csv(updated, path)


def rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def display_dashboard(records: pd.DataFrame) -> None:
    counts = dashboard_counts(records)
    cols = st.columns(6)
    cols[0].metric("total records", counts["total"])
    cols[1].metric("retained for full text", counts["retained"])
    cols[2].metric("background only", counts["background"])
    cols[3].metric("excluded after narrowing", counts["excluded"])
    cols[4].metric("blank narrowed decisions", counts["blank"])
    cols[5].metric("retained missing evidence role", counts["retained_missing_role"])

    role_counts = records["evidence_role"].map(clean).replace("", "(blank)").value_counts().to_dict()
    st.caption(
        "Evidence role counts: "
        + "; ".join(f"{role}: {count}" for role, count in sorted(role_counts.items()))
    )


def display_help() -> None:
    with st.expander("Evidence role help"):
        st.markdown(
            "**Retain only peer-reviewed empirical studies.** Policy reviews, commentaries, issue briefs, "
            "professional statements, and evidence syntheses should be excluded from the retained empirical evidence map."
        )
        for role, description in ROLE_HELP.items():
            st.markdown(f"**{role}**: {description}")


def main() -> None:
    st.set_page_config(page_title="Narrowed Screening", layout="wide")
    st.title("Narrowed Screening Review")
    st.caption("Manual narrowed decisions and evidence roles are saved one record at a time.")

    df = read_screening_csv()
    records = app_records(df)
    display_dashboard(records)
    display_help()

    with st.sidebar:
        st.header("Review Queue")
        queue = st.selectbox("Queue", REVIEW_QUEUE_OPTIONS)
        queue_view = queue_records(records, queue)
        queue_blank = int(queue_view["narrowed_screening_decision"].map(clean).eq("").sum())
        st.caption(f"{len(queue_view)} records in queue; {queue_blank} blank narrowed decisions.")

        jump_record_id = st.text_input("Jump to record_id")
        if st.button("Jump") and jump_record_id:
            if jump_record_id in queue_view["record_id"].astype(str).tolist():
                set_current_record(jump_record_id)
                rerun()
            else:
                st.error(f"No record found for {jump_record_id} in the selected queue.")

        previous_col, next_col = st.columns(2)
        with previous_col:
            if st.button("Previous", use_container_width=True):
                move_by(-1, queue_view)
                rerun()
        with next_col:
            if st.button("Next", use_container_width=True):
                move_by(1, queue_view)
                rerun()
        if st.button("Next blank decision", use_container_width=True):
            next_unscreened(queue_view)
            rerun()

    if queue_view.empty:
        st.success("No records match this review queue.")
        return

    position = current_position(queue_view)
    source_row = queue_view.iloc[position]
    record_id = str(source_row["record_id"])

    st.divider()
    st.caption(f"Record {position + 1} of {len(queue_view)} in selected queue")
    year = clean(source_row.get("publication_year", "")) or clean(source_row.get("year", ""))
    strong_label = (
        "Strong match: Yes — in the 59"
        if clean(source_row["timeline_scope_tier"]) == "tier_1_strong_match"
        else "Strong match: No"
    )

    meta_cols = st.columns([1, 1, 1, 1])
    meta_cols[0].metric("record_id", record_id)
    meta_cols[1].metric("year", year or "NA")
    meta_cols[2].metric("timeline tier", clean(source_row["timeline_scope_tier"]) or "NA")
    meta_cols[3].metric("first-pass", clean(source_row["human_title_abstract_decision"]) or "NA")

    st.markdown(f"**{strong_label}**")
    st.markdown("### Title")
    st.write(clean(source_row["title"]) or "_No title available._")
    st.markdown("### Abstract")
    st.write(clean(source_row["abstract"]) or "_No abstract available._")

    info_cols = st.columns(4)
    info_cols[0].markdown(f"**Journal**  \n{clean(source_row['journal']) or 'NA'}")
    info_cols[1].markdown(f"**DOI**  \n{clean(source_row['doi']) or 'NA'}")
    info_cols[2].markdown(f"**PMID**  \n{clean(source_row['pmid']) or 'NA'}")
    url = clean(source_row["url"])
    info_cols[3].markdown(f"**URL**  \n[{url}]({url})" if url else "**URL**  \nNA")

    st.markdown("### Automation Suggestions")
    suggestion_cols = st.columns([1, 1, 2])
    suggestion_cols[0].markdown(f"**suggested evidence role**  \n{clean(source_row['evidence_role_suggested']) or 'Not run'}")
    suggestion_cols[1].markdown(f"**confidence**  \n{clean(source_row['evidence_role_suggestion_confidence']) or 'Not run'}")
    suggestion_cols[2].markdown(f"**automation_suggestion**  \n{clean(source_row['automation_suggestion']) or 'NA'}")
    narrowed_suggestion = clean(source_row["narrowed_screening_decision_suggested"])
    narrowed_reason_suggestion = clean(source_row["narrowed_screening_reason_suggested"])
    if narrowed_suggestion or narrowed_reason_suggestion:
        st.markdown(
            f"**suggested narrowed action**  \n"
            f"{narrowed_suggestion or 'NA'}"
            f"{' — ' + narrowed_reason_suggestion if narrowed_reason_suggestion else ''}"
        )
    suggestion_reason = clean(source_row["evidence_role_suggestion_reason"])
    if suggestion_reason:
        st.caption(suggestion_reason)

    st.markdown("### Manual Review Fields")
    current_decision = clean(source_row["narrowed_screening_decision"])
    current_reason = clean(source_row["narrowed_screening_reason"])
    current_notes = "" if pd.isna(source_row["narrowed_notes"]) else str(source_row["narrowed_notes"])
    current_role = clean(source_row["evidence_role"])

    narrowed_decision = st.selectbox(
        "narrowed_screening_decision",
        NARROWED_DECISION_OPTIONS,
        index=NARROWED_DECISION_OPTIONS.index(current_decision) if current_decision in NARROWED_DECISION_OPTIONS else 0,
    )
    narrowed_reason = st.selectbox(
        "narrowed_screening_reason (optional)",
        NARROWED_REASON_OPTIONS,
        index=NARROWED_REASON_OPTIONS.index(current_reason) if current_reason in NARROWED_REASON_OPTIONS else 0,
    )
    evidence_role = st.selectbox(
        "evidence_role (manual, optional)",
        EVIDENCE_ROLE_OPTIONS,
        index=EVIDENCE_ROLE_OPTIONS.index(current_role) if current_role in EVIDENCE_ROLE_OPTIONS else 0,
    )
    narrowed_notes = st.text_area("narrowed_notes (optional)", value=current_notes, height=120)

    action_cols = st.columns([1, 1, 1])
    with action_cols[0]:
        if st.button("Save current record", type="primary", use_container_width=True):
            try:
                save_current_record(df, record_id, narrowed_decision, narrowed_reason, narrowed_notes, evidence_role)
                st.success("Saved current record to data/manual/screening_decisions.csv.")
                rerun()
            except ValueError as exc:
                st.error(str(exc))
    with action_cols[1]:
        if st.button("Copy suggested role to manual evidence_role", use_container_width=True):
            try:
                copied_role = copy_suggested_role_for_record(df, record_id)
                st.success(f"Copied suggested role for this record: {copied_role}")
                rerun()
            except ValueError as exc:
                st.error(str(exc))
    with action_cols[2]:
        if st.button("Mark as pre-2015 cohort and exclude", use_container_width=True):
            try:
                mark_pre_2015_cohort_for_record(df, record_id)
                st.success("Marked current record as excluded for pre-2015 cohort.")
                rerun()
            except ValueError as exc:
                st.error(str(exc))


if __name__ == "__main__":
    main()
