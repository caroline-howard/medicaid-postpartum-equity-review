# Title/Abstract Screening Guide

This guide supports human screening for the narrowed empirical scoping review of Medicaid/CHIP postpartum coverage, continuity, implementation, access, and equity evidence. PubMed is the only automated academic database source in the main PRISMA workflow, and the final Strategy E search produced 211 records for title/abstract screening.

Do not make inclusion or exclusion decisions to reach a target number of studies. Final inclusion depends on the documented screening and full-text eligibility process.

## Decision Rules

### include_for_full_text

Use `include_for_full_text` when the title/abstract suggests the record may address Medicaid/CHIP, postpartum or postnatal care, coverage/eligibility/extension/continuity/churn/redetermination, and at least one relevant access, care continuity, utilization, behavioral health, morbidity, or equity outcome.

### maybe

Use `maybe` when the record might fit but the title/abstract is unclear.

### exclude

Use `exclude` when the record clearly fails the review scope. Every `exclude` decision must have a `human_title_abstract_exclusion_reason`.

Valid exclusion reasons are:

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

## Recommended Screening Order

Screen highest `relevance_score` records first. Use `include_for_full_text` when the record is clearly relevant, use `maybe` when uncertain, and use `exclude` only when the reason is clear.

After high-score records, screen the remaining records quickly for obvious exclusions or hidden relevant papers.

## Narrowed Second-Pass Screening

The initial broad title/abstract screen has been completed and should be preserved for transparency. The project has now been narrowed to an empirical scoping-review evidence map. Final narrowed screening rules are documented in `docs/narrowed_empirical_screening_rules.md`.

The narrowed empirical workflow retains only peer-reviewed empirical primary studies where Medicaid, CHIP, or public insurance is the postpartum coverage, eligibility, continuity, access, implementation, reimbursement, or policy mechanism. Policy commentaries, issue briefs, professional statements, narrative reviews, evidence syntheses, broad maternal health background articles, Medicaid-only payer/data-source records, and entirely pre-2015 cohorts are excluded after narrowing.

Narrowed empirical screening is complete. Thirty-two records are retained for full-text review:

- `post_2021_policy_implementation_evidence`: 16
- `pre_2021_baseline_problem_evidence`: 14
- `service_specific_medicaid_access_policy`: 2

Automation-assisted fields remain guidance only. Manual narrowed decisions are stored in `narrowed_screening_decision`, `narrowed_screening_reason`, `narrowed_notes`, and `evidence_role`.

Final narrowed exclusion reasons include:

- `pre_2015_cohort`
- `not_medicaid_postpartum_policy`
- `outside_final_empirical_scope`
- `not_empirical_study`
- `policy_or_commentary_only`
- `evidence_synthesis_not_primary_study`

Historical or triage-oriented reason values may remain in the CSV for transparency, but they are not the final narrowed empirical inclusion logic.
