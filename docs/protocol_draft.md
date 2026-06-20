# Protocol Draft

## Title

State Adoption and Implementation of Twelve-Month Postpartum Medicaid Coverage Extensions After the American Rescue Plan Act: A Systematic Review

## Background And Rationale

The American Rescue Plan Act created a pathway for states to extend Medicaid and CHIP postpartum coverage to 12 months. State adoption and implementation of these extensions may affect postpartum access, coverage continuity, insurance churn, behavioral health access, postpartum care utilization, and equity for low-income and medically vulnerable postpartum populations. This portfolio systematic review narrows the original broader screening set to focus specifically on post-2021 state adoption and implementation of 12-month postpartum Medicaid coverage extensions.

## Research Question

How has state adoption of 12-month postpartum Medicaid coverage extensions after 2021 been studied in relation to postpartum access, coverage continuity, and equity?

## Eligibility Criteria

For the narrowed final scope, eligible sources should directly address state adoption or implementation of 12-month postpartum Medicaid or CHIP coverage extensions after 2021. Relevant policy/intervention topics include 12-month postpartum coverage, extended postpartum eligibility, continuous postpartum coverage, Section 1115 waivers, state plan amendments, American Rescue Plan Act implementation, post-2021 state adoption, redetermination, and insurance churn. Eligible outcomes or analytic connections include postpartum access, coverage continuity, insurance churn, redetermination, behavioral health access, postpartum care utilization, equity, disparities, rural access, low-income populations, or medically vulnerable postpartum populations.

Sources may include peer-reviewed studies, systematic reviews, policy reports, government sources, state policy documents, and professional association sources. Sources may be downgraded or excluded in the narrowed second-pass screen if they focus on general maternal mortality or morbidity without 12-month postpartum Medicaid extension policy, postpartum care without Medicaid/CHIP coverage policy, Medicaid expansion generally without postpartum extension, broad maternal health legislation where postpartum Medicaid extension is only a minor mention, clinical postpartum outcomes without coverage or policy relevance, pre-2021 policy context not relevant to later 12-month extension policy, or opinion without useful policy detail or evidence.

## Information Sources

Academic records for the final main workflow were searched in PubMed. Crossref may be used for metadata enrichment. Policy and gray-literature context is tracked manually from CMS/Medicaid.gov, KFF, MACPAC, NASHP, ACOG, the Commonwealth Fund, and state Medicaid documents. OpenAlex was explored during development but was not retained in the final main workflow because it produced an overly broad result set.

## Search Strategy

The final academic database strategy is PubMed Strategy E, with PubMed as the main automated academic database source. OpenAlex was exploratory only and is not part of the final PRISMA workflow.

Primary academic search string:

`(Medicaid[Title/Abstract] OR CHIP[Title/Abstract]) AND (postpartum[Title/Abstract] OR post-partum[Title/Abstract] OR postnatal[Title/Abstract]) AND (coverage[Title/Abstract] OR eligibility[Title/Abstract] OR extension[Title/Abstract] OR "continuous coverage"[Title/Abstract] OR churn[Title/Abstract] OR redetermination[Title/Abstract])`

Policy scan terms:

- Medicaid postpartum coverage extension state plan amendment
- Section 1115 postpartum waiver
- Medicaid postpartum extension tracker
- postpartum Medicaid eligibility maternal health equity
- 12-month postpartum Medicaid coverage maternal health access
- Medicaid postpartum coverage continuity care equity

## Selection Process

All candidate records remain available for human screening. Automated relevance scoring may suggest `likely_include`, `maybe`, or `likely_exclude`, but these suggestions are not formal exclusion decisions. A human reviewer completes title/abstract screening and full-text eligibility review using the manual CSV files.

Initial broad title/abstract screening has been completed for 211 records. Screening results were `include_for_full_text` for 136 records, `maybe` for 30 records, and `exclude` for 45 records. Exclusion reasons were `wrong_policy_or_intervention` (19), `not_medicaid_or_chip` (10), `not_postpartum` (9), `wrong_population` (3), `opinion_without_data_or_policy_detail` (2), `duplicate` (1), and `not_us_based` (1). The original first-pass screening decisions are preserved for transparency.

The 166 records marked `include_for_full_text` or `maybe` are eligible for a second-pass narrowed screen before full-text review. The second-pass screen uses `narrowed_screening_decision`, `narrowed_screening_reason`, and `narrowed_notes` to classify records as `retain_for_full_text`, `background_only`, `exclude_after_narrowing`, or `unsure_second_pass`.

No records were excluded by automation. Final inclusion decisions have not been made because narrowed screening, full-text retrieval, eligibility review, and evidence synthesis have not been completed. The next step is second-pass narrowed screening, followed by full-text retrieval and eligibility review for retained records.

## Record Volume Quality Checks

There is no required number of included studies. Final inclusion depends on eligibility criteria and human screening decisions. Practical targets are used only to assess search calibration:

- Approximately 100-400 initial candidate records before deduplication is a useful target.
- Fewer than 50 PubMed records should be flagged as potentially too narrow.
- More than 750 records should be flagged as potentially too broad.
- A feasible portfolio systematic review often includes approximately 10-25 core evidence sources, plus separately labeled policy/context sources when relevant.
- Records must not be excluded or included merely to hit a target number.

## Data Extraction Plan

Included sources will be extracted into `data/outputs/evidence_table.csv`, including source type, year, state(s), population, policy feature, study design, data source, outcomes, equity focus, key findings, limitations, program evaluation implications, quality/relevance notes, and final synthesis inclusion status.

## Risk Of Bias And Quality Appraisal Placeholder

A formal risk-of-bias or quality-appraisal approach should be selected after the included source types are known. Potential approaches may differ for quantitative studies, qualitative studies, systematic reviews, and policy reports.

## Synthesis Plan

The synthesis will summarize evidence by state adoption or implementation feature, outcome domain, population, state or national scope, study/report type, and equity relevance. Policy/context sources should be labeled separately from core evidence sources.

## Automation Statement

Automation is used for reproducible searching, metadata cleaning, deduplication, transparent relevance scoring, screening workbook setup, policy-source logging, evidence-table templating, and PRISMA-style count tracking. Automation does not make final include/exclude decisions. `records_marked_ineligible_by_automation` is set to `0` unless the reviewer later approves a specific automated exclusion rule.
