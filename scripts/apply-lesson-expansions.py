#!/usr/bin/env python3
"""Append focused, idempotent teaching explanations to selected core lessons."""
import json
import difflib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES_PATH = ROOT / "src/data/modules.json"
EXPANSIONS_PATH = ROOT / "src/data/lesson-expansions.json"
modules = json.loads(MODULES_PATH.read_text())
expansions = json.loads(EXPANSIONS_PATH.read_text())

# Reconcile a corrected source attribution before exact-paragraph matching. Without
# this step, an older bundled copy differs only by the bad label and is appended
# again as if it were a new explanation.
def normalize_attribution(value):
    if isinstance(value, str):
        return value.replace(
            "Causal Inference for the Brave and True; MIT",
            "Causal Inference for the Brave and True; open-source handbook",
        )
    if isinstance(value, list):
        return [normalize_attribution(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_attribution(item) for key, item in value.items()}
    return value

modules = normalize_attribution(modules)
by_id = {module["id"]: module for module in modules}

unknown_modules = sorted(set(expansions) - set(by_id))
if unknown_modules:
    raise SystemExit(f"Lesson expansions reference unknown modules: {unknown_modules}")

updated = 0
deduplicated = 0
reconciled_legacy = 0

# These expansion paragraphs are intentionally rewritten by the audit-correction
# pass. Reconcile only these reviewed targets, and only when one old paragraph is
# an unambiguous near-match for the corrected canonical text.
FUZZY_RECONCILIATION_TARGETS = {
    ("bayesian", "Communicate Bayesian evidence responsibly"),
    ("backtesting", "Validate, stress and account for multiplicity"),
    ("kernel-density", "Bandwidth is the main smoothing decision"),
    ("kernel-density", "Kernel regression estimates a local conditional mean"),
    ("kernel-density", "Local polynomials and a careful workflow"),
    ("statistical-tools", "Make a small data dictionary"),
    ("matching-weighting", "Weighting choices define which population the contrast describes"),
    ("synthetic-control", "Use placebos as a reference, not a magic test"),
    ("heterogeneous-effects", "Keep discovery and confirmation distinct"),
    ("multilevel-partial-pooling", "Why a group label can matter"),
    ("spatial-dependence-regional-econometrics", "Spatial lag and spatial error tell different stories"),
    ("causal-mediation-mechanisms", "Use sensitivity analysis and report the limits"),
    ("partial-identification-bounds", "Derive worst-case bounds for missing binary outcomes"),
    ("robust-clustered-inference", "Few clusters need extra care"),
    ("robust-clustered-inference", "Uncertainty follows the data-generating design"),
}


def retain_one_paragraph(body, paragraph, label):
    """Append a missing paragraph or remove exact repeated copies of it."""
    parts = body.split("\n\n") if body else []
    count = sum(part == paragraph for part in parts)
    if count > 1:
        kept = []
        seen = False
        for part in parts:
            if part == paragraph:
                if seen:
                    continue
                seen = True
            kept.append(part)
        if body.count(paragraph) != count:
            raise SystemExit(f"Repeated supplement is not a standalone paragraph at {label}")
        return "\n\n".join(kept).rstrip(), 0, count - 1
    if count == 1 or paragraph in body:
        return body, 0, 0
    return (f"{body.rstrip()}\n\n{paragraph}" if body.strip() else paragraph), 1, 0


def reconcile_corrected_legacy(body, module_id, title, paragraph, label):
    """Replace a stale paragraph before later audit edits can duplicate its correction."""
    old = None
    if (module_id, title) == ("returns-risk", "Compound wealth and annualize with care") and "16.7% per year" in paragraph:
        old = paragraph.replace("16.7% per year", "16.8% per year")
    elif (module_id, title) == ("regression", "Start with a question, units and a fitted line") and "OpenIntro Statistics — Ch. 8: Introduction to Linear Regression" in paragraph:
        old = paragraph.replace(
            "For an introduction to fitting and interpreting a linear regression, see ‘OpenIntro Statistics — Ch. 8: Introduction to Linear Regression’ in the linked sources.",
            "For a fuller treatment, see ‘NIST — Linear Least Squares Regression’ in the linked sources.",
        )
    elif (module_id, title) == ("regression", "Separate mean-response uncertainty from prediction") and "Penn State STAT 501 — Regression Inference and Prediction Intervals (Lesson 7)" in paragraph:
        old = paragraph.replace(
            "‘Penn State STAT 501 — Regression Inference and Prediction Intervals (Lesson 7)’",
            "‘Penn State STAT 501 — Regression’",
        )
    elif (module_id, title) == ("regression", "Validate predictions on data the model did not see") and "For residual diagnostics and validation practice, see ‘NIST — Residual Diagnostics’ in the linked sources." in paragraph:
        old = paragraph.replace(
            "For residual diagnostics and validation practice, see ‘NIST — Residual Diagnostics’ in the linked sources.",
            "For a fuller treatment, see ‘NIST — Linear Least Squares Regression’ in the linked sources.",
        )
    elif (module_id, title) == ("measurement-error-economics", "Classical predictor error can flatten a slope") and "(9/13) × £40 = £27.69, approximately" in paragraph:
        old = paragraph.replace(
            "the expected slope using the noisy hours measure would be (9/13) × £40 = £27.69, approximately.",
            "the expected slope using the noisy hours measure would be about 0.692 × £40 = £27.70.",
        )
    elif module_id == "time-series" and title in {
        "Choose a time scale and avoid spurious patterns",
        "Look for dependence in direction and magnitude",
    } and "NIST — Box-Jenkins Model Identification (ACF and PACF)" in paragraph:
        old = paragraph.replace(
            "NIST — Box-Jenkins Model Identification (ACF and PACF)",
            "NIST — Time Series and Autocorrelation",
        )
    if old is None and (module_id, title) in FUZZY_RECONCILIATION_TARGETS:
        candidates = [
            (difflib.SequenceMatcher(None, paragraph, part).ratio(), part)
            for part in body.split("\n\n")
            if part != paragraph
        ]
        candidates.sort(reverse=True)
        if candidates and candidates[0][0] >= 0.60:
            runner_up = candidates[1][0] if len(candidates) > 1 else 0.0
            if candidates[0][0] - runner_up < 0.15:
                raise SystemExit(f"Ambiguous corrected expansion near-match at {label}")
            old = candidates[0][1]
    if old is None or old == paragraph:
        return body, 0
    parts = body.split("\n\n") if body else []
    stale_count = sum(part == old for part in parts)
    if not stale_count:
        if old in body:
            raise SystemExit(f"Stale corrected paragraph is not standalone at {label}")
        return body, 0
    current_count = sum(part == paragraph for part in parts)
    if current_count:
        parts = [part for part in parts if part != old]
        return "\n\n".join(parts).rstrip(), stale_count
    reconciled = False
    kept = []
    for part in parts:
        if part == old:
            if reconciled:
                continue
            kept.append(paragraph)
            reconciled = True
        else:
            kept.append(part)
    return "\n\n".join(kept).rstrip(), stale_count


for module_id, lesson_additions in expansions.items():
    module = by_id[module_id]
    by_title = {lesson.get("title"): lesson for lesson in module.get("lessons", [])}
    missing_titles = sorted(set(lesson_additions) - set(by_title))
    if missing_titles:
        raise SystemExit(f"{module_id} is missing expanded lesson titles: {missing_titles}")
    for title, paragraphs in lesson_additions.items():
        if not isinstance(paragraphs, list) or not paragraphs:
            raise SystemExit(f"{module_id}/{title} needs at least one explanatory paragraph")
        lesson = by_title[title]
        body = str(lesson.get("body", "")).rstrip()
        for paragraph in paragraphs:
            if not isinstance(paragraph, str) or len(paragraph) < 200:
                raise SystemExit(f"{module_id}/{title} contains a missing or shallow paragraph")
            body, reconciled = reconcile_corrected_legacy(body, module_id, title, paragraph, f"{module_id}/{title}")
            reconciled_legacy += reconciled
            body, added, removed = retain_one_paragraph(body, paragraph, f"{module_id}/{title}")
            updated += added
            deduplicated += removed
        lesson["body"] = body

MODULES_PATH.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n")

# Preserve the same additions in any legacy enriched source that contains a target lesson.
updated_enriched = 0
for module_id, lesson_additions in expansions.items():
    path = ROOT / "src/data/enriched" / f"{module_id}.json"
    if not path.is_file():
        continue
    item = normalize_attribution(json.loads(path.read_text()))
    enriched_by_title = {lesson.get("title"): lesson for lesson in item.get("lessons", [])}
    for title, paragraphs in lesson_additions.items():
        lesson = enriched_by_title.get(title)
        if lesson is None:
            continue
        body = str(lesson.get("body", "")).rstrip()
        for paragraph in paragraphs:
            body, reconciled = reconcile_corrected_legacy(body, module_id, title, paragraph, f"legacy {module_id}/{title}")
            reconciled_legacy += reconciled
            body, _, _ = retain_one_paragraph(body, paragraph, f"legacy {module_id}/{title}")
        lesson["body"] = body
        updated_enriched += 1
    path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n")

print(f"Applied focused explanations to {len(expansions)} core lessons ({updated} new paragraphs; {deduplicated} duplicate paragraphs removed; {reconciled_legacy} stale corrected paragraphs reconciled; {updated_enriched} enriched source lessons aligned).")
