from __future__ import annotations

from collections import Counter
from datetime import datetime
from shutil import copy2

import pandas as pd

from common import DATA, ensure_dirs, normalize_text, read_csv_if_exists, require_columns, write_csv


SCREENING_CSV = DATA / "manual" / "screening_decisions.csv"
REPORT_PATH = DATA / "outputs" / "evidence_role_suggestion_report.md"

SUGGESTION_COLUMNS = [
    "evidence_role_suggested",
    "evidence_role_suggestion_reason",
    "evidence_role_suggestion_confidence",
    "narrowed_screening_decision_suggested",
    "narrowed_screening_reason_suggested",
]

ROLE_OPTIONS = [
    "pre_2021_baseline_problem_evidence",
    "post_2021_policy_implementation_evidence",
    "service_specific_medicaid_access_policy",
    "broad_maternal_health_background_only",
    "medicaid_only_payer_or_data_source_exclude",
]

POST_2021_POLICY_TERMS = [
    "ARPA",
    "American Rescue Plan",
    "American Rescue Plan Act",
    "FFCRA",
    "Families First Coronavirus Response Act",
    "continuous coverage provision",
    "public health emergency",
    "PHE",
    "unwinding",
    "redetermination pause",
    "12-month postpartum Medicaid",
    "one-year postpartum Medicaid",
    "state adoption",
    "implementation of postpartum Medicaid extension",
    "postpartum Medicaid extension",
    "postpartum Medicaid coverage extension",
]

PRE_2021_BASELINE_TERMS = [
    "60-day postpartum coverage",
    "60 days postpartum",
    "coverage cliff",
    "postpartum coverage cliff",
    "pregnancy Medicaid ending after 60 days",
    "Medicaid ending after 60 days",
    "postpartum insurance loss",
    "insurance loss",
    "churn",
    "uninsurance after Medicaid-paid birth",
    "uninsured after 60 days",
    "readmission while uninsured",
    "postpartum care access gaps",
    "coverage gaps",
]

SERVICE_TERMS = [
    "LARC",
    "immediate postpartum contraception",
    "contraception",
    "oral health",
    "dental coverage",
    "lactation support",
    "breastfeeding support",
    "opioid use disorder",
    "substance use treatment",
    "STI services",
    "sexually transmitted infection",
]

CONDITIONAL_BEHAVIORAL_HEALTH_SERVICE_TERMS = [
    "behavioral health",
    "mental health",
]

SERVICE_POLICY_TERMS = [
    "Medicaid coverage",
    "Medicaid reimbursement",
    "billing",
    "payment",
    "benefit",
    "managed care",
    "state plan amendment",
    "coverage extension",
    "extended postpartum coverage",
    "postpartum Medicaid",
    "public insurance policy",
]

BROAD_BACKGROUND_TERMS = [
    "maternal health",
    "postpartum care",
    "hypertension",
    "mental health",
    "mortality",
    "morbidity",
    "health policy",
    "maternal mortality",
    "maternal morbidity",
    "policy article",
]

PAYER_ONLY_TERMS = [
    "payer",
    "claims database",
    "claims data",
    "insurance subgroup",
    "covariate",
    "sample descriptor",
    "socioeconomic proxy",
    "Medicaid-paid",
    "Medicaid payer",
    "Medicaid status",
]

POLICY_MECHANISM_TERMS = [
    "12-month",
    "twelve-month",
    "12 months",
    "one year",
    "postpartum coverage extension",
    "postpartum Medicaid extension",
    "state plan amendment",
    "Section 1115",
    "1115 waiver",
    "waiver",
    "state adoption",
    "implementation",
    "continuous coverage",
    "redetermination",
]

EVIDENCE_SYNTHESIS_TERMS = [
    "systematic review",
    "scoping review",
    "meta analysis",
    "meta-analysis",
    "literature review",
    "integrative review",
    "umbrella review",
    "evidence synthesis",
]

POLICY_COMMENTARY_TERMS = [
    "commentary",
    "editorial",
    "opinion",
    "perspective",
    "viewpoint",
    "issue brief",
    "policy brief",
    "policy review",
    "narrative policy review",
    "position statement",
    "professional recommendation",
    "professional recommendations",
    "professional statement",
    "committee opinion",
    "practice bulletin",
    "clinical guidance",
    "recommendation statement",
]

EMPIRICAL_TERMS = [
    "administrative data",
    "claims",
    "claims data",
    "survey",
    "cohort",
    "regression",
    "difference in differences",
    "difference-in-differences",
    "interrupted time series",
    "quasi experimental",
    "quasi-experimental",
    "interview",
    "interviews",
    "focus group",
    "focus groups",
    "qualitative",
    "mixed methods",
    "mixed-methods",
    "economic analysis",
    "cost analysis",
    "analytic modeling",
    "sample",
    "participants",
    "respondents",
    "we analyzed",
    "we examined",
    "we estimated",
]


