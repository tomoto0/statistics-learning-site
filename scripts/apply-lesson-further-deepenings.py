#!/usr/bin/env python3
"""Append the third, lesson-specific teaching deepening to every existing lesson."""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES_PATH = ROOT / "src/data/modules.json"
DEEPENINGS_PATH = ROOT / "src/data/lesson-further-deepenings.json"

modules = json.loads(MODULES_PATH.read_text())
further = json.loads(DEEPENINGS_PATH.read_text())

# Earlier bundled copies of several prepared paragraphs carried an unsupported
# publisher attribution. Normalize it before duplicate checks so the corrected
# source paragraph is recognized as an edit, not appended as a near-duplicate.
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
lesson_count = sum(len(module.get("lessons", [])) for module in modules)
if len(modules) != 42 or lesson_count != 238:
    raise SystemExit(f"Expected the fixed 42-module/238-lesson curriculum; found {len(modules)} modules and {lesson_count} lessons")
by_id = {module["id"]: module for module in modules}
if len(by_id) != len(modules):
    raise SystemExit("Module IDs must remain unique")
unknown = sorted(set(further) - set(by_id))
missing = sorted(set(by_id) - set(further))
if unknown or missing:
    raise SystemExit(f"Module coverage mismatch; unknown={unknown}, missing={missing}")

seen = set()

def word_fivegrams(text):
    words = re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", text).casefold())
    return {" ".join(words[index:index + 5]) for index in range(max(0, len(words) - 4))}

def containment_similarity(left, right):
    a = word_fivegrams(left)
    b = word_fivegrams(right)
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))

updated = 0
for module_id, lesson_additions in further.items():
    module = by_id[module_id]
    by_title = {lesson.get("title"): lesson for lesson in module.get("lessons", [])}
    if len(by_title) != len(module.get("lessons", [])):
        raise SystemExit(f"{module_id} has duplicate lesson titles")
    if set(lesson_additions) != set(by_title):
        missing_titles = sorted(set(by_title) - set(lesson_additions))
        extra_titles = sorted(set(lesson_additions) - set(by_title))
        raise SystemExit(f"{module_id} lesson coverage mismatch; missing={missing_titles}, extra={extra_titles}")
    for title, paragraph in lesson_additions.items():
        if not isinstance(paragraph, str) or len(paragraph) < 600:
            raise SystemExit(f"{module_id}/{title} has a missing or shallow third-pass deepening")
        words = len(paragraph.split())
        if not 100 <= words <= 135 or "\n" in paragraph.strip():
            raise SystemExit(f"{module_id}/{title} has unexpected length/format ({words} whitespace-delimited words)")
        normalized = " ".join(unicodedata.normalize("NFKC", paragraph).casefold().split())
        if normalized in seen:
            raise SystemExit(f"Duplicate third-pass deepening detected at {module_id}/{title}")
        seen.add(normalized)
        lesson = by_title[title]
        body = str(lesson.get("body", ""))
        for previous in body.split("\n\n"):
            if previous.strip() and previous.strip() != paragraph.strip() and containment_similarity(paragraph, previous) >= 0.48:
                raise SystemExit(f"{module_id}/{title} is too similar to an existing lesson paragraph")
        occurrences = body.count(paragraph)
        if occurrences > 1:
            raise SystemExit(f"{module_id}/{title} already contains a duplicated third-pass deepening")
        if occurrences == 0:
            lesson["body"] = f"{body.rstrip()}\n\n{paragraph}" if body.strip() else paragraph
            updated += 1

if len(seen) != 238:
    raise SystemExit(f"Expected 238 unique third-pass deepenings; found {len(seen)}")
MODULES_PATH.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n")
print(f"Applied third-stage deepenings to 238 existing lessons ({updated} new bundled paragraphs).")
