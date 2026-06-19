# Protocol Draft

## Title

Medicaid Postpartum Coverage & Maternal Health Equity Systematic Review - Portfolio Paper

## Background And Rationale

Postpartum Medicaid coverage policies may affect access to care, continuity of insurance, behavioral health treatment, care coordination, and maternal health equity. Recent state and federal policy changes extending postpartum Medicaid eligibility create a need to synthesize evidence on coverage continuity and outcomes for low-income and medically vulnerable postpartum populations.

## Research Question

How do Medicaid postpartum coverage extensions relate to maternal health access, continuity of care, and health equity for low-income and medically vulnerable postpartum populations?

## Eligibility Criteria

Eligible sources focus on postpartum people covered by Medicaid/CHIP or affected by Medicaid postpartum eligibility or coverage policies in the United States from 2014 through 2026. Eligible policy/intervention topics include Medicaid postpartum coverage extensions, 12-month postpartum coverage, state plan amendments, Section 1115 waivers, eligibility continuity, redetermination, and insurance churn. Eligible outcomes include access to care, postpartum visit completion, continuity of coverage, behavioral health access, maternal morbidity, emergency department use, care coordination, and equity implications.

Sources may include peer-reviewed studies, systematic reviews, policy reports, government sources, state policy documents, and professional association sources. Sources may be excluded for wrong population, wrong policy/intervention, not Medicaid/CHIP, not postpartum, not U.S.-based, no relevant outcome, background-only relevance, opinion without data or policy detail, duplicate status, or other documented reasons.

## Information Sources

Academic records for the final main workflow will be searched in PubMed. Crossref may be used for metadata enrichment. Policy and gray-literature context will be tracked manually from CMS/Medicaid.gov, KFF, MACPAC, NASHP, ACOG, the Commonwealth Fund, and state Medicaid documents. OpenAlex was explored during development but was not retained in the final main workflow because it produced an overly broad result set.

## Search Strategy

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

The synthesis will summarize evidence by policy feature, outcome domain, population, state or national scope, study/report type, and equity relevance. Policy/context sources should be labeled separately from core evidence sources.

## Automation Statement

Automation is used for reproducible searching, metadata cleaning, deduplication, transparent relevance scoring, screening workbook setup, policy-source logging, evidence-table templating, and PRISMA-style count tracking. Automation does not make final include/exclude decisions. `records_marked_ineligible_by_automation` is set to `0` unless the reviewer later approves a specific automated exclusion rule.
