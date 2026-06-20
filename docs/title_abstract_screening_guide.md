# Title/Abstract Screening Guide

This guide supports human screening for the Medicaid Postpartum Coverage & Maternal Health Equity Systematic Review. PubMed is the only automated academic database source in the main PRISMA workflow, and the final Strategy E search produced 211 records for title/abstract screening.

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
