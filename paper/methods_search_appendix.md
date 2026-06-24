# Methods Search Appendix

## Databases And Interfaces

- PubMed through NCBI E-utilities.
- Crossref through the Crossref Works API for metadata enrichment.
- Manually curated policy and gray-literature sources tracked in `data/manual/policy_sources_manual.csv` as development/context documentation only.

OpenAlex was explored during development but was not retained in the final main workflow because it produced an overly broad result set.

This repository supports an in-progress narrowed empirical scoping-review portfolio paper on Medicaid/CHIP postpartum coverage, continuity, implementation, access, and equity evidence. PubMed is the main automated academic database source, and the final PubMed search uses Strategy E. OpenAlex was exploratory only and is not part of the final PRISMA workflow.

## Exact Academic Search String

`(Medicaid[Title/Abstract] OR CHIP[Title/Abstract]) AND (postpartum[Title/Abstract] OR post-partum[Title/Abstract] OR postnatal[Title/Abstract]) AND (coverage[Title/Abstract] OR eligibility[Title/Abstract] OR extension[Title/Abstract] OR "continuous coverage"[Title/Abstract] OR churn[Title/Abstract] OR redetermination[Title/Abstract])`

## Limits

- Geography: United States.
- Date range: 2014-2026.
- Sources: PubMed records with optional Crossref metadata enrichment.

## Search Logging

The PubMed search script writes source, interface/API, search date, exact search string, result count, downloaded count, and notes to `data/outputs/search_log.csv`.

## Deduplication Logic

PubMed records are deduplicated before screening in this order:

1. DOI when available.
2. PMID when available.
3. Normalized title when DOI and PMID are unavailable.

The combined file, deduplicated file, and duplicate-record file are saved separately so the process can be audited.

## Automation Role

Automation retrieves records, cleans metadata, deduplicates records, scores relevance, prepares screening files, and builds PRISMA-style count outputs. No records are excluded by automation in the final Strategy E workflow. `records_marked_ineligible_by_automation` remains `0`.

## Relevance Scoring Logic

Relevance scores are used only to sort and triage records for human title/abstract screening. They do not determine inclusion or exclusion, and no record is removed on the basis of score.

The scoring logic is implemented in `scripts/05_score_relevance.py`. For each deduplicated record, the script concatenates the title and abstract, normalizes the text to lowercase alphanumeric tokens, and searches for terms in five keyword groups:

| Keyword group | Terms |
| --- | --- |
| `medicaid_chip` | `medicaid`, `chip`, `children health insurance`, `children s health insurance` |
| `postpartum` | `postpartum`, `post partum`, `postnatal`, `pregnancy`, `pregnant`, `maternal`, `after delivery`, `after childbirth` |
| `coverage_policy` | `coverage`, `eligibility`, `extension`, `continuous coverage`, `churn`, `redetermination`, `waiver`, `state plan`, `section 1115`, `insurance continuity` |
| `outcomes` | `access`, `continuity`, `behavioral health`, `morbidity`, `mortality`, `equity`, `disparities`, `postpartum visit`, `emergency department`, `ed use`, `care coordination` |
| `us_state_policy` | `united states`, `u s`, `state`, `medicaid agency`, `section 1115`, `cms`, `federal`, `county` |

For each group, the script counts the number of group terms found in the normalized title/abstract text. Points for each group are capped at 3, using `min(group_hits, 3)`. The final `relevance_score` is the sum of capped points across the five groups, so the maximum possible score is 15.

The script writes the raw group hit counts (`medicaid_chip_hits`, `postpartum_hits`, `coverage_policy_hits`, `outcomes_hits`, and `us_state_policy_hits`) plus the final `relevance_score` to `data/processed/scored_records.csv`. It also writes `automation_suggestion` as a triage label: `likely_include` for scores of 8 or higher, `maybe` for scores from 4 to 7, and `likely_exclude` for scores below 4. These labels are not screening decisions.

## Screening Process

Human reviewers complete title/abstract screening in `data/manual/screening_decisions.csv`. Initial broad title/abstract screening has been completed for 211 records. Allowed first-pass title/abstract decisions are:

- `include_for_full_text`
- `maybe`
- `exclude`

Allowed exclusion reasons are:

