# Protocol Draft

## Title

Medicaid Postpartum Coverage, Care Continuity, Implementation, Access, And Maternal Health Equity: A Narrowed Empirical Scoping Review

## Background And Rationale

Medicaid and CHIP are central sources of coverage for pregnancy and postpartum care in the United States. Policy changes after the American Rescue Plan Act expanded state options for 12-month postpartum coverage, while earlier research documented postpartum insurance loss, churn, access gaps, and inequities after Medicaid-paid births. This portfolio review uses a reproducible search and screening workflow to map peer-reviewed empirical evidence on Medicaid/CHIP postpartum coverage, continuity, implementation, access, utilization, outcomes, and equity.

## Research Question

What peer-reviewed empirical evidence examines Medicaid, CHIP, or public insurance as a postpartum coverage, eligibility, continuity, access, implementation, reimbursement, or policy mechanism, and how does that evidence inform postpartum maternal health access and equity?

## Eligibility Criteria

The final evidence map retains peer-reviewed empirical primary studies or rigorous original analyses. Medicaid, CHIP, or public insurance must be the postpartum coverage, eligibility, continuity, access, implementation, reimbursement, or policy mechanism rather than only a payer, claims source, covariate, subgroup, or sample descriptor.

Eligible evidence may include quantitative claims or administrative data studies, survey studies, cohort studies, quasi-experimental studies, qualitative interview or focus group studies, mixed-methods implementation studies, and cost or economic analyses that use original data or original analytic modeling and directly address Medicaid postpartum coverage or access policy.

The narrowed empirical workflow excludes policy opinion pieces, commentaries, professional statements, issue briefs, narrative policy reviews, broad maternal health background articles with only a brief Medicaid mention, systematic reviews, scoping reviews, meta-analyses, records where Medicaid is only a payer/data source, and studies whose data or cohorts are entirely before 2015.

## Information Sources

Academic records for the final main workflow were searched in PubMed using Strategy E. Crossref may be used for metadata enrichment. Policy and gray-literature sources may be tracked manually for context, but they are not part of the final retained empirical evidence map. OpenAlex was explored during development but was not retained in the final main workflow because it produced an overly broad result set and is excluded from PRISMA and methods counts.

## Search Strategy

The final automated academic database strategy is PubMed Strategy E:

`(Medicaid[Title/Abstract] OR CHIP[Title/Abstract]) AND (postpartum[Title/Abstract] OR post-partum[Title/Abstract] OR postnatal[Title/Abstract]) AND (coverage[Title/Abstract] OR eligibility[Title/Abstract] OR extension[Title/Abstract] OR "continuous coverage"[Title/Abstract] OR churn[Title/Abstract] OR redetermination[Title/Abstract])`

PubMed Strategy E identified 211 records. After deduplication, 211 records remained for screening.

## Selection Process

All candidate records remained available for human review. Automation supported metadata cleaning, transparent relevance scoring, and triage only. No records were excluded by automation, and `records_marked_ineligible_by_automation` remains `0`.

First-pass title/abstract screening was broad and inclusive. A human reviewer screened 211 PubMed records, marking 136 as `include_for_full_text`, 30 as `maybe`, and 45 as `exclude`. The 166 records marked `include_for_full_text` or `maybe` were then reviewed through a narrowed empirical second-pass workflow.

The narrowed empirical screen retained 32 records for full-text review. Full-text review has been completed for all 32 records. Final full-text decisions were manual:

- Full-text records assessed: 32
- Included core empirical evidence: 28
- Excluded after full text: 4
- Blank full-text decisions remaining: 0

Included evidence roles among the 28 final empirical studies:

- `post_2021_policy_implementation_evidence`: 14
- `pre_2021_baseline_problem_evidence`: 13
- `service_specific_medicaid_access_policy`: 1

Full-text exclusion reasons:

- `unable_to_access_full_text`: 3
- `medicaid_only_payer_or_data_source`: 1

The final included-study table has been generated at `data/outputs/final_evidence_table.csv`. This table documents included studies after full-text eligibility review; it is not a completed evidence extraction or synthesis product.

## Record Volume Quality Checks

There is no required number of included studies. Final inclusion depends on eligibility criteria and documented human screening decisions. Practical targets are used only to assess search calibration:

- Approximately 100-400 initial candidate records before deduplication is a useful target.
- Fewer than 50 PubMed records should be flagged as potentially too narrow.
- More than 750 records should be flagged as potentially too broad.
- Records must not be excluded or included merely to hit a target number.

## Data Extraction

Evidence extraction has not yet been completed. The next step is to extract structured study details from the 28 included full-text studies, including study design, data years, data source, state or scope, population, Medicaid policy mechanism, outcomes, equity focus, main findings, limitations, and notes.

## Risk Of Bias And Quality Appraisal Placeholder

A formal risk-of-bias or quality-appraisal approach should be selected before drafting the final evidence synthesis. This task has not yet been completed in the repository.

## Synthesis Plan

Evidence synthesis has not yet been drafted. Before evidence extraction, included studies were manually classified for synthesis planning by policy period and scope. This classification helps determine how the evidence should be organized later, but it is not an evidence synthesis and does not change inclusion decisions.

### Manual Synthesis-Planning Classification

Manual synthesis-planning classification occurs after full-text review and before evidence extraction. This step has been completed for all 28 included studies. It distinguishes pre-FFCRA/pre-extension baseline evidence, FFCRA/COVID continuous eligibility evidence, formal 12-month postpartum extension evidence, and multiple-era studies. It also distinguishes national, multi-state, single-state, and unclear scope.

This step prevents imprecise writing where all "postpolicy" evidence is treated as the same. It will guide extraction by policy period and scope, but it does not alter PRISMA counts, included-study totals, narrowed screening decisions, or full-text decisions.

## Automation Statement

Automation was used for reproducible searching, metadata cleaning, deduplication, transparent relevance scoring, screening workbook setup, triage, evidence-table preparation, validation, and PRISMA-style count tracking. Automation did not make final title/abstract or full-text include/exclude decisions.
