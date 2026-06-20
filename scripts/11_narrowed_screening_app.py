from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
SCREENING_CSV = ROOT / "data" / "manual" / "screening_decisions.csv"

ELIGIBLE_FIRST_PASS = {"include_for_full_text", "maybe"}
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
    "broad_maternal_health_policy_only",
    "not_12_month_extension",
    "not_post_2021_relevant",
    "not_medicaid_postpartum_policy",
    "background_context_only",
    "other",
]

REQUIRED_COLUMNS = [
    "record_id",
    "title",
    "abstract",
    "year",
    "journal",
    "doi",
    "pmid",
    "url",
    "relevance_score",
    "human_title_abstract_decision",
    "narrowed_screening_decision",
    "narrowed_screening_reason",
    "narrowed_notes",
]


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def read_screening_csv() -> pd.DataFrame:
    if not SCREENING_CSV.exists():
        st.error(f"Screening CSV not found: {SCREENING_CSV}")
        st.stop()
    df = pd.read_csv(SCREENING_CSV, dtype=str).fillna("")
    for column in ["narrowed_screening_decision", "narrowed_screening_reason", "narrowed_notes"]:
        if column not in df.columns:
            df[column] = ""
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        st.error(f"screening_decisions.csv is missing required columns: {', '.join(missing)}")
        st.stop()
    return df


def write_screening_csv(df: pd.DataFrame) -> None:
    temp_path = SCREENING_CSV.with_suffix(".csv.tmp")
    df.to_csv(temp_path, index=False)
    temp_path.replace(SCREENING_CSV)


def second_pass_records(df: pd.DataFrame, blank_only: bool, decision_filter: str) -> pd.DataFrame:
    view = df[df["human_title_abstract_decision"].map(clean).isin(ELIGIBLE_FIRST_PASS)].copy()
    if blank_only:
        view = view[view["narrowed_screening_decision"].map(clean).eq("")]
    if decision_filter != "all":
        view = view[view["narrowed_screening_decision"].map(clean).eq(decision_filter)]
    view["_score"] = pd.to_numeric(view["relevance_score"], errors="coerce").fillna(0)
    return view.sort_values(["_score", "record_id"], ascending=[False, True]).drop(columns=["_score"])


def set_current_record(record_id: str) -> None:
    st.session_state.narrowed_current_record_id = record_id


def current_position(view: pd.DataFrame) -> int:
    record_ids = view["record_id"].astype(str).tolist()
    current = st.session_state.get("narrowed_current_record_id", "")
    if current in record_ids:
        return record_ids.index(current)
    if record_ids:
        set_current_record(record_ids[0])
        return 0
    return -1


def move_by(delta: int, view: pd.DataFrame) -> None:
    if view.empty:
        return
    position = current_position(view)
    next_position = min(max(position + delta, 0), len(view) - 1)
    set_current_record(str(view.iloc[next_position]["record_id"]))


def next_unscreened(df: pd.DataFrame) -> None:
    view = second_pass_records(df, blank_only=False, decision_filter="all")
    if view.empty:
        return
    record_ids = view["record_id"].astype(str).tolist()
    current = st.session_state.get("narrowed_current_record_id", "")
    start = record_ids.index(current) + 1 if current in record_ids else 0
    for offset in range(len(record_ids)):
        candidate = record_ids[(start + offset) % len(record_ids)]
        row = df[df["record_id"].astype(str).eq(candidate)].iloc[0]
        if clean(row["narrowed_screening_decision"]) == "":
            set_current_record(candidate)
            return


def rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def save_current_record(df: pd.DataFrame, record_id: str, decision: str, reason: str, notes: str) -> bool:
    decision = clean(decision)
    reason = clean(reason)
    notes = "" if notes is None else str(notes)
    if decision not in NARROWED_DECISION_OPTIONS:
        st.error("Choose a valid narrowed screening decision.")
        return False
    if decision and reason not in NARROWED_REASON_OPTIONS:
        st.error("Choose a valid narrowed screening reason.")
        return False
    if decision and not reason:
        st.error("Choose a narrowed screening reason before saving.")
        return False

    mask = df["record_id"].astype(str).eq(str(record_id))
    if not mask.any():
        st.error(f"Could not find record_id {record_id}.")
        return False

    df.loc[mask, "narrowed_screening_decision"] = decision
    df.loc[mask, "narrowed_screening_reason"] = reason
    df.loc[mask, "narrowed_notes"] = notes
    write_screening_csv(df)
    return True


