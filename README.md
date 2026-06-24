# Medicaid/CHIP Postpartum Coverage, Continuity, Implementation, Access, And Equity

This repository supports a reproducible PRISMA 2020-style workflow for a narrowed empirical scoping review of Medicaid/CHIP postpartum coverage, continuity, implementation, access, and equity evidence.

The workflow uses PubMed Strategy E, broad first-pass title/abstract screening, and a narrowed empirical second-pass screen. Automation supports retrieval, deduplication, scoring, triage, formatting, and validation. Final scholarly inclusion depends on documented human full-text review and evidence extraction.

## 1. Set Up The Project

Run commands from the repository root.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Run The Academic Search And Build Screening Files

Run the pipeline scripts in this order:

```bash
python scripts/01_pubmed_search.py
python scripts/03_crossref_enrich.py
python scripts/04_combine_and_deduplicate.py
python scripts/05_score_relevance.py
python scripts/06_build_screening_workbook.py
python scripts/08_build_evidence_table_template.py
python scripts/07_build_prisma_counts.py
```

These scripts retrieve PubMed records, enrich metadata when possible, deduplicate records, score title/abstract relevance for triage, create screening files, create the evidence extraction template, and build PRISMA-style counts.

## 3. Complete Title/Abstract Screening

Run the local browser screening app:

```bash
streamlit run scripts/10_screening_app.py
```

The app reads from and saves directly to `data/manual/screening_decisions.csv`.

Allowed first-pass title/abstract decisions are:

- `include_for_full_text`
- `maybe`
- `exclude`

Exclusion reasons are required only for records marked `exclude`.

Spreadsheet alternative:

- `data/manual/screening_decisions.xlsx`

## 4. Validate Title/Abstract Screening And Rebuild PRISMA Counts

After title/abstract screening updates, run:

```bash
python scripts/09_validate_screening_decisions.py
python scripts/07_build_prisma_counts.py
```

## 5. Run Narrowed Empirical Triage

Run the timeline/scope triage script:

```bash
python scripts/12_timeline_scope_triage.py
```

The script writes automation fields such as `timeline_scope_score`, `timeline_scope_tier`, `timeline_scope_matched_terms`, `automation_narrowing_suggestion`, and `automation_narrowing_note` to `data/manual/screening_decisions.csv`.

These fields are prioritization aids only. They are not final screening decisions.

## 6. Complete Narrowed Empirical Screening

Run the narrowed screening app:

```bash
streamlit run scripts/11_narrowed_screening_app.py
```

The app reads from and saves directly to `data/manual/screening_decisions.csv`. It saves the current record's manual narrowed fields:

- `narrowed_screening_decision`
- `narrowed_screening_reason`
- `narrowed_notes`
- `evidence_role`

Allowed narrowed decisions are:

- `retain_for_full_text`
- `background_only`
- `exclude_after_narrowing`
- `unsure_second_pass`

Narrowed screening rule:

Retain peer-reviewed empirical or rigorous analytic studies only when Medicaid, CHIP, or public insurance is the postpartum coverage, eligibility, continuity, access, implementation, reimbursement, or policy mechanism.

Exclude commentary, advocacy pieces, policy reviews, issue briefs, professional statements, narrative reviews, evidence syntheses outside the narrowed scope, records where Medicaid is only a payer, data source, covariate, or sample descriptor, and studies whose data are entirely pre-2015.

Assign `evidence_role` mainly from the study data period and policy mechanism:

- `pre_2021_baseline_problem_evidence`
- `post_2021_policy_implementation_evidence`
- `service_specific_medicaid_access_policy`

Use `post_2021_policy_implementation_evidence` only when study data include post-2021, COVID-era, FFCRA, ARPA, unwinding, or implementation-period evidence. Studies published after 2021 but using only pre-2021 data should be categorized as `pre_2021_baseline_problem_evidence`.

## 7. Proceed To Full-Text Review

Use the narrowed retained-record export to guide full-text retrieval:

- `data/outputs/narrowed_empirical_retained_records.csv`

Record full-text retrieval and eligibility decisions in:

- `data/manual/full_text_review.csv`

## 8. Extract Evidence

Extract eligible studies into:

- `data/outputs/evidence_table.csv`

## 9. Rebuild PRISMA Outputs After Updates

After screening, full-text, or extraction updates, rerun:

```bash
python scripts/09_validate_screening_decisions.py
python scripts/07_build_prisma_counts.py
```

## 10. Key Files

- `data/raw/pubmed_records.csv`: candidate records retrieved from PubMed.
- `data/raw/openalex_records.csv`: exploratory development output only; not part of the main PRISMA workflow.
- `data/processed/deduplicated_records.csv`: records after DOI, PMID, and normalized-title deduplication.
- `data/processed/scored_records.csv`: deduplicated records with relevance scores and automation triage labels.
- `data/manual/screening_decisions.csv`: main manual screening file for title/abstract and narrowed empirical decisions.
- `data/manual/screening_decisions.xlsx`: formatted spreadsheet alternative for title/abstract screening.
- `data/manual/full_text_review.csv`: full-text retrieval and eligibility review file.
- `data/manual/policy_sources_manual.csv`: manually curated policy and gray-literature source log retained as context/development documentation.
- `data/outputs/evidence_table.csv`: evidence extraction template.
- `data/outputs/prisma_counts.csv`: PRISMA-style count summary.
- `data/outputs/search_log.csv`: reproducible source-level search log.
- `data/outputs/screening_validation_report.md`: validation report for screening decisions.
- `data/outputs/narrowed_empirical_screening_summary.md`: summary of narrowed empirical screening.
- `data/outputs/narrowed_empirical_retained_records.csv`: records retained for full-text review after narrowed empirical screening.

## Human Review Note

Scripts retrieve, deduplicate, score, format, triage, and validate records. They do not make final scholarly inclusion decisions. Final inclusion depends on documented human full-text review and evidence extraction.
