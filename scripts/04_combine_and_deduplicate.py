from __future__ import annotations

import pandas as pd

from common import DATA, ensure_dirs, normalize_doi, normalize_text, read_csv_if_exists, write_csv


CANONICAL_COLUMNS = [
    "record_id",
    "title",
    "abstract",
    "year",
    "journal",
    "doi",
    "pmid",
    "url",
    "authors",
    "source_database",
    "source_databases_found",
    "openalex_id",
    "publication_types",
    "mesh_terms",
    "concepts",
    "type",
]


def load_source(path, source_name: str) -> pd.DataFrame:
    df = read_csv_if_exists(path)
    if df.empty:
        return df
    df["source_database"] = df.get("source_database", source_name)
    for column in CANONICAL_COLUMNS:
        if column not in df.columns and column != "record_id":
            df[column] = ""
    return df


def dedupe_key(row: pd.Series) -> str:
    doi = normalize_doi(row.get("doi", ""))
    pmid = normalize_text(row.get("pmid", ""))
    title = normalize_text(row.get("title", ""))
    if doi:
        return f"doi:{doi}"
    if pmid:
        return f"pmid:{pmid}"
    return f"title:{title}"


def merge_group(group: pd.DataFrame, record_number: int) -> dict:
    merged = {}
    for column in CANONICAL_COLUMNS:
        if column == "record_id":
            merged[column] = f"REC{record_number:05d}"
        elif column == "source_databases_found":
            merged[column] = "; ".join(sorted(set(group["source_database"].astype(str))))
        else:
            values = [str(value).strip() for value in group.get(column, pd.Series(dtype=str)).fillna("") if str(value).strip()]
            merged[column] = values[0] if values else ""
    return merged


def main() -> None:
    ensure_dirs()
    pubmed = load_source(DATA / "raw" / "pubmed_records.csv", "PubMed")
    # PubMed is the only automated academic database source retained for the
    # final main PRISMA workflow. OpenAlex is exploratory only.
    combined = pubmed.copy().fillna("")
    if combined.empty:
        write_csv(pd.DataFrame(columns=CANONICAL_COLUMNS), DATA / "processed" / "all_records_combined.csv")
        write_csv(pd.DataFrame(columns=CANONICAL_COLUMNS), DATA / "processed" / "deduplicated_records.csv")
        write_csv(pd.DataFrame(columns=list(combined.columns) + ["dedupe_key"]), DATA / "processed" / "duplicates_removed.csv")
        return
    combined["dedupe_key"] = combined.apply(dedupe_key, axis=1)
    write_csv(combined, DATA / "processed" / "all_records_combined.csv")
    deduped = []
    duplicates = []
    for number, (_, group) in enumerate(combined.groupby("dedupe_key", sort=False), start=1):
        deduped.append(merge_group(group, number))
        if len(group) > 1:
            duplicates.append(group.assign(duplicate_group=number))
    write_csv(pd.DataFrame(deduped)[CANONICAL_COLUMNS], DATA / "processed" / "deduplicated_records.csv")
    duplicate_df = pd.concat(duplicates, ignore_index=True, sort=False) if duplicates else pd.DataFrame(columns=list(combined.columns) + ["duplicate_group"])
    write_csv(duplicate_df, DATA / "processed" / "duplicates_removed.csv")


if __name__ == "__main__":
    main()
