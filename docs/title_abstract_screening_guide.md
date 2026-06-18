# Title/Abstract Screening Guide

## Automation Tiers

- `tier_1_likely_include`: Contains all core concepts. Screen these first.
- `tier_2_maybe`: Contains Medicaid/CHIP and postpartum/pregnancy concepts but is missing one adjacent concept. Screen these after tier 1.
- `tier_3_likely_exclude`: Missing multiple core concepts. Check quickly if time allows.
- `tier_4_obvious_exclude`: Clear automation exclusion candidate.

## What `automation_exclude` Means

`automation_exclude` means the rule-based script found that the record clearly lacked one or more required core concepts. It is not a human screening decision. These records are counted separately as `records_marked_ineligible_by_automation` in PRISMA counts.

## Screening Order

Start with `tier_1_likely_include`, then `tier_2_maybe`. If time allows, skim `tier_3_likely_exclude` for any record that should be rescued. Do not treat tier 3 as automatically excluded.

## Validation Sample

Review `data/manual/automation_exclusion_validation_sample.csv`. For each sampled record, set `human_validation_decision` to:

- `confirm_exclude`
- `rescue_for_manual_screening`
- `unsure`

Use `human_validation_notes` to document why the automation was correct or wrong.

## Rescuing A Record

If an `automation_exclude` record appears relevant, change `human_title_abstract_decision` in `data/manual/screening_decisions.csv` from `automation_exclude` to `maybe` or `include_for_full_text`, clear or revise the exclusion reason, and note that the record was rescued during validation. Then rerun `scripts/07_build_prisma_counts.py`.
