# Methods Search Appendix

## Databases And Interfaces

- PubMed through NCBI E-utilities.
- Crossref through the Crossref Works API for metadata enrichment.
- Manually curated policy and gray-literature sources tracked in `data/manual/policy_sources_manual.csv`.

OpenAlex was explored during development but was not retained in the final main workflow because it produced an overly broad result set.

## Exact Academic Search String

`(Medicaid[Title/Abstract] OR CHIP[Title/Abstract]) AND (postpartum[Title/Abstract] OR post-partum[Title/Abstract] OR postnatal[Title/Abstract]) AND (coverage[Title/Abstract] OR eligibility[Title/Abstract] OR extension[Title/Abstract] OR "continuous coverage"[Title/Abstract] OR churn[Title/Abstract] OR redetermination[Title/Abstract])`

## Limits

- Geography: United States.
- Date range: 2014-2026.
- Sources: PubMed, Crossref metadata enrichment, and manually curated policy/context sources.

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

## Screening Process

Human reviewers complete title/abstract screening in `data/manual/screening_decisions.csv`. Allowed title/abstract decisions are:

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
- `background_only`
- `opinion_without_data_or_policy_detail`
- `duplicate`
- `other`

## Full-Text Review

Human reviewers complete full-text review in `data/manual/full_text_review.csv`. Allowed full-text decisions are:

- `include_core_evidence`
- `include_policy_context`
- `background_only`
- `exclude`

## Record Volume Guidance

There is no required number of included studies for this systematic review. Final inclusion depends on eligibility criteria and human screening decisions.

Practical record-volume targets are quality checks only:

- Target initial candidate records after database searching: approximately 100-400 records before deduplication.
- If fewer than 50 PubMed records are retrieved, flag the search as potentially too narrow and suggest broader search terms.
- If more than 750 records are retrieved, flag the search as potentially too broad and suggest narrower search terms or additional filters.
- Target final included sources for a feasible portfolio systematic review: approximately 10-25 core evidence sources, plus separately labeled policy/context sources if relevant.
- Do not exclude records simply to hit a target number.
- Do not include weak or off-topic records just to reach a target number.
- The final number of included studies should come from the documented screening and full-text eligibility process.

## PRISMA Count Definitions

`scripts/07_build_prisma_counts.py` reads the PubMed-only search log, deduplicated records, duplicate records, screening decisions, full-text review decisions, and evidence table. It outputs `data/outputs/prisma_counts.csv` with database identification counts, duplicate removals, human screening exclusions, full-text retrieval and eligibility counts, included studies, reports of included studies, and a record-volume quality flag.
