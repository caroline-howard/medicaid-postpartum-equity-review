# Methods Search Appendix

## Databases And Interfaces

- PubMed through NCBI E-utilities.
- Crossref through the Crossref Works API for metadata enrichment when needed.
- Manually curated policy and gray-literature source logs for context only.

PubMed is the final automated academic database source for the PRISMA workflow. OpenAlex was explored during development but was not retained because the query returned an overly broad result set. OpenAlex records are excluded from final PRISMA and methods counts.

## Exact Academic Search String

The final PubMed search uses Strategy E:

`(Medicaid[Title/Abstract] OR CHIP[Title/Abstract]) AND (postpartum[Title/Abstract] OR post-partum[Title/Abstract] OR postnatal[Title/Abstract]) AND (coverage[Title/Abstract] OR eligibility[Title/Abstract] OR extension[Title/Abstract] OR "continuous coverage"[Title/Abstract] OR churn[Title/Abstract] OR redetermination[Title/Abstract])`

## Limits

- Geography: United States.
- Date range: 2014-2026.
- Main academic source: PubMed.
- Metadata enrichment: Crossref when needed.

## Search Logging

The PubMed search script writes source, interface/API, search date, exact search string, result count, downloaded count, and notes to `data/outputs/search_log.csv`.

## Deduplication Logic

PubMed records are deduplicated before screening in this order:

1. DOI when available.
2. PMID when available.
3. Normalized title when DOI and PMID are unavailable.

The combined file, deduplicated file, and duplicate-record file are saved separately so the process can be audited.

## Automation Role

Automation retrieves records, cleans metadata, deduplicates records, scores relevance, prepares screening files, supports triage, and builds PRISMA-style count outputs. No records were excluded by automation in the final Strategy E workflow. `records_marked_ineligible_by_automation` remains `0`.

Final title/abstract screening, narrowed empirical screening, and full-text inclusion decisions were manual.

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

The script writes the raw group hit counts plus the final `relevance_score` to `data/processed/scored_records.csv`. It also writes `automation_suggestion` as a triage label: `likely_include` for scores of 8 or higher, `maybe` for scores from 4 to 7, and `likely_exclude` for scores below 4. These labels are not screening decisions.

## Screening Process

PubMed Strategy E identified 211 records. After deduplication, 211 records remained for first-pass title/abstract screening.

First-pass title/abstract screening was broad and inclusive. Human screening decisions were:

- `include_for_full_text`: 136
- `maybe`: 30
- `exclude`: 45

Exclusion reasons for the 45 first-pass excluded records were:

- `wrong_policy_or_intervention`: 19
- `not_medicaid_or_chip`: 10
- `not_postpartum`: 9
- `wrong_population`: 3
- `opinion_without_data_or_policy_detail`: 2
- `duplicate`: 1
- `not_us_based`: 1

The review was then narrowed to an empirical scoping-review evidence map. Retained full-text records had to be peer-reviewed empirical primary studies or rigorous original analyses where Medicaid, CHIP, or public insurance was the postpartum coverage, eligibility, continuity, access, implementation, reimbursement, or policy mechanism. Policy/commentary pieces, professional statements, issue briefs, narrative reviews, evidence syntheses, broad background articles, Medicaid-only payer/data-source records, and studies with data or cohorts entirely before 2015 were excluded from the retained empirical evidence map.

The narrowed empirical screen retained 32 records for full-text review.

## Full-Text Review

Human reviewers completed full-text review in `data/manual/full_text_review.csv`. Allowed final full-text decisions were:

- `include_core_evidence`
- `exclude`

Final full-text review counts were:

- Full-text records assessed: 32
- Included core empirical evidence: 28
- Excluded after full text: 4
- Blank full-text decisions remaining: 0

Included empirical evidence categories:

- `post_2021_policy_implementation_evidence`: 14
- `pre_2021_baseline_problem_evidence`: 13
- `service_specific_medicaid_access_policy`: 1

Full-text exclusion reasons:

- `unable_to_access_full_text`: 3
- `medicaid_only_payer_or_data_source`: 1

The final included empirical evidence table is saved at `data/outputs/final_evidence_table.csv`.

## Record Volume Guidance

There is no required number of included studies for this review. Final inclusion depends on eligibility criteria and documented human screening decisions.

Practical record-volume targets are quality checks only:

- Target initial candidate records after database searching: approximately 100-400 records before deduplication.
- If fewer than 50 PubMed records are retrieved, flag the search as potentially too narrow and suggest broader search terms.
- If more than 750 PubMed records are retrieved, flag the search as potentially too broad and suggest narrower terms or additional filters.
- Do not exclude records simply to hit a target number.
- Do not include weak or off-topic records just to reach a target number.
- The final number of included studies should come from the documented screening and full-text eligibility process.

## PRISMA Count Definitions

`scripts/07_build_prisma_counts.py` reads the PubMed-only search log, deduplicated records, screening decisions, full-text review decisions, and final evidence table. It outputs `data/outputs/prisma_counts.csv` with database identification counts, duplicate removals, human screening exclusions, full-text retrieval and eligibility counts, included studies, reports of included studies, and a record-volume quality flag.
