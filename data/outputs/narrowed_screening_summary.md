# Narrowed Screening Summary

The systematic review scope was narrowed before full-text review.

Old broad topic: Medicaid postpartum coverage extensions, maternal health access, continuity of care, and health equity.

New final scope: state adoption and implementation of 12-month postpartum Medicaid coverage extensions after the American Rescue Plan Act.

New research question: How has state adoption of 12-month postpartum Medicaid coverage extensions after 2021 been studied in relation to postpartum access, coverage continuity, and equity?

## Initial Broad Screening Status

- Total records screened in first-pass title/abstract screening: 211
- `include_for_full_text`: 136
- `maybe`: 30
- `exclude`: 45
- Records eligible for narrowed second-pass screening: 166

The original first-pass screening decisions are preserved in `data/manual/screening_decisions.csv`.

## Narrowed Second-Pass Screening Status

Narrowed second-pass screening has not been completed yet. The new columns `narrowed_screening_decision`, `narrowed_screening_reason`, and `narrowed_notes` have been added to `data/manual/screening_decisions.csv`.

Current narrowed decision counts:

- `retain_for_full_text`: 0
- `background_only`: 0
- `exclude_after_narrowing`: 0
- `unsure_second_pass`: 0
- blank/not yet screened: 166

Reasons by category will be summarized after narrowed screening is completed.

Number moving to full-text review after narrowing: not yet determined.

No records were excluded by automation.

## Next Step

Run the narrowed second-pass screening app and review the 166 first-pass `include_for_full_text` or `maybe` records:

```bash
streamlit run scripts/11_narrowed_screening_app.py
```

After narrowed screening is complete, `data/manual/full_text_review.csv` should be filtered to records marked `retain_for_full_text`.
