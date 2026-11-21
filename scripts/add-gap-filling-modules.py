#!/usr/bin/env python3
"""Idempotently add the focused curriculum gaps from a maintained JSON source."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES_PATH = ROOT / "src/data/modules.json"
EXTRA_PATH = ROOT / "src/data/gap-filling-modules.json"
DESCRIPTIONS_PATH = ROOT / "src/data/module-descriptions.json"

modules = json.loads(MODULES_PATH.read_text())
extra = json.loads(EXTRA_PATH.read_text())
descriptions = json.loads(DESCRIPTIONS_PATH.read_text())

if len({module["id"] for module in modules}) != len(modules):
    raise SystemExit("The base curriculum contains duplicate IDs")
if len({module["id"] for module in extra}) != len(extra):
    raise SystemExit("The new curriculum source contains duplicate IDs")
if len({module["slug"] for module in extra}) != len(extra):
    raise SystemExit("The new curriculum source contains duplicate slugs")

by_id = {module["id"]: index for index, module in enumerate(modules)}
for module in extra:
    if not module.get("lessons") or len(module["lessons"]) < 5:
        raise SystemExit(f"{module['id']} needs at least five lessons")
    if not module.get("sources") or not module.get("quiz"):
        raise SystemExit(f"{module['id']} needs sources and a knowledge check")
    existing = by_id.get(module["id"])
    if existing is None:
        if any(item["slug"] == module["slug"] for item in modules):
            raise SystemExit(f"Slug collision for {module['slug']}")
        by_id[module["id"]] = len(modules)
        modules.append(module)
    else:
        if modules[existing]["slug"] != module["slug"]:
            raise SystemExit(f"ID {module['id']} already maps to another slug")
        modules[existing] = module
    descriptions[module["id"]] = module["excerpt"]

if len({module["slug"] for module in modules}) != len(modules):
    raise SystemExit("Merged curriculum contains duplicate slugs")
MODULES_PATH.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n")
DESCRIPTIONS_PATH.write_text(json.dumps(descriptions, ensure_ascii=False, indent=2) + "\n")
print(f"Added or refreshed {len(extra)} gap-filling modules; curriculum now has {len(modules)} modules and {sum(len(m['lessons']) for m in modules)} lessons.")
