#!/usr/bin/env python3
"""Attach curated GitHub teaching references to the relevant modules.

The linked repositories are reference-only: no source prose, figures, data,
code, or problem sets are copied into the site. The short examples in
lesson-expansions.json are authored independently.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES_PATH = ROOT / "src/data/modules.json"


def openintro(chapter: str, title: str) -> dict[str, str]:
    return {
        "label": f"OpenIntro Statistics — {title} (CC BY-SA 3.0)",
        "url": f"https://github.com/OpenIntroStat/openintro-statistics/tree/master/{chapter}",
    }


def causality(chapter: str, title: str) -> dict[str, str]:
    return {
        "label": f"Matheus Facure — {title} (Causal Inference for the Brave and True; MIT)",
        "url": f"https://github.com/matheusfacure/python-causality-handbook/blob/master/causal-inference-for-the-brave-and-true/{chapter}.ipynb",
    }


def ec607(lecture: str, title: str, folder: str, filename: str) -> dict[str, str]:
    return {
        "label": f"Edward Rubin — EC 607: {title} (license not stated; link only)",
        "url": f"https://github.com/edrubin/EC607S23/blob/master/notes-lecture/{folder}/{filename}.html",
    }


RESOURCES: dict[str, list[dict[str, str]]] = {
    "statistical-thinking": [
        openintro("ch_intro_to_data", "Ch. 1: Introduction to Data"),
        openintro("ch_summarizing_data", "Ch. 2: Summarizing Data"),
        {
            "label": "OpenIntro Statistics — repository license (CC BY-SA 3.0)",
            "url": "https://github.com/OpenIntroStat/openintro-statistics/blob/master/LICENSE.md",
        },
    ],
    "probability": [openintro("ch_probability", "Ch. 3: Probability")],
    "distributions": [openintro("ch_distributions", "Ch. 4: Distributions")],
    "estimation": [openintro("ch_inference_for_means", "Ch. 7: Inference for Numerical Data")],
    "p-values": [
        openintro("ch_inference_for_means", "Ch. 7: Inference for Numerical Data"),
        openintro("ch_inference_for_props", "Ch. 6: Inference for Categorical Data"),
    ],
    "regression": [
        openintro("ch_regr_simple_linear", "Ch. 8: Introduction to Linear Regression"),
        openintro("ch_regr_mult_and_log", "Ch. 9: Multiple and Logistic Regression"),
        causality("05-The-Unreasonable-Effectiveness-of-Linear-Regression", "Ch. 05: Linear Regression"),
        ec607("03", "Lecture 03: Why Regression?", "03-why-regression", "03-why-regression"),
        ec607("05", "Lecture 05: Regression Stuff", "05-regression-stuff", "05-regression-stuff"),
    ],
    "exploratory-data-analysis": [
        openintro("ch_intro_to_data", "Ch. 1: Introduction to Data"),
        openintro("ch_summarizing_data", "Ch. 2: Summarizing Data"),
    ],
    "correlation": [openintro("ch_regr_simple_linear", "Ch. 8: Linear Regression and Correlation")],
    "causal": [
        causality("01-Introduction-To-Causality", "Ch. 01: Introduction to Causality"),
        causality("02-Randomised-Experiments", "Ch. 02: Randomised Experiments"),
        causality("04-Graphical-Causal-Models", "Ch. 04: Graphical Causal Models"),
        {
            "label": "Matheus Facure — repository license (MIT)",
            "url": "https://github.com/matheusfacure/python-causality-handbook/blob/master/LICENSE",
        },
        ec607("02", "Lecture 02: The Experimental Ideal", "02-the-ideal", "02-the-ideal"),
        ec607("06", "Lecture 06: Controls", "06-controls", "06-controls"),
        ec607("07", "Lecture 07: DAGs", "07-dags", "07-dags"),
    ],
    "experimental-design": [
        causality("02-Randomised-Experiments", "Ch. 02: Randomised Experiments"),
        ec607("02", "Lecture 02: The Experimental Ideal", "02-the-ideal", "02-the-ideal"),
    ],
    "iv-2sls": [
        causality("08-Instrumental-Variables", "Ch. 08: Instrumental Variables"),
        causality("09-Non-Compliance-and-LATE", "Ch. 09: Non-compliance and LATE"),
        ec607("09", "Lecture 09: Instrumental Variables", "09-iv", "09-iv"),
    ],
    "matching-weighting": [
        causality("10-Matching", "Ch. 10: Matching"),
        causality("11-Propensity-Score", "Ch. 11: Propensity Scores"),
        causality("12-Doubly-Robust-Estimation", "Ch. 12: Doubly Robust Estimation"),
        ec607("08", "Lecture 08: Matching", "08-matching", "08-matching"),
    ],
    "difference-in-differences": [
        causality("13-Difference-in-Differences", "Ch. 13: Difference-in-Differences"),
    ],
    "panel-fixed-effects": [
        causality("14-Panel-Data-and-Fixed-Effects", "Ch. 14: Panel Data and Fixed Effects"),
    ],
    "synthetic-control": [
        causality("15-Synthetic-Control", "Ch. 15: Synthetic Control"),
    ],
    "regression-discontinuity": [
        causality("16-Regression-Discontinuity-Design", "Ch. 16: Regression Discontinuity"),
        ec607("10", "Lecture 10: Regression Discontinuity", "10-rd", "10-rd"),
    ],
    "heterogeneous-effects": [
        causality("18-Heterogeneous-Treatment-Effects-and-Personalization", "Ch. 18: Heterogeneous Treatment Effects"),
    ],
    "robust-clustered-inference": [
        ec607("11", "Lecture 11: Inference and Clustering", "11-clustering", "11-clustering"),
    ],
}


def main() -> None:
    modules = json.loads(MODULES_PATH.read_text())
    by_id = {module["id"]: module for module in modules}
    missing = sorted(set(RESOURCES) - set(by_id))
    if missing:
        raise SystemExit(f"GitHub resource map references unknown modules: {missing}")

    added = 0
    for module_id, resources in RESOURCES.items():
        module = by_id[module_id]
        sources = module.setdefault("sources", [])
        urls = {source.get("url") for source in sources}
        for resource in resources:
            if resource["url"] not in urls:
                sources.append(resource)
                urls.add(resource["url"])
                added += 1

    MODULES_PATH.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n")
    print(f"Attached {added} GitHub teaching references across {len(RESOURCES)} modules (idempotent).")


if __name__ == "__main__":
    main()
