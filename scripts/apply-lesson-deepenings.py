#!/usr/bin/env python3
"""Append the second, lesson-specific teaching deepening to every existing lesson."""
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES_PATH = ROOT / "src/data/modules.json"
DEEPENINGS_PATH = ROOT / "src/data/lesson-deepenings.json"
modules = json.loads(MODULES_PATH.read_text())
deepenings = json.loads(DEEPENINGS_PATH.read_text())

lesson_count = sum(len(module.get("lessons", [])) for module in modules)
if len(modules) != 42 or lesson_count != 238:
    raise SystemExit(f"Expected the fixed 42-module/238-lesson curriculum; found {len(modules)} modules and {lesson_count} lessons")

by_id = {module["id"]: module for module in modules}
if len(by_id) != len(modules):
    raise SystemExit("Module IDs must remain unique")
unknown_modules = sorted(set(deepenings) - set(by_id))
missing_modules = sorted(set(by_id) - set(deepenings))
if unknown_modules or missing_modules:
    raise SystemExit(f"Module coverage mismatch; unknown={unknown_modules}, missing={missing_modules}")

seen_paragraphs = set()
updated = 0
replaced_legacy = 0

OLD_MEDIAN_SENTENCE = "In both settings, the median remains −0.4 pp:"
NEW_MEDIAN_SENTENCE = "In both settings, the median remains −0.30 pp (the average of −0.4 and −0.2 pp):"
OLD_EDA_SENTENCE = "First validate the key (fund, month): these three observed values are not four observations, and the blank is not 0%."
NEW_EDA_SENTENCE = "First validate the key (fund, month): there are four intended fund-month keys but only three observed return values; Fund B’s February return is missing, not 0%."
OLD_RESEARCH_DESIGN_SENTENCE = "A randomized offer could make selection independent in expectation, whereas voluntary take-up still requires assumptions about who complies and whose outcome is measured."
NEW_RESEARCH_DESIGN_SENTENCE = "Random assignment makes the offer independent of potential outcomes in expectation, so the intention-to-treat effect is identified under suitable follow-up and measurement conditions. Actual take-up can remain selective; an effect of participation therefore needs additional instrumental-variable assumptions and is generally interpreted for compliers."
LEGACY_SENTENCE_PATCHES = {
    ("statistical-thinking", "Compare center and spread with a worked example"): [(OLD_MEDIAN_SENTENCE, NEW_MEDIAN_SENTENCE)],
    ("exploratory-data-analysis", "Ask what one row represents"): [(OLD_EDA_SENTENCE, NEW_EDA_SENTENCE)],
    ("research-design", "Write down the question before the model"): [(OLD_RESEARCH_DESIGN_SENTENCE, NEW_RESEARCH_DESIGN_SENTENCE)],
    ("spatial-dependence-regional-econometrics", "Spatial lag and spatial error tell different stories"): [
        ("The resulting spatial lags are (−0.5, 0, 0, 0.5).", "The resulting spatial lags are (−0.5, −0.25, 0.25, 0.5)."),
        ("the numerator is Σzᵢ(Wz)ᵢ = (−1)(−0.5) + (−0.5)(0) + (0.5)(0) + (1)(0.5) = 1.", "the numerator is Σzᵢ(Wz)ᵢ = (−1)(−0.5) + (−0.5)(−0.25) + (0.5)(0.25) + (1)(0.5) = 1.25."),
        ("the Moran-style ratio is 1/2.5 = 0.40.", "the Moran-style ratio is 1.25/2.5 = 0.50."),
    ],
}


