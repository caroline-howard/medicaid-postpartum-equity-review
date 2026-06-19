from __future__ import annotations

import time
import xml.etree.ElementTree as ET

import pandas as pd
import requests

from common import CONFIG, DATA, ensure_dirs, read_yaml, today_iso, write_csv


EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def text_at(node: ET.Element | None, path: str) -> str:
    found = node.find(path) if node is not None else None
    return "".join(found.itertext()).strip() if found is not None else ""


def list_text(node: ET.Element | None, path: str) -> str:
    if node is None:
        return ""
    return "; ".join("".join(item.itertext()).strip() for item in node.findall(path) if "".join(item.itertext()).strip())


def search_pubmed(query: str, start_year: int, end_year: int, retmax: int = 500) -> tuple[list[str], int]:
    params = {
        "db": "pubmed",
        "term": f"({query}) AND ({start_year}:{end_year}[dp])",
        "retmode": "json",
        "retmax": retmax,
        "sort": "relevance",
    }
    response = requests.get(f"{EUTILS}/esearch.fcgi", params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()["esearchresult"]
    return payload.get("idlist", []), int(payload.get("count", 0))


def fetch_pubmed(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    response = requests.post(
        f"{EUTILS}/efetch.fcgi",
        data={"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"},
        timeout=60,
    )
    response.raise_for_status()
    root = ET.fromstring(response.text)
    records = []
    for article in root.findall(".//PubmedArticle"):
        medline = article.find("MedlineCitation")
        pubmed_data = article.find("PubmedData")
        pmid = text_at(medline, "PMID")
        article_node = medline.find("Article") if medline is not None else None
        journal = text_at(article_node, "Journal/Title")
        year = text_at(article_node, "Journal/JournalIssue/PubDate/Year")
        title = text_at(article_node, "ArticleTitle")
        abstract = list_text(article_node, "Abstract/AbstractText")
        pub_types = list_text(article_node, "PublicationTypeList/PublicationType")
        mesh_terms = list_text(medline, "MeshHeadingList/MeshHeading/DescriptorName")
        authors = []
        for author in article.findall(".//Author"):
            last = text_at(author, "LastName")
            fore = text_at(author, "ForeName")
            collective = text_at(author, "CollectiveName")
            authors.append(" ".join([fore, last]).strip() or collective)
        doi = ""
        for article_id in pubmed_data.findall("ArticleIdList/ArticleId") if pubmed_data is not None else []:
            if article_id.attrib.get("IdType") == "doi":
                doi = article_id.text or ""
        records.append(
            {
                "source_database": "PubMed",
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "journal": journal,
                "year": year,
                "publication_types": pub_types,
                "authors": "; ".join(authors),
                "doi": doi,
                "mesh_terms": mesh_terms,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
            }
        )
    for article in root.findall(".//PubmedBookArticle"):
        document = article.find("BookDocument")
        book = document.find("Book") if document is not None else None
        pmid = text_at(document, "PMID")
        title = text_at(document, "ArticleTitle") or text_at(book, "BookTitle")
        abstract = list_text(document, "Abstract/AbstractText")
        year = text_at(book, "PubDate/Year")
        journal = text_at(book, "BookTitle")
        publisher = text_at(book, "Publisher/PublisherName")
        authors = []
        for author in article.findall(".//Author"):
            last = text_at(author, "LastName")
            fore = text_at(author, "ForeName")
            collective = text_at(author, "CollectiveName")
            authors.append(" ".join([fore, last]).strip() or collective)
        doi = ""
        for article_id in document.findall("ArticleIdList/ArticleId") if document is not None else []:
            if article_id.attrib.get("IdType") == "doi":
                doi = article_id.text or ""
        records.append(
            {
                "source_database": "PubMed",
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "journal": journal or publisher,
                "year": year,
                "publication_types": "PubMed book/report",
                "authors": "; ".join(authors),
                "doi": doi,
                "mesh_terms": "",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
            }
        )
    return records


def main() -> None:
    ensure_dirs()
    config = read_yaml(CONFIG / "search_terms.yaml")
    query = config["academic_search_string"]
    start_year = config["date_range"]["start_year"]
    end_year = config["date_range"]["end_year"]
    pmids, result_count = search_pubmed(query, start_year, end_year)
    time.sleep(0.34)
    records = fetch_pubmed(pmids)
    write_csv(pd.DataFrame(records), DATA / "raw" / "pubmed_records.csv")
    write_csv(
        pd.DataFrame(
            [
                {
                    "source": "PubMed",
                    "interface_api": "NCBI E-utilities",
                    "date_searched": today_iso(),
                    "exact_search_string": query,
                    "result_count": result_count,
                    "downloaded_count": len(records),
                    "notes": f"Final main automated bibliographic database search; date range limited to {start_year}-{end_year}; retmax 500.",
                }
            ]
        ),
        DATA / "outputs" / "search_log.csv",
    )


if __name__ == "__main__":
    main()
