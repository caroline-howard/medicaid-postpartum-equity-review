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
- `authors`: Author list, when available.
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

Primary human screening file. Automation suggestions are triage aids only and are not final decisions.

### First-Pass Title/Abstract Screening

First-pass screening was intentionally broad and inclusive.

- `record_id`: Stable local record identifier.
- `human_title_abstract_decision`: First-pass human title/abstract decision. Allowed values are `include_for_full_text`, `maybe`, and `exclude`.
- `human_title_abstract_exclusion_reason`: Required only when `human_title_abstract_decision` is `exclude`. Allowed values are `wrong_population`, `wrong_policy_or_intervention`, `not_medicaid_or_chip`, `not_postpartum`, `not_us_based`, `no_relevant_outcome`, `background_only`, `opinion_without_data_or_policy_detail`, `duplicate`, and `other`.
- `notes`: Optional first-pass reviewer notes.

### Legacy/Triage Fields

These columns may remain in the CSV for transparency and auditability. They are not final inclusion logic.

- `timeline_scope_score`: Rule-based automation score used to prioritize review.
- `timeline_scope_tier`: Rule-based triage tier.
- `timeline_scope_matched_terms`: Matched triage terms grouped by concept.
- `automation_narrowing_suggestion`: Automation suggestion for prioritization only.
- `automation_narrowing_note`: Short explanation of the automated triage tier.
- `evidence_role_suggested`: Rule-based suggested evidence role.
- `evidence_role_suggestion_confidence`: Rule-based confidence label for the suggested evidence role.
- `evidence_role_suggestion_reason`: Matched terms or rationale behind the suggested role.
- `narrowed_screening_decision_suggested`: Automation-suggested narrowed action, used only as guidance.
- `narrowed_screening_reason_suggested`: Automation-suggested narrowed reason, used only as guidance.

### Final Narrowed Empirical Screening Fields

These fields document the final empirical scoping-review evidence map.

- `narrowed_screening_decision`: Final narrowed decision. The final retained pool uses `retain_for_full_text`; exclusions use `exclude_after_narrowing`. Historical allowed values may also include `background_only` and `unsure_second_pass`, but those are not retained evidence-map categories.
- `narrowed_screening_reason`: Human reason for the narrowed decision. Final exclusion reasons include `not_empirical_study`, `policy_or_commentary_only`, `evidence_synthesis_not_primary_study`, `not_medicaid_postpartum_policy`, `pre_2015_cohort`, and `outside_final_empirical_scope`. Historical/triage reasons may remain in older rows, including `directly_about_12_month_postpartum_medicaid_extension`, `state_adoption_or_implementation`, `access_or_continuity_outcome`, `equity_or_disparity_relevance`, `broad_maternal_health_policy_only`, `not_12_month_extension`, `not_post_2021_relevant`, `background_context_only`, and `other`.
- `narrowed_notes`: Free-text notes for narrowed empirical screening.
- `evidence_role`: Manual evidence role for records retained for full-text review. Final retained roles are `post_2021_policy_implementation_evidence`, `pre_2021_baseline_problem_evidence`, and `service_specific_medicaid_access_policy`.

## `data/manual/full_text_review.csv`

Human full-text review file. The current full-text pool should be limited to the 32 records marked `retain_for_full_text` after narrowed empirical screening. Historical full-text decision categories may exist in the template, but the final empirical evidence synthesis should include only peer-reviewed empirical primary studies that pass full-text eligibility review.

## `data/manual/synthesis_manual_classification.csv`

Manual synthesis-planning classification file for the 28 studies included after full-text review. This file is the source of truth for synthesis planning classifications, but it is not a screening decision file, evidence extraction output, or PRISMA count input.

- `record_id`: Stable local record identifier.
- `manual_policy_period_group`: Manual policy-period classification. Allowed values are `pre_policy_baseline_before_ffcra_or_extension`, `post_ffcra_continuous_eligibility_period`, `post_12_month_postpartum_extension_period`, `multiple_policy_eras`, and `unsure_manual_review`.
- `manual_policy_eras_included`: Free-text note describing which policy eras are included, especially for `multiple_policy_eras`.
- `manual_scope_type`: Manual scope classification. Allowed values are `national`, `multi_state`, `single_state`, and `not_clearly_specified`.
- `manual_synthesis_notes`: Free-text reviewer notes explaining classification decisions.

If `multiple_policy_era_type` appears in generated output files, it is a derived planning field based on `manual_policy_eras_included`. It is not a manual screening decision.

## `data/outputs/narrowed_empirical_retained_records.csv`

Export of the 32 records retained for full-text review after narrowed empirical screening. Key fields include `record_id`, bibliographic identifiers, first-pass decision, narrowed decision, narrowed reason, narrowed notes, manual `evidence_role`, suggested role fields, triage tier, and relevance score.

## `data/outputs/evidence_table.csv`

Evidence extraction template for empirical studies that pass full-text eligibility review. Historical source-type fields may exist in the template, but the final evidence map should use peer-reviewed empirical primary studies only. Evidence extraction has not yet been completed.

## Manual Synthesis-Planning Export Files

These files are generated from `data/manual/synthesis_manual_classification.csv` only. They are not evidence extraction outputs and are not PRISMA screening outputs.

- `data/outputs/manual_pre_policy_baseline_before_ffcra_or_extension_studies.csv`: manually classified pre-policy baseline studies.
- `data/outputs/manual_post_ffcra_continuous_eligibility_period_studies.csv`: manually classified FFCRA/COVID public health emergency continuous eligibility period studies.
- `data/outputs/manual_post_12_month_postpartum_extension_period_studies.csv`: manually classified formal 12-month postpartum extension period studies.
- `data/outputs/manual_multiple_policy_eras_studies.csv`: manually classified studies spanning multiple relevant policy eras.
- `data/outputs/manual_unsure_review_studies.csv`: manually classified studies needing policy-period review.
- `data/outputs/manual_national_studies.csv`: manually classified national-scope studies.
- `data/outputs/manual_multi_state_studies.csv`: manually classified multi-state studies.
- `data/outputs/manual_single_state_studies.csv`: manually classified single-state studies.
- `data/outputs/manual_not_clearly_specified_scope_studies.csv`: manually classified studies with unclear scope.
- `data/outputs/manual_synthesis_classification_summary.csv`: cross-tabulated manual classification summary by policy period and scope, plus derived multiple-policy-era planning counts where present.
- `docs/manual_synthesis_classification_summary.md`: human-readable manual classification summary. This documentation is a synthesis-planning aid only; evidence extraction has not yet been completed.

## `data/outputs/prisma_counts.csv`

PRISMA-style counts derived from the PubMed-only search log, deduplication outputs, human screening file, full-text review file, and evidence table. Also includes `record_volume_flag` and `record_volume_note` as search-quality checks. These flags do not determine final inclusion.
