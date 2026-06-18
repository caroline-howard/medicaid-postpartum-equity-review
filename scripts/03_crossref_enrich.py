from __future__ import annotations

import time

import pandas as pd
import requests

from common import DATA, ensure_dirs, read_csv_if_exists, require_columns, write_csv


def query_crossref_by_doi(doi: str) -> dict:
    if not doi:
        return {}
    response = requests.get(f"https://api.crossref.org/works/{doi}", timeout=20)
    if response.status_code == 404:
        return {}
    response.raise_for_status()
    return response.json().get("message", {})


def query_crossref_by_title(title: str) -> dict:
    if not title:
        return {}
    response = requests.get("https://api.crossref.org/works", params={"query.title": title, "rows": 1}, timeout=20)
    response.raise_for_status()
    items = response.json().get("message", {}).get("items", [])
    return items[0] if items else {}


def publication_date(message: dict) -> str:
    parts = (message.get("published-print") or message.get("published-online") or message.get("created") or {}).get("date-parts", [[]])[0]
    return "-".join(str(part) for part in parts)


def main() -> None:
    ensure_dirs()
    input_path = DATA / "processed" / "deduplicated_records.csv"
    if not input_path.exists():
        input_path = DATA / "processed" / "all_records_combined.csv"
    if not input_path.exists():
        pubmed = read_csv_if_exists(DATA / "raw" / "pubmed_records.csv")
        openalex = read_csv_if_exists(DATA / "raw" / "openalex_records.csv")
        records = pd.concat([pubmed, openalex], ignore_index=True, sort=False).fillna("")
    else:
        records = read_csv_if_exists(input_path)
    require_columns(records, ["title", "doi"], str(input_path))
    enriched_rows = []
    for _, row in records.iterrows():
        message = {}
        try:
            message = query_crossref_by_doi(str(row.get("doi", "")).replace("https://doi.org/", ""))
            if not message:
                message = query_crossref_by_title(row.get("title", ""))
            time.sleep(0.1)
        except requests.RequestException as exc:
            message = {"crossref_error": str(exc)}
        updated = row.to_dict()
        updated.update(
            {
                "crossref_doi": message.get("DOI", ""),
                "crossref_publisher": message.get("publisher", ""),
                "crossref_journal": "; ".join(message.get("container-title", [])),
                "crossref_publication_date": publication_date(message),
                "crossref_url": message.get("URL", ""),
                "crossref_reference_count": message.get("reference-count", ""),
            }
        )
        enriched_rows.append(updated)
    write_csv(pd.DataFrame(enriched_rows), DATA / "processed" / "crossref_enriched_records.csv")


if __name__ == "__main__":
    main()
