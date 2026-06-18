from __future__ import annotations

import pandas as pd
import requests

from common import CONFIG, DATA, append_search_log, ensure_dirs, join_values, read_yaml, today_iso, write_csv


def inverted_index_to_text(index: dict | None) -> str:
    if not index:
        return ""
    words = sorted(((position, word) for word, positions in index.items() for position in positions), key=lambda x: x[0])
    return " ".join(word for _, word in words)


def search_openalex(query: str, start_year: int, end_year: int) -> tuple[list[dict], int]:
    params = {
        "search": query,
        "filter": f"from_publication_date:{start_year}-01-01,to_publication_date:{end_year}-12-31",
        "per-page": 200,
        "page": 1,
    }
    response = requests.get("https://api.openalex.org/works", params=params, timeout=60)
    response.raise_for_status()
    payload = response.json()
    records = []
    for work in payload.get("results", []):
        source = (work.get("primary_location") or {}).get("source") or {}
        authors = [
            (authorship.get("author") or {}).get("display_name", "")
            for authorship in work.get("authorships", [])
        ]
        concepts = [concept.get("display_name", "") for concept in work.get("concepts", [])]
        records.append(
            {
                "source_database": "OpenAlex",
                "openalex_id": work.get("id", ""),
                "title": work.get("display_name", ""),
                "abstract": inverted_index_to_text(work.get("abstract_inverted_index")),
                "doi": work.get("doi", ""),
                "year": work.get("publication_year", ""),
                "journal": source.get("display_name", ""),
                "authors": join_values(authors),
                "url": work.get("landing_page_url") or work.get("id", ""),
                "cited_by_count": work.get("cited_by_count", ""),
                "concepts": join_values(concepts),
                "type": work.get("type", ""),
            }
        )
    return records, int((payload.get("meta") or {}).get("count", len(records)))


def main() -> None:
    ensure_dirs()
    config = read_yaml(CONFIG / "search_terms.yaml")
    query = config["academic_search_string"]
    start_year = config["date_range"]["start_year"]
    end_year = config["date_range"]["end_year"]
    records, result_count = search_openalex(query, start_year, end_year)
    write_csv(pd.DataFrame(records), DATA / "raw" / "openalex_records.csv")
    print(
        "OpenAlex exploratory search complete. "
        f"Reported matches: {result_count}; downloaded: {len(records)}. "
        "Results were saved to data/raw/openalex_records.csv but were not appended "
        "to the main PRISMA search log."
    )


if __name__ == "__main__":
    main()
