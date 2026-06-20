# Title/Abstract Screening Guide

This guide supports human screening for the portfolio systematic review now titled "State Adoption and Implementation of Twelve-Month Postpartum Medicaid Coverage Extensions After the American Rescue Plan Act: A Systematic Review." PubMed is the only automated academic database source in the main PRISMA workflow, and the final Strategy E search produced 211 records for title/abstract screening.

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

The initial broad title/abstract screen has been completed and should be preserved for transparency. Before full-text review, the scope has been narrowed to focus specifically on post-2021 state adoption and implementation of 12-month postpartum Medicaid coverage extensions.

Second-pass narrowed screening applies only to records with first-pass `human_title_abstract_decision` values of `include_for_full_text` or `maybe`.

### Narrowed Inclusion Criteria

Use `retain_for_full_text` when the title/abstract suggests the record directly addresses most or all of the following:

- Medicaid or CHIP postpartum coverage.
- 12-month postpartum coverage extension, extended postpartum eligibility, continuous postpartum coverage, Section 1115 waiver, state plan amendment, American Rescue Plan Act, or post-2021 state adoption/implementation.
- U.S. state or federal policy context.
- A relevant connection to postpartum access, coverage continuity, insurance churn, redetermination, behavioral health access, postpartum care utilization, equity, disparities, rural access, low-income populations, or medically vulnerable postpartum populations.

### Narrowed Downgrade Or Exclusion Criteria

Use `exclude_after_narrowing` when the record is about general maternal mortality or morbidity but not 12-month postpartum Medicaid coverage extension; postpartum care but not Medicaid/CHIP coverage policy; Medicaid expansion generally but not postpartum extension; broad maternal health legislation where postpartum Medicaid extension is only a minor mention; clinical postpartum outcomes without coverage, eligibility, or policy relevance; pre-2021 context not relevant to later 12-month extension policy; or an opinion piece without useful policy detail or evidence.

Use `background_only` when the record is useful context but does not directly answer the narrowed research question, discusses maternal health policy broadly and mentions postpartum Medicaid extension only briefly, or explains Medicaid, CHIP, maternal mortality, or postpartum care access generally without core evidence on state adoption or implementation.

Use `unsure_second_pass` when the title/abstract is not clear enough to confidently retain, downgrade, or exclude.

Allowed `narrowed_screening_reason` values are:

- `directly_about_12_month_postpartum_medicaid_extension`
- `state_adoption_or_implementation`
- `access_or_continuity_outcome`
- `equity_or_disparity_relevance`
- `broad_maternal_health_policy_only`
- `not_12_month_extension`
- `not_post_2021_relevant`
- `not_medicaid_postpartum_policy`
- `background_context_only`
- `other`