def replace_legacy_deepening(body, module_id, title, paragraph):
    """Reconcile earlier copies before appending the audited deepening."""
    patch = LEGACY_SENTENCE_PATCHES.get((module_id, title))
    if patch is None:
        return body, 0
    legacy = paragraph
    for old_sentence, new_sentence in patch:
        if new_sentence not in paragraph:
            raise SystemExit(f"The corrected deepening is missing its verified sentence for {module_id}/{title}")
        legacy = legacy.replace(new_sentence, old_sentence)
    parts = body.split("\n\n") if body else []
    legacy_count = sum(part == legacy for part in parts)
    if not legacy_count:
        return body, 0
    if any(part == paragraph for part in parts):
        parts = [part for part in parts if part != legacy]
        return "\n\n".join(parts), legacy_count
    replaced = False
    kept = []
    for part in parts:
        if part == legacy:
            if replaced:
                continue
            kept.append(paragraph)
            replaced = True
        else:
            kept.append(part)
    return "\n\n".join(kept), legacy_count


for module_id, lesson_additions in deepenings.items():
    module = by_id[module_id]
    by_title = {lesson.get("title"): lesson for lesson in module.get("lessons", [])}
    if len(by_title) != len(module.get("lessons", [])):
        raise SystemExit(f"{module_id} has duplicate lesson titles")
    if set(lesson_additions) != set(by_title):
        missing = sorted(set(by_title) - set(lesson_additions))
        extra = sorted(set(lesson_additions) - set(by_title))
        raise SystemExit(f"{module_id} lesson coverage mismatch; missing={missing}, extra={extra}")

    for title, paragraph in lesson_additions.items():
        if not isinstance(paragraph, str) or len(paragraph) < 850:
            raise SystemExit(f"{module_id}/{title} has a missing or shallow deepening")
        words = len(paragraph.split())
        if not 140 <= words <= 210 or "\n" in paragraph.strip():
            raise SystemExit(f"{module_id}/{title} has an unexpected length/format ({words} whitespace-delimited words)")
        normalized = " ".join(unicodedata.normalize("NFKC", paragraph).casefold().split())
        if normalized in seen_paragraphs:
            raise SystemExit(f"Duplicate lesson deepening detected at {module_id}/{title}")
        seen_paragraphs.add(normalized)

        lesson = by_title[title]
        body = str(lesson.get("body", ""))
        body, legacy_updates = replace_legacy_deepening(body, module_id, title, paragraph)
        replaced_legacy += legacy_updates
        occurrences = body.count(paragraph)
        if occurrences > 1:
            raise SystemExit(f"{module_id}/{title} already contains a duplicated deepening")
        if occurrences == 0:
            body = f"{body.rstrip()}\n\n{paragraph}" if body.strip() else paragraph
            updated += 1
        lesson["body"] = body

if len(seen_paragraphs) != 238:
    raise SystemExit(f"Expected 238 unique deepenings; found {len(seen_paragraphs)}")
MODULES_PATH.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n")

# Keep legacy enriched curriculum sources aligned when they contain a target lesson.
updated_enriched = 0
for module_id, lesson_additions in deepenings.items():
    path = ROOT / "src/data/enriched" / f"{module_id}.json"
    if not path.is_file():
        continue
    item = json.loads(path.read_text())
    enriched_by_title = {lesson.get("title"): lesson for lesson in item.get("lessons", [])}
    for title, paragraph in lesson_additions.items():
        lesson = enriched_by_title.get(title)
        if lesson is None:
            continue
        body = str(lesson.get("body", ""))
        body, legacy_updates = replace_legacy_deepening(body, module_id, title, paragraph)
        replaced_legacy += legacy_updates
        occurrences = body.count(paragraph)
        if occurrences > 1:
            raise SystemExit(f"Legacy source {module_id}/{title} contains a duplicated deepening")
        if occurrences == 0:
            lesson["body"] = f"{body.rstrip()}\n\n{paragraph}" if body.strip() else paragraph
            updated_enriched += 1
    path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n")

print(f"Applied second-stage deepenings to 238 existing lessons ({updated} new bundled paragraphs; {replaced_legacy} stale median paragraphs reconciled; {updated_enriched} legacy lesson bodies aligned).")