- `wrong_population`
- `wrong_policy_or_intervention`
- `not_medicaid_or_chip`
- `not_postpartum`
- `not_us_based`
- `no_relevant_outcome`
- `background_only` (first-pass broad-screen reason only)
- `opinion_without_data_or_policy_detail`
- `duplicate`
- `other`

Completed title/abstract screening results were:

- `include_for_full_text`: 136
- `maybe`: 30
- `exclude`: 45

Exclusion reasons for excluded records were:

- `wrong_policy_or_intervention`: 19
- `not_medicaid_or_chip`: 10
- `not_postpartum`: 9
- `wrong_population`: 3
- `opinion_without_data_or_policy_detail`: 2
- `duplicate`: 1
- `not_us_based`: 1

The 166 records marked `include_for_full_text` or `maybe` were then assessed in a narrowed empirical second-pass screen before full-text review. The project is now documented as a narrowed empirical scoping review. The narrowed evidence map retains only peer-reviewed empirical primary studies where Medicaid, CHIP, or public insurance is the postpartum coverage, eligibility, continuity, access, implementation, reimbursement, or policy mechanism.

The narrowed empirical screen excluded policy opinion pieces, commentaries, issue briefs, general policy reports, professional statements, narrative policy reviews, systematic reviews, scoping reviews, meta-analyses, broad maternal health background articles with only a minor Medicaid mention, records where Medicaid is only a payer/data source/covariate/subgroup, and studies with data or cohorts entirely before 2015.

Narrowed second-pass decisions are stored in `narrowed_screening_decision`. The final retained evidence-map category is:

- `retain_for_full_text`

Exclusions are stored as:

- `exclude_after_narrowing`

Historical values such as `background_only` and `unsure_second_pass` may remain in scripts or older outputs for auditability, but they are not retained evidence-map source types.

Final narrowed exclusion reasons include:

- `pre_2015_cohort`
- `not_medicaid_postpartum_policy`
- `outside_final_empirical_scope`
- `not_empirical_study`
- `policy_or_commentary_only`
- `evidence_synthesis_not_primary_study`

Historical or triage-oriented reason values may remain in the CSV for transparency, but they are not the final narrowed empirical inclusion logic.

Narrowed empirical screening is complete. Thirty-two records were retained for full-text review:

- `post_2021_policy_implementation_evidence`: 16
- `pre_2021_baseline_problem_evidence`: 14
- `service_specific_medicaid_access_policy`: 2

No records were excluded by automation. Final inclusion decisions have not been made because full-text retrieval, eligibility review, and evidence synthesis have not been completed. The next step is full-text retrieval and eligibility review for the 32 records retained after narrowing.

Timeline-based automation triage was used only to prioritize and audit review. The triage script (`scripts/12_timeline_scope_triage.py`) searches title and abstract text for timing terms, extended postpartum coverage terms, Medicaid/CHIP policy mechanism terms, and access/continuity/equity outcome terms. It writes a transparent score, tier, matched-term list, suggestion, and note to the screening file. These fields are used only to prioritize human review and do not populate `narrowed_screening_decision` or determine final inclusion/exclusion.

## Full-Text Review

Human reviewers complete full-text review in `data/manual/full_text_review.csv`. The final evidence synthesis should include only peer-reviewed empirical primary studies that pass full-text eligibility review. Template values may include historical categories, but policy/context or background records are not retained evidence-map source types.

- `include_core_evidence`
- `exclude`

## Record Volume Guidance

There is no required number of included studies for this narrowed empirical scoping review. Final inclusion depends on eligibility criteria and human screening decisions.

Practical record-volume targets are quality checks only:

- Target initial candidate records after database searching: approximately 100-400 records before deduplication.
- If fewer than 50 PubMed records are retrieved, flag the search as potentially too narrow and suggest broader search terms.
- If more than 750 records are retrieved, flag the search as potentially too broad and suggest narrower search terms or additional filters.
- Do not exclude records simply to hit a target number.
- Do not include weak or off-topic records just to reach a target number.
- The final number of included studies should come from the documented screening and full-text eligibility process.

## PRISMA Count Definitions

`scripts/07_build_prisma_counts.py` reads the PubMed-only search log, deduplicated records, duplicate records, screening decisions, full-text review decisions, and evidence table. It outputs `data/outputs/prisma_counts.csv` with database identification counts, duplicate removals, human screening exclusions, full-text retrieval and eligibility counts, included studies, reports of included studies, and a record-volume quality flag.
