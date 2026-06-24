# Narrowed Empirical Screening Rules

This repository now documents a narrowed empirical scoping-review workflow. The initial PubMed title/abstract screen was intentionally broad, but the final evidence map is frozen to peer-reviewed empirical primary studies that directly examine Medicaid, CHIP, or public insurance as a postpartum coverage, eligibility, continuity, access, implementation, reimbursement, or policy mechanism.

## Retain For Full Text

Use `retain_for_full_text` only for peer-reviewed empirical primary studies that use original data or original analysis. Eligible empirical designs include quantitative claims or administrative data studies, survey studies, cohort studies, difference-in-differences or other quasi-experimental designs, interrupted time series, qualitative interview or focus group studies, mixed-methods implementation studies, and cost or economic analyses that use original data or original analytic modeling.

The retained study must directly address Medicaid, CHIP, or public insurance in relation to postpartum coverage continuity, eligibility, access, utilization, implementation, reimbursement, outcomes, or equity.

## Exclude After Narrowing

Use `exclude_after_narrowing` for records that do not meet the narrowed empirical evidence-map scope. Exclusion categories include:

- Policy opinion pieces, commentaries, professional recommendations, position statements, issue briefs, general policy reports, professional association statements, and narrative policy reviews.
- Systematic reviews, scoping reviews, meta-analyses, and other evidence syntheses that do not present primary empirical findings.
- Broad maternal health background articles where Medicaid or postpartum coverage is only a minor contextual mention.
- Records where Medicaid appears only as a payer, claims source, covariate, subgroup, socioeconomic proxy, or sample descriptor rather than the postpartum policy mechanism being studied.
- Studies with data or cohorts entirely before 2015.
- Remaining records outside the frozen final empirical scope.

## Narrowed Exclusion Reasons

Use the most specific reason available:

- `not_empirical_study`: no original empirical data or original analytic modeling.
- `policy_or_commentary_only`: policy opinion, commentary, issue brief, professional statement, recommendation, or narrative policy review.
- `evidence_synthesis_not_primary_study`: systematic review, scoping review, meta-analysis, or other evidence synthesis.
- `medicaid_only_payer_or_data_source_exclude`: Medicaid is only a payer, data source, covariate, subgroup, or descriptor.
- `pre_2015_cohort`: study data or cohort are entirely before 2015.
- `not_medicaid_postpartum_policy`: not about Medicaid, CHIP, or public-insurance postpartum coverage/access policy.
- `outside_final_empirical_scope`: outside the final frozen empirical full-text pool after narrowing.

## Evidence Roles For Retained Studies

Retained studies are assigned one manual `evidence_role`:

- `post_2021_policy_implementation_evidence`: empirical evidence on post-2021 Medicaid/CHIP postpartum coverage extension, FFCRA continuous coverage, unwinding, state adoption, or implementation.
- `pre_2021_baseline_problem_evidence`: empirical pre-2021 evidence documenting the baseline problem, such as postpartum coverage loss, Medicaid churn, uninsurance, care access gaps, or related disparities.
- `service_specific_medicaid_access_policy`: empirical evidence on Medicaid postpartum service coverage, reimbursement, access, or implementation for directly relevant services.

The frozen retained evidence map has 32 records:

- `post_2021_policy_implementation_evidence`: 16
- `pre_2021_baseline_problem_evidence`: 14
- `service_specific_medicaid_access_policy`: 2

The next step is full-text retrieval and eligibility review for these 32 retained empirical records.