def phrase_matches(normalized: str, terms: list[str]) -> list[str]:
    padded = f" {normalized} "
    matches = []
    for term in terms:
        normalized_term = normalize_text(term)
        if normalized_term and f" {normalized_term} " in padded:
            matches.append(term)
    return matches


def year_int(value: object) -> int | None:
    try:
        return int(str(value).strip())
    except ValueError:
        return None


def confidence_from_scores(best_score: int, second_score: int) -> str:
    if best_score >= 5 and best_score >= second_score + 3:
        return "high"
    if best_score >= 3:
        return "medium"
    return "low"


def non_empirical_suggestion(normalized: str) -> tuple[str, list[str]]:
    synthesis_matches = phrase_matches(normalized, EVIDENCE_SYNTHESIS_TERMS)
    if synthesis_matches:
        return "evidence_synthesis_not_primary_study", synthesis_matches

    commentary_matches = phrase_matches(normalized, POLICY_COMMENTARY_TERMS)
    empirical_matches = phrase_matches(normalized, EMPIRICAL_TERMS)
    if commentary_matches and not empirical_matches:
        return "policy_or_commentary_only", commentary_matches

    return "", []


def suggest_role(row: pd.Series) -> dict[str, str]:
    text = " ".join(
        str(row.get(column, ""))
        for column in [
            "title",
            "abstract",
            "narrowed_notes",
            "narrowed_screening_decision",
            "narrowed_screening_reason",
        ]
    )
    normalized = normalize_text(text)
    year = year_int(row.get("publication_year", row.get("year", "")))

    post_matches = phrase_matches(normalized, POST_2021_POLICY_TERMS)
    pre_matches = phrase_matches(normalized, PRE_2021_BASELINE_TERMS)
    service_matches = phrase_matches(normalized, SERVICE_TERMS)
    conditional_behavioral_health_matches = phrase_matches(normalized, CONDITIONAL_BEHAVIORAL_HEALTH_SERVICE_TERMS)
    service_policy_matches = phrase_matches(normalized, SERVICE_POLICY_TERMS)
    broad_matches = phrase_matches(normalized, BROAD_BACKGROUND_TERMS)
    payer_matches = phrase_matches(normalized, PAYER_ONLY_TERMS)
    policy_matches = phrase_matches(normalized, POLICY_MECHANISM_TERMS)
    non_empirical_reason, non_empirical_matches = non_empirical_suggestion(normalized)
    service_specific_matches = service_matches + (conditional_behavioral_health_matches if service_policy_matches else [])
    has_service_specific_policy = bool(service_specific_matches and service_policy_matches)

    scores = {
        "post_2021_policy_implementation_evidence": len(post_matches) * 3 + len(policy_matches),
        "pre_2021_baseline_problem_evidence": len(pre_matches) * 3 + (1 if year and year < 2021 else 0),
        "service_specific_medicaid_access_policy": (
            len(service_specific_matches) * 3 + len(service_policy_matches) * 2 + 3 if has_service_specific_policy else 0
        ),
        "broad_maternal_health_background_only": len(broad_matches) * 2,
        "medicaid_only_payer_or_data_source_exclude": max(len(payer_matches) * 3 - len(policy_matches), 0),
    }
    if year and year >= 2021 and post_matches:
        scores["post_2021_policy_implementation_evidence"] += 2
    if payer_matches and not policy_matches:
        scores["medicaid_only_payer_or_data_source_exclude"] += 2
    if payer_matches and not policy_matches and not has_service_specific_policy:
        scores["medicaid_only_payer_or_data_source_exclude"] += 3
    if broad_matches and not policy_matches and not has_service_specific_policy:
        scores["broad_maternal_health_background_only"] += 2

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    role, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0

    if non_empirical_reason:
        if non_empirical_reason == "evidence_synthesis_not_primary_study":
            role = "broad_maternal_health_background_only"
            confidence = "high"
        elif payer_matches and not policy_matches:
            role = "medicaid_only_payer_or_data_source_exclude"
            confidence = "high"
        else:
            role = "broad_maternal_health_background_only"
            confidence = "high" if non_empirical_matches else "medium"
    elif best_score == 0:
        role = "broad_maternal_health_background_only"
        confidence = "low"
    else:
        confidence = confidence_from_scores(best_score, second_score)

    match_map = {
        "post_2021_policy_implementation_evidence": post_matches + policy_matches,
        "pre_2021_baseline_problem_evidence": pre_matches,
        "service_specific_medicaid_access_policy": service_specific_matches + service_policy_matches,
        "broad_maternal_health_background_only": broad_matches,
        "medicaid_only_payer_or_data_source_exclude": payer_matches,
    }
    matched = match_map.get(role, [])
    if non_empirical_reason:
        reason = (
            f"Suggested exclude_after_narrowing with reason `{non_empirical_reason}` because this appears "
            f"non-empirical. Matched terms: {', '.join(dict.fromkeys(non_empirical_matches))}."
        )
    elif matched:
        reason = f"Matched {role} terms: {', '.join(dict.fromkeys(matched))}."
    else:
        reason = "Only weak or general evidence-role terms were present."

    return {
        "evidence_role_suggested": role,
        "evidence_role_suggestion_reason": reason,
        "evidence_role_suggestion_confidence": confidence,
        "narrowed_screening_decision_suggested": "exclude_after_narrowing" if non_empirical_reason else "",
        "narrowed_screening_reason_suggested": non_empirical_reason,
    }


