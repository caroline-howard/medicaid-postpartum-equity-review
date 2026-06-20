# Data Dictionary

## `data/outputs/search_log.csv`

- `source`: Database or source name.
- `interface_api`: API or interface used.
- `date_searched`: Date the search script was run.
- `exact_search_string`: Search string used.
- `result_count`: Total results reported by the source.
- `downloaded_count`: Records downloaded into the repository.
- `notes`: Search limits or implementation notes.

## `data/processed/deduplicated_records.csv`

- `record_id`: Stable local record identifier.
- `title`: Record title.
- `abstract`: Abstract or available description.
- `year`: Publication year.
- `journal`: Journal or source title.
- `doi`: Digital object identifier.
- `pmid`: PubMed identifier.
- `url`: Record URL.
- `authors`: Author list.
- `source_database`: Source retained from first matching record.
- `source_databases_found`: Databases where the record appeared.

## `data/processed/scored_records.csv`

Includes deduplicated record fields plus transparent relevance-score components:

- `medicaid_chip_hits`
- `postpartum_hits`
- `coverage_policy_hits`
- `outcomes_hits`
- `us_state_policy_hits`
- `relevance_score`
- `automation_suggestion`

## `data/manual/screening_decisions.csv`

Human title/abstract screening file. Automation suggestions are triage aids only.

Allowed title/abstract decisions: `include_for_full_text`, `maybe`, `exclude`.

Allowed exclusion reasons: `wrong_population`, `wrong_policy_or_intervention`, `not_medicaid_or_chip`, `not_postpartum`, `not_us_based`, `no_relevant_outcome`, `background_only`, `opinion_without_data_or_policy_detail`, `duplicate`, `other`.

## `data/manual/full_text_review.csv`

Human full-text review file.

Allowed full-text decisions: `include_core_evidence`, `include_policy_context`, `background_only`, `exclude`.

## `data/outputs/evidence_table.csv`

Evidence extraction template for included sources. Policy/context sources should be labeled separately from core evidence sources.

Allowed source types: `peer_reviewed_study`, `systematic_review`, `policy_report`, `government_source`, `state_policy_document`, `professional_association_source`, `background_only`.

## `data/outputs/prisma_counts.csv`

PRISMA-style counts derived from the search log, deduplication outputs, human screening file, full-text review file, and evidence table. Also includes `record_volume_flag` and `record_volume_note` as search-quality checks. These flags do not determine final inclusion.
