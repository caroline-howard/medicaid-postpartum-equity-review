# Medicaid Postpartum Coverage & Maternal Health Equity Systematic Review

This repository supports a reproducible PRISMA 2020-style systematic review portfolio project on Medicaid/CHIP postpartum coverage, care continuity, implementation, access, and maternal health equity. The workflow retrieves PubMed records, enriches and deduplicates metadata, prepares human screening files, supports title/abstract and full-text review, and generates PRISMA-style counts and planning files.

Automation supports searching, deduplication, scoring, triage, formatting, and validation only. Final title/abstract and full-text inclusion decisions are manual.

## Project Status

- PubMed Strategy E final search: 211 records.
- Full-text records assessed: 32.
- Final included empirical studies after full-text review: 28.
- Excluded after full text: 4.
- Blank full-text decisions remaining: 0.
- Manual synthesis-planning classification: complete for 28 included studies.
- Evidence extraction: not yet completed.
- Evidence synthesis/write-up: not yet started.

Full-text exclusion reasons:

- `unable_to_access_full_text`: 3
- `medicaid_only_payer_or_data_source`: 1

The final included-study table is saved at `data/outputs/final_evidence_table.csv`. This table documents studies included after full-text review; it should not be treated as completed evidence extraction or completed evidence synthesis.

## Set Up The Project

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run The Academic Search And Build Screening Files

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

PubMed is the main automated academic database source. The final PubMed query uses Strategy E. OpenAlex was tested during development but is exploratory only and excluded from PRISMA and methods counts because it returned an overly broad result set.

## Complete Title/Abstract Screening

Use the local browser screening app:

```bash
streamlit run scripts/10_screening_app.py
```

The app reads from and saves directly to `data/manual/screening_decisions.csv`. Allowed title/abstract decisions are `include_for_full_text`, `maybe`, and `exclude`. Exclusion reasons are required only for excluded records.

Spreadsheet alternative: `data/manual/screening_decisions.xlsx`.

## Validate Screening And Rebuild PRISMA Counts

```bash
python scripts/09_validate_screening_decisions.py
python scripts/07_build_prisma_counts.py
```

## Run Narrowed Empirical Triage

```bash
python scripts/12_timeline_scope_triage.py
```

The automation fields produced by this script are prioritization aids only. They do not make final screening decisions and should not be treated as automated exclusions.

## Complete Narrowed Empirical Screening

```bash
streamlit run scripts/11_narrowed_screening_app.py
```

The narrowed screening app saves `narrowed_screening_decision`, `narrowed_screening_reason`, `narrowed_notes`, and `evidence_role` to `data/manual/screening_decisions.csv`.

Allowed narrowed decisions:

- `retain_for_full_text`
- `background_only`
- `exclude_after_narrowing`
- `unsure_second_pass`

Retain peer-reviewed empirical or rigorous analytic studies only when Medicaid, CHIP, or public insurance is the postpartum coverage, eligibility, continuity, access, implementation, reimbursement, or policy mechanism. Exclude commentary, advocacy pieces, policy reviews, issue briefs, professional statements, narrative reviews, evidence syntheses outside the narrowed scope, records where Medicaid is only a payer/data source/covariate/sample descriptor, and studies whose data are entirely pre-2015.

Evidence roles should be based mainly on study data period and policy mechanism:

- `pre_2021_baseline_problem_evidence`
- `post_2021_policy_implementation_evidence`
- `service_specific_medicaid_access_policy`

Use `post_2021_policy_implementation_evidence` only when study data include post-2021, COVID-era, FFCRA, ARPA, unwinding, or implementation-period evidence. Studies published after 2021 but using only pre-2021 data should be categorized as `pre_2021_baseline_problem_evidence`.

## Complete Full-Text Review

The full-text review file is:

- `data/manual/full_text_review.csv`

The full-text review app is:

```bash
streamlit run scripts/14_full_text_review_app.py
```

Allowed full-text decisions are `include_core_evidence` and `exclude`. Excluded records require a populated `full_text_exclusion_reason`.

## Manual Synthesis-Planning Classification

This step occurs after full-text inclusion and before evidence extraction. It does not include or exclude studies. It organizes the 28 included studies for later extraction and writing by manually classifying each study by policy period and scope.

Run the manual classification app with:

```bash
streamlit run scripts/16_synthesis_manual_classification_app.py
```

Manual classification source of truth:

```text
data/manual/synthesis_manual_classification.csv
```

Manual policy-period field: `manual_policy_period_group`

Allowed values:

- `pre_policy_baseline_before_ffcra_or_extension`
- `post_ffcra_continuous_eligibility_period`
- `post_12_month_postpartum_extension_period`
- `multiple_policy_eras`
- `unsure_manual_review`

Definitions:

- `pre_policy_baseline_before_ffcra_or_extension`: evidence before FFCRA continuous eligibility and before formal 12-month postpartum extension adoption.
- `post_ffcra_continuous_eligibility_period`: evidence where the relevant postpolicy period is FFCRA/COVID public health emergency continuous Medicaid eligibility.
- `post_12_month_postpartum_extension_period`: evidence where the relevant postpolicy period is formal 12-month postpartum Medicaid extension adoption, generally 2022+ in adopting states.
- `multiple_policy_eras`: evidence spanning more than one relevant era.
- `unsure_manual_review`: unclear policy timing; needs review.

Manual era detail field: `manual_policy_eras_included`

This free-text field documents which eras are included, especially for `multiple_policy_eras`.

Manual scope field: `manual_scope_type`

Allowed values:

- `national`
- `multi_state`
- `single_state`
- `not_clearly_specified`

Manual notes field: `manual_synthesis_notes`

Manual synthesis-planning classification is used to plan evidence extraction and later synthesis. It is not a substitute for evidence extraction.

## Manual Synthesis-Planning Classification Results

These are manual synthesis-planning classification results, not evidence synthesis findings, PRISMA counts, or inclusion/exclusion decisions.

Policy-period classification:

| Manual policy period | Count |
| --- | ---: |
| `pre_policy_baseline_before_ffcra_or_extension` | 12 |
| `post_ffcra_continuous_eligibility_period` | 2 |
| `post_12_month_postpartum_extension_period` | 0 |
| `multiple_policy_eras` | 14 |
| `unsure_manual_review` | 0 |

Scope classification:

| Manual scope type | Count |
| --- | ---: |
| `national` | 7 |
| `multi_state` | 15 |
| `single_state` | 6 |
| `not_clearly_specified` | 0 |

Multiple-policy-era breakdown:

| Multiple policy era type | Count |
| --- | ---: |
| `pre_plus_ffcra` | 11 |
| `pre_plus_ffcra_plus_12_month_extension` | 2 |
| `pre_plus_12_month_extension` | 1 |
| `ffcra_plus_12_month_extension` | 0 |
| `multiple_eras_unclear` | 0 |

Evidence-structure interpretation: the manual classification shows that the included evidence is concentrated in pre-policy baseline and multiple-era studies, especially pre-FFCRA plus FFCRA continuous eligibility studies. No studies were classified as exclusively post-12-month postpartum extension period. This means later extraction and synthesis should distinguish FFCRA/COVID continuous eligibility evidence from formal 12-month postpartum extension evidence and should avoid treating all postpolicy evidence as the same.

## Extract Evidence

Evidence extraction has not yet been completed. The next step is to extract structured study details from the 28 included full-text studies.

The final included-study table is:

- `data/outputs/final_evidence_table.csv`

The broader evidence extraction template remains:

- `data/outputs/evidence_table.csv`

## Rebuild PRISMA Outputs After Updates

```bash
python scripts/09_validate_screening_decisions.py
python scripts/15_validate_full_text_review.py
python scripts/07_build_prisma_counts.py
```

## Key Files

- `data/raw/pubmed_records.csv`: PubMed records retrieved by the final academic search.
- `data/raw/openalex_records.csv`: exploratory development output only; not part of PRISMA or methods counts.
- `data/processed/deduplicated_records.csv`: PubMed records after DOI, PMID, and normalized-title deduplication.
- `data/processed/scored_records.csv`: deduplicated records with transparent relevance scores and triage suggestions.
- `data/manual/screening_decisions.csv`: manual title/abstract and narrowed screening decisions.
- `data/manual/screening_decisions.xlsx`: formatted title/abstract screening workbook.
- `data/manual/full_text_review.csv`: manual full-text review file with fields that will support later extraction.
- `data/manual/synthesis_manual_classification.csv`: manual synthesis-planning classification by policy period and scope.
- `data/manual/policy_sources_manual.csv`: manually curated policy and gray-literature source log.
- `data/outputs/evidence_table.csv`: evidence extraction template; extraction has not yet been completed.
- `data/outputs/final_evidence_table.csv`: final included empirical studies after full-text review; not completed evidence extraction.
- `data/outputs/manual_synthesis_classification_summary.csv`: manual policy-period by scope classification summary for synthesis planning.
- `data/outputs/prisma_counts.csv`: PRISMA-style count summary.
- `data/outputs/search_log.csv`: reproducible source-level search log.
- `data/outputs/screening_validation_report.md`: validation report for title/abstract screening decisions.
- `data/outputs/full_text_validation_report.md`: validation report for full-text review and final evidence table.
- `data/outputs/full_text_review_summary.md`: summary of completed full-text review counts.
- `data/outputs/narrowed_empirical_screening_summary.md`: summary of narrowed empirical screening, if generated.
- `data/outputs/narrowed_empirical_retained_records.csv`: retained narrowed empirical records, if generated.

## Human Review Note

Scripts retrieve, deduplicate, score, format, triage, and validate records. Final scholarly inclusion depends on documented human full-text review. Evidence extraction and narrative synthesis are separate next steps and have not yet been completed.