def backup_screening_csv() -> None:
    backup_dir = DATA / "manual" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    copy2(SCREENING_CSV, backup_dir / f"screening_decisions_before_evidence_role_suggestions_{timestamp}.csv")


def write_report(df: pd.DataFrame) -> None:
    role_counts = df["evidence_role_suggested"].fillna("").replace("", "(blank)").value_counts().to_dict()
    confidence_counts = df["evidence_role_suggestion_confidence"].fillna("").replace("", "(blank)").value_counts().to_dict()
    narrowed_reason_counts = (
        df["narrowed_screening_reason_suggested"].fillna("").replace("", "(blank)").value_counts().to_dict()
    )

    lines = [
        "# Evidence Role Suggestion Report",
        "",
        "These are rule-based suggestions for manual review. They do not overwrite manual `evidence_role`, `narrowed_screening_decision`, `narrowed_screening_reason`, or `narrowed_notes` fields and do not make final inclusion decisions.",
        "",
        "The narrowed workflow retains only peer-reviewed empirical studies. Policy reviews, commentaries, issue briefs, professional statements, and evidence syntheses are suggested for exclusion from the retained empirical evidence map.",
        "",
        f"- Records evaluated: {len(df)}",
        "",
        "## Counts By Suggested Role",
        "",
    ]
    for role in ROLE_OPTIONS:
        lines.append(f"- `{role}`: {role_counts.get(role, 0)}")
    if role_counts.get("(blank)", 0):
        lines.append(f"- `(blank)`: {role_counts.get('(blank)', 0)}")

    lines.extend(["", "## Counts By Confidence", ""])
    for confidence in ["high", "medium", "low", "(blank)"]:
        if confidence in confidence_counts:
            lines.append(f"- `{confidence}`: {confidence_counts[confidence]}")

    lines.extend(["", "## Counts By Suggested Narrowed Exclusion Reason", ""])
    for reason in [
        "not_empirical_study",
        "policy_or_commentary_only",
        "evidence_synthesis_not_primary_study",
        "not_medicaid_postpartum_policy",
        "(blank)",
    ]:
        if reason in narrowed_reason_counts:
            lines.append(f"- `{reason}`: {narrowed_reason_counts[reason]}")

    lines.extend(["", "## Common Suggestion Reasons", ""])
    reason_counter = Counter(df["evidence_role_suggestion_reason"].fillna("").replace("", "(blank)"))
    for reason, count in reason_counter.most_common(20):
        lines.append(f"- {count}: {reason}")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    df = read_csv_if_exists(SCREENING_CSV)
    require_columns(df, ["record_id", "title", "abstract"], str(SCREENING_CSV))

    manual_before = df["evidence_role"].copy() if "evidence_role" in df.columns else None
    manual_narrowed_decision_before = df["narrowed_screening_decision"].copy() if "narrowed_screening_decision" in df.columns else None
    manual_narrowed_reason_before = df["narrowed_screening_reason"].copy() if "narrowed_screening_reason" in df.columns else None
    manual_narrowed_notes_before = df["narrowed_notes"].copy() if "narrowed_notes" in df.columns else None
    for column in SUGGESTION_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    for index, row in df.iterrows():
        suggestion = suggest_role(row)
        for column, value in suggestion.items():
            df.at[index, column] = value

    if manual_before is not None and not df["evidence_role"].equals(manual_before):
        raise RuntimeError("Manual evidence_role values changed unexpectedly.")
    if manual_narrowed_decision_before is not None and not df["narrowed_screening_decision"].equals(manual_narrowed_decision_before):
        raise RuntimeError("Manual narrowed_screening_decision values changed unexpectedly.")
    if manual_narrowed_reason_before is not None and not df["narrowed_screening_reason"].equals(manual_narrowed_reason_before):
        raise RuntimeError("Manual narrowed_screening_reason values changed unexpectedly.")
    if manual_narrowed_notes_before is not None and not df["narrowed_notes"].equals(manual_narrowed_notes_before):
        raise RuntimeError("Manual narrowed_notes values changed unexpectedly.")

    backup_screening_csv()
    write_csv(df, SCREENING_CSV)
    write_report(df)
    print(f"Wrote evidence-role suggestions for {len(df)} records.")
    if manual_before is None:
        print("Manual evidence_role column was not present; no manual values were overwritten.")
    else:
        print("Manual evidence_role column was present and unchanged.")
    print(f"Wrote {REPORT_PATH}.")


if __name__ == "__main__":
    main()
