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
python scripts/09_build_automation_screening_outputs.py
python scripts/07_build_prisma_counts.py
python scripts/10_validate_screening_automation.py
```

## Key Outputs

- `data/raw/pubmed_records.csv`: candidate records retrieved from PubMed.
- `data/raw/openalex_records.csv`: exploratory development output only; not part of main screening or PRISMA counts unless explicitly approved later.
- `data/processed/deduplicated_records.csv`: PubMed candidate records after DOI, PMID, and normalized-title deduplication.
- `data/processed/scored_records.csv`: deduplicated records with transparent rule-based relevance scores and automation suggestions.
- `data/manual/screening_decisions.csv`: human title/abstract screening file.
- `data/manual/automation_exclusion_validation_sample.csv`: validation sample for records marked `automation_exclude`.
- `data/manual/full_text_review.csv`: human full-text eligibility file.
- `data/manual/policy_sources_manual.csv`: manually curated policy and gray-literature source log.
- `data/outputs/evidence_table.csv`: evidence extraction template.
- `data/outputs/automation_screening_report.md`: automation tier counts, screening burden, and validation guidance.
- `data/outputs/prisma_counts.csv`: PRISMA-style count summary.
- `data/outputs/search_log.csv`: reproducible source-level search log.

## Human Review Required

Automation keeps all candidate records available for human screening. Human reviewers must complete title/abstract decisions, full-text eligibility decisions, evidence extraction, and final synthesis inclusion decisions. The automated `automation_suggestion` field is only a triage aid.

There is no required number of final included studies. Final inclusion depends on eligibility criteria and documented human screening decisions. Practical record-volume targets are used only as quality checks: approximately 100-400 PubMed candidate records before deduplication is a useful initial target; fewer than 50 PubMed records should be flagged as potentially too narrow; more than 750 should be flagged as potentially too broad; and a feasible portfolio systematic review often has about 10-25 core evidence sources plus separately labeled policy/context sources.

OpenAlex was tested during development but is not retained in the final main search workflow because the query returned an overly broad result set. OpenAlex records are not included in `data/manual/screening_decisions.csv`, `data/outputs/prisma_counts.csv`, or the main PRISMA database count unless explicitly approved later.

## Automation-Assisted Screening

Run `scripts/05_score_relevance.py` to create concept flags and conservative automation tiers. Then run `scripts/06_build_screening_workbook.py`, `scripts/09_build_automation_screening_outputs.py`, and `scripts/07_build_prisma_counts.py`.

Review `data/outputs/automation_screening_report.md` first. Manually screen `tier_1_likely_include` and `tier_2_maybe` records before lower-priority records. Review `data/manual/automation_exclusion_validation_sample.csv` to validate sampled `automation_exclude` records and rescue any record that appears incorrectly excluded. Rerun `scripts/07_build_prisma_counts.py` after screening decisions change.

## PRISMA 2020 Support

The search log, deduplication outputs, screening files, full-text review file, and evidence table are designed to support a PRISMA 2020 flow diagram and methods appendix. Records marked `automation_exclude` are counted separately in `records_marked_ineligible_by_automation`.