def main() -> None:
    st.set_page_config(page_title="Narrowed Second-Pass Screening", layout="wide")
    st.title("State Adoption and Implementation of Twelve-Month Postpartum Medicaid Coverage Extensions")
    st.subheader("Second-Pass Narrowed Screening")

    st.markdown(
        "Screen only the 166 first-pass `include_for_full_text` or `maybe` records for direct relevance "
        "to post-2021 state adoption and implementation of 12-month postpartum Medicaid coverage extensions."
    )

    df = read_screening_csv()
    eligible = df[df["human_title_abstract_decision"].map(clean).isin(ELIGIBLE_FIRST_PASS)]
    total = len(eligible)
    completed = int(eligible["narrowed_screening_decision"].map(clean).ne("").sum())
    st.progress(completed / total if total else 0, text=f"{completed} / {total} second-pass records completed")

    with st.sidebar:
        st.header("Navigation")
        blank_only = st.checkbox("Show only blank narrowed decisions", value=False)
        decision_filter = st.selectbox(
            "Filter by narrowed decision",
            ["all", "retain_for_full_text", "background_only", "exclude_after_narrowing", "unsure_second_pass", ""],
            format_func=lambda value: "(blank)" if value == "" else value,
        )
        view = second_pass_records(df, blank_only=blank_only, decision_filter=decision_filter)

        jump_record_id = st.text_input("Jump to record_id")
        if st.button("Jump") and jump_record_id:
            if jump_record_id in eligible["record_id"].astype(str).tolist():
                set_current_record(jump_record_id)
                rerun()
            else:
                st.error(f"No second-pass record found for {jump_record_id}.")

        previous_col, next_col = st.columns(2)
        with previous_col:
            if st.button("Previous", use_container_width=True):
                move_by(-1, view)
                rerun()
        with next_col:
            if st.button("Next", use_container_width=True):
                move_by(1, view)
                rerun()
        if st.button("Next unscreened", use_container_width=True):
            next_unscreened(df)
            rerun()

    if view.empty:
        st.success("No records match the current narrowed-screening filter.")
        return

    position = current_position(view)
    row = view.iloc[position]
    record_id = str(row["record_id"])
    source_row = df[df["record_id"].astype(str).eq(record_id)].iloc[0]

    st.caption(f"Record {position + 1} of {len(view)} in current view")
    top_cols = st.columns([2, 1, 1, 1])
    top_cols[0].metric("record_id", record_id)
    top_cols[1].metric("first-pass decision", clean(source_row["human_title_abstract_decision"]))
    top_cols[2].metric("relevance_score", clean(source_row["relevance_score"]) or "0")
    top_cols[3].metric("year", clean(source_row["year"]) or "NA")

    st.markdown("### Title")
    st.write(clean(source_row["title"]) or "_No title available._")
    st.markdown("### Abstract")
    st.write(clean(source_row["abstract"]) or "_No abstract available._")

    metadata_cols = st.columns(4)
    metadata_cols[0].markdown(f"**Journal**  \n{clean(source_row['journal']) or 'NA'}")
    metadata_cols[1].markdown(f"**DOI**  \n{clean(source_row['doi']) or 'NA'}")
    metadata_cols[2].markdown(f"**PMID**  \n{clean(source_row['pmid']) or 'NA'}")
    url = clean(source_row["url"])
    metadata_cols[3].markdown(f"**URL**  \n[{url}]({url})" if url else "**URL**  \nNA")

    st.divider()
    st.markdown("### Narrowed Screening Decision")
    current_decision = clean(source_row["narrowed_screening_decision"])
    current_reason = clean(source_row["narrowed_screening_reason"])
    current_notes = "" if pd.isna(source_row["narrowed_notes"]) else str(source_row["narrowed_notes"])

    decision = st.radio(
        "narrowed_screening_decision",
        NARROWED_DECISION_OPTIONS,
        index=NARROWED_DECISION_OPTIONS.index(current_decision) if current_decision in NARROWED_DECISION_OPTIONS else 0,
        horizontal=True,
    )
    reason = st.selectbox(
        "narrowed_screening_reason",
        NARROWED_REASON_OPTIONS,
        index=NARROWED_REASON_OPTIONS.index(current_reason) if current_reason in NARROWED_REASON_OPTIONS else 0,
    )
    notes = st.text_area("narrowed_notes", value=current_notes, height=120)

    save_col, save_next_col = st.columns([1, 1])
    with save_col:
        if st.button("Save narrowed decision", type="primary", use_container_width=True):
            if save_current_record(df, record_id, decision, reason, notes):
                st.success("Saved to data/manual/screening_decisions.csv.")
                rerun()
    with save_next_col:
        if st.button("Save and go to next unscreened", use_container_width=True):
            if save_current_record(df, record_id, decision, reason, notes):
                df = read_screening_csv()
                next_unscreened(df)
                rerun()


if __name__ == "__main__":
    main()
