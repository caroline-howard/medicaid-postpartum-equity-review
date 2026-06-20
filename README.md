# Medicaid Postpartum Coverage & Maternal Health Equity Systematic Review

This repository supports a reproducible PRISMA 2020-style systematic review pipeline for a portfolio paper on Medicaid postpartum coverage extensions, access to care, continuity of coverage, and maternal health equity in the United States.

The main PRISMA workflow retrieves candidate academic records from PubMed, enriches metadata with Crossref when needed, deduplicates records, applies transparent relevance scoring, prepares human screening files, tracks policy/context sources, and builds PRISMA-style count outputs. It does not make final scholarly inclusion decisions.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run The Pipeline

Run scripts from the repository root:

```bash
python scripts/01_pubmed_search.py
python scripts/03_crossref_enrich.py
python scripts/04_combine_and_deduplicate.py
python scripts/05_score_relevance.py
python scripts/06_build_screening_workbook.py
python scripts/08_build_evidence_table_template.py
python scripts/07_build_prisma_counts.py
```

## Key Outputs

- `data/raw/pubmed_records.csv`: candidate records retrieved from PubMed.
- `data/raw/openalex_records.csv`: exploratory development output only; not part of main screening or PRISMA counts.
- `data/processed/deduplicated_records.csv`: PubMed candidate records after DOI, PMID, and normalized-title deduplication.
- `data/processed/scored_records.csv`: deduplicated records with transparent rule-based relevance scores and automation suggestions.
- `data/manual/screening_decisions.csv`: source file for human title/abstract screening decisions.
- `data/manual/screening_decisions.xlsx`: formatted title/abstract screening workbook.
- `data/manual/full_text_review.csv`: human full-text eligibility file.
- `data/manual/policy_sources_manual.csv`: manually curated policy and gray-literature source log.
- `data/outputs/evidence_table.csv`: evidence extraction template.
- `data/outputs/prisma_counts.csv`: PRISMA-style count summary.
- `data/outputs/search_log.csv`: reproducible source-level search log.
- `data/outputs/screening_validation_report.md`: validation report for completed title/abstract screening decisions.

## Human Review Required

Automation keeps all candidate records available for human screening. Human reviewers must complete title/abstract decisions, full-text eligibility decisions, evidence extraction, and final synthesis inclusion decisions. The automated `automation_suggestion` field is only a triage aid.

There is no required number of final included studies. Final inclusion depends on eligibility criteria and documented human screening decisions. Practical record-volume targets are used only as quality checks: approximately 100-400 PubMed candidate records before deduplication is a useful initial target; fewer than 50 PubMed records should be flagged as potentially too narrow; more than 750 should be flagged as potentially too broad; and a feasible portfolio systematic review often has about 10-25 core evidence sources plus separately labeled policy/context sources.

OpenAlex was explored during development but is not retained in the final main search workflow because it produced an overly broad result set.

## Title/Abstract Screening

Use the local browser screening app for human title/abstract screening:

```bash
streamlit run scripts/10_screening_app.py
```

The app reads from and saves directly back to `data/manual/screening_decisions.csv`. Review one record at a time, fill in `human_title_abstract_decision` using `include_for_full_text`, `maybe`, or `exclude`, and add `human_title_abstract_exclusion_reason` only for records marked `exclude`. The app requires an exclusion reason before saving an excluded record.

If you prefer a spreadsheet workflow and have compatible software, open `data/manual/screening_decisions.xlsx` for the same title/abstract screening fields.

The workbook is sorted by `relevance_score` from highest to lowest, with filters, frozen headers, wrapped title/abstract text, and dropdowns for valid decisions and exclusion reasons. The screening rules are documented in `docs/title_abstract_screening_guide.md`.

Before rerunning PRISMA counts, validate the CSV:

```bash
python scripts/09_validate_screening_decisions.py
```

After title/abstract decisions are complete and validated, rerun:

```bash
python scripts/07_build_prisma_counts.py
```

## PRISMA 2020 Support

The search log, deduplication outputs, screening files, full-text review file, and evidence table are designed to support a PRISMA 2020 flow diagram and methods appendix. `records_marked_ineligible_by_automation` is fixed at `0` unless an automated exclusion rule is explicitly approved later.
