# Protocol Draft

## Title

Medicaid/CHIP Postpartum Coverage, Continuity, Implementation, Access, and Equity: A Narrowed Empirical Scoping Review

## Background And Rationale

Medicaid and CHIP are central sources of pregnancy and postpartum coverage in the United States. Postpartum coverage policy, eligibility rules, continuity of enrollment, reimbursement, and implementation choices may affect access to care, service use, care continuity, and equity for low-income and medically vulnerable postpartum populations.

This portfolio project began with a broad PubMed title/abstract screen on Medicaid/CHIP postpartum coverage and related maternal health access topics. After broad first-pass screening, the review was narrowed to an empirical scoping-review evidence map. The final evidence map retains only peer-reviewed empirical primary studies where Medicaid, CHIP, or public insurance is the postpartum coverage, eligibility, continuity, access, implementation, reimbursement, or policy mechanism being studied.

## Research Question

What peer-reviewed empirical evidence examines Medicaid, CHIP, or public insurance as a postpartum coverage, eligibility, continuity, access, implementation, reimbursement, or policy mechanism, and how does that evidence relate to postpartum access, utilization, care continuity, outcomes, or equity?

## Eligibility Criteria

For the final narrowed evidence map, retained records must be peer-reviewed empirical primary studies using original data or original analysis. Eligible designs include quantitative claims or administrative data studies, survey studies, cohort studies, quasi-experimental designs, interrupted time series, qualitative interview or focus group studies, mixed-methods implementation studies, and cost or economic analyses that use original data or analytic modeling.

Eligible retained studies must directly address Medicaid, CHIP, or public insurance in relation to postpartum coverage, eligibility, continuity, access, implementation, reimbursement, utilization, outcomes, or equity.

Records are excluded after narrowing if they are policy opinion pieces, commentaries, professional recommendations, position statements, issue briefs, narrative policy reviews, systematic reviews, scoping reviews, meta-analyses, broad maternal health background articles with only minor Medicaid/postpartum coverage relevance, Medicaid-only payer/data-source/covariate records, or studies with data or cohorts entirely before 2015.

## Information Sources

The final automated academic database search used PubMed Strategy E and identified 211 records. Crossref may be used only for metadata enrichment. OpenAlex was explored during development but is not part of the final PRISMA workflow because it returned an overly broad result set.

Policy and gray-literature sources may remain in repository logs as contextual development artifacts, but they are not retained evidence sources in the final empirical evidence map.

## Search Strategy

Primary academic search string:

`(Medicaid[Title/Abstract] OR CHIP[Title/Abstract]) AND (postpartum[Title/Abstract] OR post-partum[Title/Abstract] OR postnatal[Title/Abstract]) AND (coverage[Title/Abstract] OR eligibility[Title/Abstract] OR extension[Title/Abstract] OR "continuous coverage"[Title/Abstract] OR churn[Title/Abstract] OR redetermination[Title/Abstract])`

## Selection Process

All candidate records remained available for human screening. Automated relevance scoring, timeline/scope triage, and evidence-role suggestions were used only to prioritize and audit screening. Automation did not make final include/exclude decisions, and `records_marked_ineligible_by_automation` remains `0`.

First-pass title/abstract screening was broad and inclusive. PubMed Strategy E identified 211 records. First-pass screening results were:

- `include_for_full_text`: 136
- `maybe`: 30
- `exclude`: 45

The 166 records marked `include_for_full_text` or `maybe` were then reviewed in a narrowed empirical second-pass screen. The final retained full-text pool is frozen at 32 peer-reviewed empirical primary studies:

- `post_2021_policy_implementation_evidence`: 16
- `pre_2021_baseline_problem_evidence`: 14
- `service_specific_medicaid_access_policy`: 2

The next step is full-text retrieval and eligibility review for these 32 records. Final synthesis conclusions have not yet been made.

## Record Volume Quality Checks

There is no required number of retained studies. Final inclusion depends on the eligibility criteria, full-text review, and documented human decisions. Practical search-volume targets were used only to assess search calibration:

- Approximately 100-400 initial PubMed candidate records before deduplication is a useful target.
- Fewer than 50 PubMed records should be flagged as potentially too narrow.
- More than 750 PubMed records should be flagged as potentially too broad.
- Records must not be excluded or included merely to hit a target number.

## Data Extraction Plan

The 32 retained records will be assessed at full text. Eligible empirical studies will be extracted into `data/outputs/evidence_table.csv`, including year, population, policy mechanism, study design, data source, outcomes, equity focus, key findings, limitations, and final synthesis inclusion status.

## Quality Appraisal Placeholder

A formal quality-appraisal approach should be selected after full-text eligibility review confirms the final empirical study designs represented in the retained pool.

## Synthesis Plan

The synthesis will summarize peer-reviewed empirical evidence by evidence role, postpartum coverage/access mechanism, population, study design, data source, outcome domain, and equity relevance.

## Automation Statement

Automation is used for reproducible searching, metadata cleaning, deduplication, transparent relevance scoring, screening workbook/app setup, triage suggestions, and PRISMA-style count tracking. Automation does not make final include/exclude decisions.
