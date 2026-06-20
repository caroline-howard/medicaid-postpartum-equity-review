from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
SCREENING_CSV = ROOT / "data" / "manual" / "screening_decisions.csv"

DECISION_OPTIONS = ["", "include_for_full_text", "maybe", "exclude"]
EXCLUSION_REASON_OPTIONS = [
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
]

DISPLAY_COLUMNS = [
    "record_id",
    "title",
    "abstract",
    "year",
    "journal",
    "doi",
    "pmid",
    "url",
    "relevance_score",
]

REQUIRED_COLUMNS = [
    *DISPLAY_COLUMNS,
    "human_title_abstract_decision",
    "human_title_abstract_exclusion_reason",
    "notes",
]


def read_screening_csv() -> pd.DataFrame:
    if not SCREENING_CSV.exists():
        st.error(f"Screening CSV not found: {SCREENING_CSV}")
        st.stop()
    df = pd.read_csv(SCREENING_CSV, dtype=str).fillna("")
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        st.error(f"screening_decisions.csv is missing required columns: {', '.join(missing)}")
        st.stop()
    return df


def write_screening_csv(df: pd.DataFrame) -> None:
    temp_path = SCREENING_CSV.with_suffix(".csv.tmp")
    df.to_csv(temp_path, index=False)
    temp_path.replace(SCREENING_CSV)


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def sorted_view(df: pd.DataFrame, blank_only: bool) -> pd.DataFrame:
    view = df.copy()
    if blank_only:
        view = view[view["human_title_abstract_decision"].map(clean).eq("")]
    view["_score"] = pd.to_numeric(view["relevance_score"], errors="coerce").fillna(0)
    return view.sort_values(["_score", "record_id"], ascending=[False, True]).drop(columns=["_score"])


def set_current_record(record_id: str) -> None:
    st.session_state.current_record_id = record_id


def current_position(view: pd.DataFrame) -> int:
    record_ids = view["record_id"].astype(str).tolist()
    current = st.session_state.get("current_record_id", "")
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


def next_unscreened(df: pd.DataFrame, view: pd.DataFrame) -> None:
    if df.empty:
        return
    ordered = sorted_view(df, blank_only=False)
    current = st.session_state.get("current_record_id", "")
    record_ids = ordered["record_id"].astype(str).tolist()
    start = record_ids.index(current) + 1 if current in record_ids else 0
    for offset in range(len(record_ids)):
        candidate = record_ids[(start + offset) % len(record_ids)]
        row = df[df["record_id"].astype(str).eq(candidate)].iloc[0]
        if clean(row["human_title_abstract_decision"]) == "":
            if view.empty or candidate in view["record_id"].astype(str).tolist():
                set_current_record(candidate)
            else:
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

    if decision not in DECISION_OPTIONS:
        st.error("Choose a valid title/abstract decision.")
        return False
    if decision == "exclude" and not reason:
        st.error("Excluded records require an exclusion reason.")
        return False
    if decision != "exclude":
        reason = ""
    if reason not in EXCLUSION_REASON_OPTIONS:
        st.error("Choose a valid exclusion reason.")
        return False

    mask = df["record_id"].astype(str).eq(str(record_id))
    if not mask.any():
        st.error(f"Could not find record_id {record_id}.")
        return False

    df.loc[mask, "human_title_abstract_decision"] = decision
    df.loc[mask, "human_title_abstract_exclusion_reason"] = reason
    df.loc[mask, "notes"] = notes
    write_screening_csv(df)
    return True


def main() -> None:
    st.set_page_config(page_title="Title/Abstract Screening", layout="wide")
    st.title("Medicaid Postpartum Coverage & Maternal Health Equity")
    st.subheader("Title/Abstract Screening")

    df = read_screening_csv()
    total = len(df)
    completed = int(df["human_title_abstract_decision"].map(clean).ne("").sum())
    st.progress(completed / total if total else 0, text=f"{completed} / {total} records completed")

    with st.sidebar:
        st.header("Navigation")
        blank_only = st.checkbox("Show only blank decisions", value=False)
        view = sorted_view(df, blank_only=blank_only)

        jump_record_id = st.text_input("Jump to record_id")
        if st.button("Jump") and jump_record_id:
            if jump_record_id in df["record_id"].astype(str).tolist():
                set_current_record(jump_record_id)
                rerun()
            else:
                st.error(f"No record found for {jump_record_id}.")

        previous_col, next_col = st.columns(2)
        with previous_col:
            if st.button("Previous record", use_container_width=True):
                move_by(-1, view)
                rerun()
        with next_col:
            if st.button("Next record", use_container_width=True):
                move_by(1, view)
                rerun()
        if st.button("Next unscreened record", use_container_width=True):
            next_unscreened(df, view)
            rerun()

    if view.empty:
        st.success("No records match the current filter.")
        return

    position = current_position(view)
    row = view.iloc[position]
    record_id = str(row["record_id"])
    source_row = df[df["record_id"].astype(str).eq(record_id)].iloc[0]

    st.caption(f"Record {position + 1} of {len(view)} in current view")
    top_cols = st.columns([2, 1, 1, 1])
    top_cols[0].metric("record_id", record_id)
    top_cols[1].metric("relevance_score", clean(source_row["relevance_score"]) or "0")
    top_cols[2].metric("year", clean(source_row["year"]) or "NA")
    top_cols[3].metric("source", clean(source_row.get("source_database", "")) or "NA")

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
    st.markdown("### Screening Decision")
    current_decision = clean(source_row["human_title_abstract_decision"])
    current_reason = clean(source_row["human_title_abstract_exclusion_reason"])
    current_notes = "" if pd.isna(source_row["notes"]) else str(source_row["notes"])

    decision = st.radio(
        "human_title_abstract_decision",
        DECISION_OPTIONS,
        index=DECISION_OPTIONS.index(current_decision) if current_decision in DECISION_OPTIONS else 0,
        horizontal=True,
    )
    reason = ""
    if decision == "exclude":
        reason = st.selectbox(
            "human_title_abstract_exclusion_reason",
            EXCLUSION_REASON_OPTIONS,
            index=EXCLUSION_REASON_OPTIONS.index(current_reason) if current_reason in EXCLUSION_REASON_OPTIONS else 0,
        )
    elif current_reason:
        st.info("Changing this record away from exclude will clear the exclusion reason on save.")

    notes = st.text_area("notes", value=current_notes, height=120)

    save_col, save_next_col = st.columns([1, 1])
    with save_col:
        if st.button("Save decision", type="primary", use_container_width=True):
            if save_current_record(df, record_id, decision, reason, notes):
                st.success("Saved to data/manual/screening_decisions.csv.")
                rerun()
    with save_next_col:
        if st.button("Save and go to next unscreened", use_container_width=True):
            if save_current_record(df, record_id, decision, reason, notes):
                df = read_screening_csv()
                next_unscreened(df, sorted_view(df, blank_only=blank_only))
                rerun()


if __name__ == "__main__":
    main()
