# State Adoption and Implementation of Twelve-Month Postpartum Medicaid Coverage Extensions After the American Rescue Plan Act

This repository supports a reproducible PRISMA 2020-style systematic review pipeline for a portfolio paper on state adoption and implementation of 12-month postpartum Medicaid coverage extensions after the American Rescue Plan Act.

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
- `data/outputs/narrowed_empirical_screening_summary.md`: status summary for the frozen narrowed empirical screening workflow.
- `data/outputs/narrowed_empirical_retained_records.csv`: the 32 records retained for full-text review after narrowed empirical screening.
- `data/outputs/narrowed_screening_summary.md`: earlier status summary for the narrowed second-pass screening workflow.
- `data/outputs/timeline_scope_triage_report.md`: automation-prioritization report for narrowed second-pass screening.

## Human Review Required

Automation keeps all candidate records available for human screening. Human reviewers must complete title/abstract decisions, full-text eligibility decisions, evidence extraction, and final synthesis inclusion decisions. The automated `automation_suggestion` field is only a triage aid.

Relevance scoring is documented in `paper/methods_search_appendix.md` and implemented in `scripts/05_score_relevance.py`. Scores are calculated from transparent keyword-group hits in the title and abstract, with each group capped at 3 points. Scores are used only to prioritize human screening order.

There is no required number of final included studies. Final inclusion depends on eligibility criteria and documented human screening decisions. Practical record-volume targets are used only as quality checks: approximately 100-400 PubMed candidate records before deduplication is a useful initial target; fewer than 50 PubMed records should be flagged as potentially too narrow; more than 750 should be flagged as potentially too broad; and a feasible portfolio systematic review often has about 10-25 core evidence sources plus separately labeled policy/context sources.

OpenAlex was explored during development but is not retained in the final main search workflow because it produced an overly broad result set.

## Current Paper Status

This is an in-progress systematic review portfolio paper. The final scope is state adoption and implementation of 12-month postpartum Medicaid coverage extensions after the American Rescue Plan Act. The research question is: How has state adoption of 12-month postpartum Medicaid coverage extensions after 2021 been studied in relation to postpartum access, coverage continuity, and equity?

The final academic database search uses PubMed Strategy E, with PubMed as the main automated academic database source. OpenAlex was exploratory only and is not part of the final PRISMA workflow.

Title/abstract screening has been completed for 211 PubMed records. Screening results were:

- `include_for_full_text`: 136
- `maybe`: 30
- `exclude`: 45

Exclusion reasons for the 45 excluded records were:

- `wrong_policy_or_intervention`: 19
- `not_medicaid_or_chip`: 10
- `not_postpartum`: 9
- `wrong_population`: 3
- `opinion_without_data_or_policy_detail`: 2
- `duplicate`: 1
- `not_us_based`: 1

A total of 166 records were marked `include_for_full_text` or `maybe` in the initial broad screen. Before full-text review, the project was narrowed to an empirical scoping-review evidence map. The narrowed workflow retains only peer-reviewed empirical primary studies where Medicaid, CHIP, or public insurance is the postpartum coverage, eligibility, continuity, access, implementation, reimbursement, or policy mechanism.

Narrowed empirical screening is complete. Thirty-two records are retained for full-text review:

- `post_2021_policy_implementation_evidence`: 16
- `pre_2021_baseline_problem_evidence`: 14
- `service_specific_medicaid_access_policy`: 2

No records were excluded by automation. Final inclusion decisions have not been made because full-text retrieval, eligibility review, and evidence synthesis have not been completed. The next step is full-text retrieval and eligibility review for the 32 records retained after narrowing.

## Title/Abstract Screening

Initial broad title/abstract screening is complete. The original decisions are preserved in `human_title_abstract_decision` and `human_title_abstract_exclusion_reason`.

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

## Narrowed Empirical Screening

The narrowed empirical screening rules are documented in `docs/narrowed_empirical_screening_rules.md`. The final retained full-text pool is frozen to 32 peer-reviewed empirical primary studies. Policy commentaries, issue briefs, professional statements, narrative reviews, evidence syntheses, Medicaid-only payer/data-source records, and entirely pre-2015 cohorts are excluded after narrowing.

The timeline/scope triage script may be used to audit automation-assisted prioritization fields:

```bash
python scripts/12_timeline_scope_triage.py
```

The script writes `timeline_scope_score`, `timeline_scope_tier`, `timeline_scope_matched_terms`, `automation_narrowing_suggestion`, and `automation_narrowing_note` to `data/manual/screening_decisions.csv`. These fields are automation suggestions for prioritization only; they are not final narrowed screening decisions and are not copied into `narrowed_screening_decision`.

Use the narrowed screening app to audit or adjust one record at a time:

```bash
streamlit run scripts/11_narrowed_screening_app.py
```

The narrowed app reads from and saves directly back to `data/manual/screening_decisions.csv`. It displays automation suggestions as guidance and saves only the current record's manual narrowed fields: `narrowed_screening_decision`, `narrowed_screening_reason`, `narrowed_notes`, and `evidence_role`.

Allowed narrowed decisions are `retain_for_full_text`, `background_only`, `exclude_after_narrowing`, and `unsure_second_pass`. Full-text retrieval should now proceed for the 32 records marked `retain_for_full_text`.

## PRISMA 2020 Support

The search log, deduplication outputs, screening files, full-text review file, and evidence table are designed to support a PRISMA 2020 flow diagram and methods appendix. `records_marked_ineligible_by_automation` is fixed at `0` unless an automated exclusion rule is explicitly approved later.
