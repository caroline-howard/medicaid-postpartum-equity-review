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

- `medicaid_chip_hits`: Number of matched Medicaid/CHIP terms in the normalized title and abstract.
- `postpartum_hits`: Number of matched postpartum, pregnancy, or maternal terms in the normalized title and abstract.
- `coverage_policy_hits`: Number of matched coverage, eligibility, extension, churn, waiver, state plan, or related policy terms in the normalized title and abstract.
- `outcomes_hits`: Number of matched access, continuity, behavioral health, morbidity, mortality, equity, disparities, utilization, or care coordination terms in the normalized title and abstract.
- `us_state_policy_hits`: Number of matched United States, state, federal, CMS, county, or Medicaid agency context terms in the normalized title and abstract.
- `relevance_score`: Sum of capped group points from the five keyword groups. Each group contributes `min(hits, 3)` points, so the maximum possible score is 15.
- `automation_suggestion`: Triage label based only on `relevance_score`: `likely_include` for scores of 8 or higher, `maybe` for scores from 4 to 7, and `likely_exclude` for scores below 4. This is not a screening decision.

The exact scoring terms and implementation are documented in `paper/methods_search_appendix.md` and implemented in `scripts/05_score_relevance.py`.

## `data/manual/screening_decisions.csv`

Human title/abstract screening file. Automation suggestions are triage aids only.

Allowed title/abstract decisions: `include_for_full_text`, `maybe`, `exclude`.

Allowed exclusion reasons: `wrong_population`, `wrong_policy_or_intervention`, `not_medicaid_or_chip`, `not_postpartum`, `not_us_based`, `no_relevant_outcome`, `background_only`, `opinion_without_data_or_policy_detail`, `duplicate`, `other`.

Narrowed second-pass screening columns preserve the original title/abstract decisions while allowing the review scope to be narrowed before full-text review:

- `timeline_scope_score`: Rule-based automation score used to prioritize second-pass screening; populated only for first-pass `include_for_full_text` and `maybe` records.
- `timeline_scope_tier`: Rule-based triage tier: `tier_1_strong_match`, `tier_2_possible_match`, `tier_3_background_context`, or `tier_4_likely_out_of_scope`.
- `timeline_scope_matched_terms`: Matched timeline/scope terms grouped by concept so the score can be audited.
- `automation_narrowing_suggestion`: Automation suggestion for prioritization only: `prioritize_for_human_review`, `possible_retain`, `likely_background_only`, or `likely_exclude_after_narrowing`.
- `automation_narrowing_note`: Short explanation of the automated triage tier.
- `narrowed_screening_decision`: Allowed values are `retain_for_full_text`, `background_only`, `exclude_after_narrowing`, and `unsure_second_pass`.
- `narrowed_screening_reason`: Allowed values are `directly_about_12_month_postpartum_medicaid_extension`, `state_adoption_or_implementation`, `access_or_continuity_outcome`, `equity_or_disparity_relevance`, `broad_maternal_health_policy_only`, `not_12_month_extension`, `not_post_2021_relevant`, `not_medicaid_postpartum_policy`, `background_context_only`, and `other`.
- `narrowed_notes`: Free-text notes for second-pass screening.

## `data/manual/full_text_review.csv`

Human full-text review file.

Allowed full-text decisions: `include_core_evidence`, `include_policy_context`, `background_only`, `exclude`.

Before narrowed screening is complete, this file may retain the broader record structure. After narrowed screening is complete, it should be filtered to records marked `retain_for_full_text`.

## `data/outputs/evidence_table.csv`

Evidence extraction template for included sources. Policy/context sources should be labeled separately from core evidence sources.

Allowed source types: `peer_reviewed_study`, `systematic_review`, `policy_report`, `government_source`, `state_policy_document`, `professional_association_source`, `background_only`.

## `data/outputs/prisma_counts.csv`

PRISMA-style counts derived from the search log, deduplication outputs, human screening file, full-text review file, and evidence table. Also includes `record_volume_flag` and `record_volume_note` as search-quality checks. These flags do not determine final inclusion.
