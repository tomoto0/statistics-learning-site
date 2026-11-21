#!/usr/bin/env python3
"""Apply the plain-language catalogue summaries after curriculum generation."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES_PATH = ROOT / "src/data/modules.json"
DESCRIPTIONS_PATH = ROOT / "src/data/module-descriptions.json"
modules = json.loads(MODULES_PATH.read_text())
descriptions = json.loads(DESCRIPTIONS_PATH.read_text())

module_ids = {module["id"] for module in modules}
description_ids = set(descriptions)
if module_ids != description_ids:
    missing = sorted(module_ids - description_ids)
    unknown = sorted(description_ids - module_ids)
    raise SystemExit(f"Description map must cover the curriculum exactly; missing={missing}, unknown={unknown}")

for module in modules:
    description = descriptions[module["id"]]
    if not isinstance(description, str) or len(description) < 150:
        raise SystemExit(f"Description for {module['id']} is missing or too short")
    module["excerpt"] = description

MODULES_PATH.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n")

# Keep the older enriched source files aligned for the modules they contain.
updated_enriched = 0
for module_id, description in descriptions.items():
    path = ROOT / "src/data/enriched" / f"{module_id}.json"
    if path.is_file():
        item = json.loads(path.read_text())
        item["excerpt"] = description
        path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n")
        updated_enriched += 1

print(f"Applied expanded descriptions to {len(modules)} modules ({updated_enriched} enriched source files aligned).")
