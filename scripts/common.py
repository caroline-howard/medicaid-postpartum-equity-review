from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path
from typing import Iterable

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONFIG = ROOT / "config"


def ensure_dirs() -> None:
    for path in [
        DATA / "raw",
        DATA / "processed",
        DATA / "manual",
        DATA / "outputs",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def today_iso() -> str:
    return date.today().isoformat()


def require_columns(df: pd.DataFrame, columns: Iterable[str], source: str) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns: {', '.join(missing)}")


def read_csv_if_exists(path: Path, columns: list[str] | None = None) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path, dtype=str).fillna("")
    return pd.DataFrame(columns=columns or [])


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def append_search_log(row: dict) -> None:
    path = DATA / "outputs" / "search_log.csv"
    columns = [
        "source",
        "interface_api",
        "date_searched",
        "exact_search_string",
        "result_count",
        "downloaded_count",
        "notes",
    ]
    existing = read_csv_if_exists(path, columns)
    updated = pd.concat([existing, pd.DataFrame([row])], ignore_index=True)
    write_csv(updated[columns], path)


def normalize_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_doi(value: object) -> str:
    text = normalize_text(value)
    return text.replace("https doi org ", "").replace("doi ", "").strip()


def join_values(values: Iterable[object]) -> str:
    cleaned = []
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            cleaned.append(text)
    return "; ".join(cleaned)
