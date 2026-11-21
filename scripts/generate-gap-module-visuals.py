#!/usr/bin/env python3
"""Build accessible, original SVG card art and teaching diagrams for four modules."""
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src/data/modules.json"
CARDS = ROOT / "public/images/module-cards"
DIAGRAMS = ROOT / "public/diagrams"
CARDS.mkdir(parents=True, exist_ok=True)
DIAGRAMS.mkdir(parents=True, exist_ok=True)
NAVY, PANEL, GRID = "#101a2b", "#17263d", "#31415a"
MINT, CORAL, BLUE, GOLD = "#61d6b3", "#ff8a76", "#8fb5ff", "#f0c46d"
PALE, MUTED, WHITE = "#dce7f3", "#9aabc0", "#f8fbff"


def esc(value):
    return html.escape(str(value), quote=True)


def text(x, y, value, size=12, color=PALE, anchor="start", weight=500):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" font-size="{size}" font-weight="{weight}">{esc(value)}</text>'


def line(x1, y1, x2, y2, color=GRID, width=2, dash=None, marker=False):
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    extra += ' marker-end="url(#arrow)"' if marker else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{extra}/>'


def path(points, color=BLUE, width=3, dash=None):
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{extra}/>'


def circle(cx, cy, radius, fill, stroke=PANEL, sw=2):
    return f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def rect(x, y, width, height, fill=PANEL, stroke=GRID, radius=12, sw=1):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def arrow(x1, y1, x2, y2, color=MUTED, width=3, dash=None):
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="{width}"{extra} marker-end="url(#arrow)"/>'


def diagram(title, description, body, height=330):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="{height}" viewBox="0 0 760 {height}" role="img" aria-labelledby="title desc">
<title id="title">{esc(title)}</title><desc id="desc">{esc(description)}</desc>
<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L0,9 L9,4.5 z" fill="{MUTED}"/></marker></defs>
<rect width="760" height="{height}" rx="24" fill="{NAVY}"/><rect x="16" y="16" width="728" height="{height-32}" rx="20" fill="{PANEL}" stroke="{GRID}" stroke-width="2"/>
{text(38, 48, title, 19, WHITE, weight=700)}{body}
<text x="722" y="{height-28}" text-anchor="end" fill="{MUTED}" font-size="10" font-weight="700" letter-spacing="1">ORIGINAL SCHEMATIC · NOT DATA</text>
</svg>'''


def card(title, description, body, legend):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400" role="img" aria-labelledby="title desc">
<title id="title">{esc(title)} — concept illustration</title><desc id="desc">{esc(description)} Original schematic, not measured data.</desc>
<defs><linearGradient id="surface" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset="1" stop-color="#15243a"/></linearGradient><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L0,10 L9,5 z" fill="{MUTED}"/></marker></defs>
<rect width="600" height="400" rx="28" fill="url(#surface)"/><rect x="18" y="18" width="564" height="364" rx="23" fill="{PANEL}" stroke="{GRID}" stroke-width="2"/>
{body}{text(300, 344, legend, 11, PALE, "middle", 700)}<text x="548" y="365" text-anchor="end" fill="{MUTED}" font-size="11" font-weight="700" letter-spacing="1.2">CONCEPT · NOT DATA</text>
</svg>'''


def regularization_art():
    body = text(74, 91, "Coefficient paths", 12, PALE, weight=700)
    body += line(92, 286, 333, 286, MUTED, 1) + line(92, 120, 92, 286, MUTED, 1)
    body += line(92, 203, 333, 203, MUTED, 1, "5 4") + text(86, 206, "0", 8, MUTED, "end", 600)
    body += path([(103, 132), (145, 150), (190, 169), (235, 184), (280, 195), (323, 200)], BLUE, 4)
    body += path([(103, 274), (145, 256), (190, 237), (235, 222), (280, 211), (323, 206)], CORAL, 4)
    body += text(102, 310, "weak", 9, MUTED) + text(324, 310, "strong λ →", 9, MUTED, "end")
    body += text(102, 127, "β₁ > 0", 9, BLUE, weight=700) + text(323, 222, "β₂ < 0", 9, CORAL, "end", 700)
    body += text(395, 91, "Prediction error", 12, PALE, weight=700)
    body += line(410, 286, 535, 286, MUTED, 1) + line(410, 120, 410, 286, MUTED, 1)
    body += path([(418, 247), (445, 218), (472, 174), (498, 146), (523, 159)], MINT, 4)
    body += path([(418, 143), (445, 162), (472, 201), (498, 236), (523, 263)], BLUE, 3)
    body += text(414, 310, "weak", 9, MUTED) + text(525, 310, "strong λ →", 9, MUTED, "end")
    body += text(552, 147, "validation", 9, MINT, weight=700) + text(552, 270, "training", 9, BLUE, weight=700)
    body += text(470, 128, "bias–variance trade-off", 9, GOLD, "middle")
    return body


def meta_art():
    body = text(40, 77, "Study", 10, MUTED, weight=700)
    lo, hi, x0, x1 = -0.6, 1.0, 230, 700
    def x(value):
        return x0 + (value - lo) / (hi - lo) * (x1 - x0)
    studies = [("Study A", -0.05, 0.28), ("Study B", 0.12, 0.18), ("Study C", 0.42, 0.35), ("Study D", 0.57, 0.24), ("Study E", 0.24, 0.31)]
    body += text(40, 103, "Individual estimates", 10, PALE)
    for i, (name, effect, se) in enumerate(studies):
        y = 107 + i * 33
        body += text(40, y + 3, name, 11, PALE)
        body += line(x(effect - 1.96 * se), y, x(effect + 1.96 * se), y, BLUE, 2)
        body += line(x(effect - 1.96 * se), y - 5, x(effect - 1.96 * se), y + 5, BLUE, 1)
        body += line(x(effect + 1.96 * se), y - 5, x(effect + 1.96 * se), y + 5, BLUE, 1)
        body += circle(round(x(effect), 1), y, 4, CORAL, PANEL, 1)
    zero = x(0)
    body += line(zero, 86, zero, 290, GOLD, 1.5, "5 4")
    body += text(zero + 4, 89, "zero", 9, GOLD)
    for label, effect, se, color in [("Fixed summary", 0.24, 0.16, CORAL), ("Random-effects summary", 0.25, 0.27, MINT)]:
        y = 280 if label.startswith("Fixed") else 310
        body += text(40, y + 3, label, 11, color, weight=700)
        left, mid, right = x(effect - 1.96 * se), x(effect), x(effect + 1.96 * se)
        body += line(left, y, right, y, color, 2.5)
        body += f'<path d="M{left:.1f},{y} L{mid:.1f},{y-7} L{right:.1f},{y} L{mid:.1f},{y+7} Z" fill="{color}" opacity=".85"/>'
    body += line(x0, 337, x1, 337, MUTED, 1)
    for value in [-0.5, 0, 0.5, 1.0]:
        xx = x(value)
        body += line(round(xx, 1), 334, round(xx, 1), 340, MUTED, 1) + text(round(xx, 1), 353, f"{value:g}", 9, MUTED, "middle")
    body += text((x0 + x1) / 2, 370, "Effect (standardized units) · interval width shows uncertainty", 10, PALE, "middle")
    return body


def mediation_art():
    body = arrow(205, 150, 332, 150, BLUE, 3) + arrow(421, 150, 545, 150, MINT, 3)
    body += f'<path d="M205,138 C290,70 465,70 548,138" fill="none" stroke="{CORAL}" stroke-width="3" marker-end="url(#arrow)"/>'
    body += arrow(270, 265, 344, 177, GOLD, 2.5, "6 5") + arrow(397, 265, 571, 177, GOLD, 2.5, "6 5")
    for x, label, fill in [(166, "T", BLUE), (376, "M", CORAL), (590, "Y", MINT), (250, "U", GOLD)]:
        y = 150 if label != "U" else 282
        radius = 31 if label != "U" else 25
        body += circle(x, y, radius, fill, PANEL, 3) + text(x, y + 6, label, 20, NAVY, "middle", 700)
    body += text(260, 137, "a", 12, BLUE, "middle", 700) + text(480, 137, "b", 12, MINT, "middle", 700)
    body += text(374, 81, "direct path c′", 11, CORAL, "middle", 700)
    body += text(429, 265, "possible mediator–outcome confounding", 10, GOLD, "middle", 700)
    body += text(166, 211, "Treatment", 10, PALE, "middle") + text(376, 211, "Mediator", 10, PALE, "middle") + text(590, 211, "Outcome", 10, PALE, "middle")
    body += text(250, 323, "U is unobserved in this sensitivity scenario", 10, GOLD, "middle")
    body += text(380, 350, "Arrows are a causal hypothesis; the dashed paths are not ruled out by randomizing T alone.", 10, MUTED, "middle")
    return body


def partial_art():
    body = text(40, 79, "Observed sample", 12, PALE, weight=700)
    body += text(40, 112, "Training offer", 10, MUTED) + text(40, 159, "Control", 10, MUTED)
    # Response bars: the muted segment is missing follow-up, not a zero outcome.
    body += rect(128, 94, 210, 24, BLUE, "none", 5, 0) + rect(128 + 210 * .88, 94, 25.2, 24, GOLD, "none", 5, 0)
    body += rect(128, 141, 210 * .78, 24, MINT, "none", 5, 0) + rect(128 + 210 * .78, 141, 46.2, 24, GOLD, "none", 5, 0)
    body += text(128, 135, "88% observed · 74% pass", 9, PALE)
    body += text(128, 182, "78% observed · 59% pass", 9, PALE)
    body += text(130, 205, "Gold = outcomes not observed; they may be 0 or 1", 9, GOLD)
    body += text(406, 79, "Compatible treatment-effect set", 12, PALE, weight=700)
    x0, x1, y = 432, 710, 144
    lo, hi = -0.2, 0.4
    X = lambda value: x0 + (value - lo) / (hi - lo) * (x1 - x0)
    zero = X(0)
    body += line(zero, 103, zero, 194, GOLD, 1.5, "5 4") + text(zero + 3, 101, "0", 9, GOLD)
    a, b = X(-0.029), X(0.311)
    body += line(a, y, b, y, CORAL, 8) + line(a, y - 10, a, y + 10, CORAL, 2) + line(b, y - 10, b, y + 10, CORAL, 2)
    body += circle(a, y, 5, CORAL, PANEL, 1) + circle(b, y, 5, CORAL, PANEL, 1)
    body += line(x0, 195, x1, 195, MUTED, 1)
    for value in [-0.2, 0, 0.2, 0.4]:
        xx = X(value)
        body += line(round(xx, 1), 192, round(xx, 1), 198, MUTED, 1) + text(round(xx, 1), 212, f"{value:.1f}", 9, MUTED, "middle")
    body += text((x0 + x1) / 2, 238, "Effect on pass rate", 10, PALE, "middle")
    body += text((a + b) / 2, 171, "−0.029 to +0.311", 11, CORAL, "middle", 700)
    body += text(380, 273, "Binary outcome: unknown cases widen each group's mean range.", 10, MUTED, "middle")
    body += text(380, 293, "The interval crossing zero means the sign is not identified without more assumptions.", 10, GOLD, "middle")
    return body


cards = {
    "regularization-cross-validation": card(
        "Regularization, Cross-Validation & Prediction",
        "Two coefficient paths shrink as the penalty grows; a validation-error curve has a broad minimum while training error rises.",
        line(92, 285, 510, 285, MUTED, 1) + line(92, 115, 92, 285, MUTED, 1)
        + path([(105,145),(175,160),(245,192),(315,224),(385,249),(455,266)], BLUE, 5)
        + path([(105,264),(175,248),(245,221),(315,193),(385,165),(455,147)], CORAL, 5)
        + path([(105,240),(175,216),(245,177),(315,147),(385,163),(455,208)], MINT, 4)
        + path([(105,148),(175,163),(245,195),(315,224),(385,248),(455,264)], GOLD, 3)
        + line(315, 122, 315, 285, GOLD, 1.5, "6 5")
        + text(150, 118, "coefficient size", 11, PALE, weight=700)
        + text(385, 118, "error", 11, PALE, weight=700)
        + text(105, 310, "weak penalty", 9, MUTED) + text(455, 310, "strong λ →", 9, MUTED, "end")
        + text(320, 139, "validation minimum", 9, GOLD, "middle")
        + text(485, 153, "CV", 9, MINT, weight=700) + text(485, 270, "train", 9, BLUE, weight=700),
        "λ shrinks coefficients · choose with validation data"),
    "meta-analysis-evidence-synthesis": card(
        "Meta-Analysis & Evidence Synthesis for Economics",
        "Study estimates and uncertainty intervals are combined into a random-effects summary; the zero line is an effect reference.",
        line(82, 290, 520, 290, MUTED, 1) + line(292, 112, 292, 292, GOLD, 1.5, "5 5")
        + text(292, 106, "zero", 9, GOLD, "middle")
        + line(150, 143, 340, 143, BLUE, 2) + circle(245, 143, 6, CORAL, PANEL, 2)
        + line(205, 185, 390, 185, BLUE, 2) + circle(300, 185, 6, CORAL, PANEL, 2)
        + line(245, 227, 455, 227, BLUE, 2) + circle(350, 227, 6, CORAL, PANEL, 2)
        + line(210, 269, 420, 269, BLUE, 2) + circle(315, 269, 6, CORAL, PANEL, 2)
        + text(120, 147, "Study A", 9, PALE) + text(120, 189, "Study B", 9, PALE)
        + text(120, 231, "Study C", 9, PALE) + text(120, 273, "Study D", 9, PALE)
        + line(250, 314, 365, 314, MINT, 3) + text(135, 318, "Random-effects", 9, MINT, weight=700)
        + text(500, 318, "between-study variation", 8, GOLD, "end"),
        "Study estimates + intervals · pooled mean allows heterogeneity"),
    "causal-mediation-mechanisms": card(
        "Causal Mediation & Mechanism Analysis",
        "Treatment T affects mediator M, which may affect outcome Y; a direct path and a hidden mediator–outcome confounder are shown.",
        arrow(198, 204, 289, 164, BLUE, 4) + arrow(358, 164, 439, 203, MINT, 4)
        + f'<path d="M196,190 C260,99 385,99 444,190" fill="none" stroke="{CORAL}" stroke-width="4" marker-end="url(#arrow)"/>'
        + arrow(271, 282, 310, 181, GOLD, 3, "6 5") + arrow(327, 282, 455, 230, GOLD, 3, "6 5")
        + circle(174, 210, 30, BLUE, PANEL, 3) + circle(326, 152, 30, CORAL, PANEL, 3)
        + circle(466, 210, 30, MINT, PANEL, 3) + circle(295, 305, 23, GOLD, PANEL, 3)
        + text(174, 217, "T", 20, NAVY, "middle", 700) + text(326, 159, "M", 20, NAVY, "middle", 700)
        + text(466, 217, "Y", 20, NAVY, "middle", 700) + text(295, 311, "U", 17, NAVY, "middle", 700)
        + text(236, 166, "a", 11, BLUE, weight=700) + text(397, 168, "b", 11, MINT, weight=700)
        + text(322, 113, "direct c′", 10, CORAL, "middle", 700)
        + text(410, 294, "possible hidden confounding", 8, GOLD, "middle", 700),
        "T → M → Y · direct path · mediation assumptions matter"),
    "partial-identification-bounds": card(
        "Partial Identification, Bounds & Sensitivity",
        "Observed and missing binary outcomes produce a treatment-effect interval rather than one exact point; zero remains inside this example set.",
        rect(88, 134, 190, 78, "#203553", GRID, 10, 1) + rect(88, 226, 190, 54, "#203553", GRID, 10, 1)
        + text(105, 158, "Treatment group", 10, PALE, weight=700) + rect(105, 174, 136, 13, BLUE, "none", 4, 0) + rect(241, 174, 18, 13, GOLD, "none", 4, 0)
        + text(105, 248, "Control group", 10, PALE, weight=700) + rect(105, 263, 119, 13, MINT, "none", 4, 0) + rect(224, 263, 35, 13, GOLD, "none", 4, 0)
        + line(337, 250, 510, 250, MUTED, 1) + line(414, 135, 414, 252, GOLD, 2, "6 5")
        + line(365, 198, 493, 198, CORAL, 7) + circle(365, 198, 7, CORAL, PANEL, 2) + circle(493, 198, 7, CORAL, PANEL, 2)
        + text(414, 128, "zero", 9, GOLD, "middle") + text(429, 177, "compatible effect range", 9, CORAL, "middle", 700)
        + text(300, 311, "Stronger assumptions can narrow the set", 10, PALE, "middle"),
        "Observed data → lower and upper effect bounds"),
}

modules = json.loads(DATA.read_text())
by_id = {module["id"]: module for module in modules}
required = {
    "regularization-cross-validation": "Regularization, Cross-Validation & Prediction",
    "meta-analysis-evidence-synthesis": "Meta-Analysis & Evidence Synthesis for Economics",
    "causal-mediation-mechanisms": "Causal Mediation & Mechanism Analysis",
    "partial-identification-bounds": "Partial Identification, Bounds & Sensitivity",
}
if set(cards) != set(required):
    raise SystemExit("The visual map does not exactly cover the four new modules")
if not set(required).issubset(by_id):
    raise SystemExit(f"Missing module records: {sorted(set(required) - set(by_id))}")

regularization = diagram("Regularization stabilizes prediction", "Left: one positive and one negative coefficient both move toward the zero line as the penalty grows. Right: the illustrative validation-error curve falls and then rises while training error increases.", regularization_art(), 350)
meta = diagram("A forest plot combines study estimates", "Five illustrative study estimates with uncertainty intervals, a zero reference, and fixed- and random-effects summary diamonds. The effects are a schematic example, not measured results.", meta_art(), 400)
mediation = diagram("Treatment, mediator, outcome and a hidden common cause", "A proposed T-to-M-to-Y pathway, a direct T-to-Y path, and a possible unmeasured cause U of both mediator and outcome. Dashed arrows identify an assumption the analysis must address.", mediation_art(), 380)
partial = diagram("Missing binary outcomes imply treatment-effect bounds", "Synthetic response and pass rates for treatment and control groups imply an effect range from about minus 0.029 to plus 0.311, crossing zero. Gold segments indicate outcomes not observed.", partial_art(), 340)
figures = {
    "regularization-cross-validation": (regularization, "The left chart shows one positive and one negative coefficient approaching a labeled zero baseline as λ strengthens. The right chart contrasts a stylized validation-error minimum with rising training error; all curves are explanatory, not fitted results.", "Original teaching schematic; signed coefficient paths shrink toward zero and error curves are stylized illustrations, not fitted economic data."),
    "meta-analysis-evidence-synthesis": (meta, "A separate schematic shows five illustrative study estimates; the interactive default draws nine synthetic studies and lets the learner change their number. Both include pooled summaries and intervals; these are not measured study results.", "The static figure uses five illustrative studies; the interactive lab defaults to nine and is controlled separately. All are schematic examples, not measured results."),
    "causal-mediation-mechanisms": (mediation, "T is treatment, M is a proposed mediator and Y is the outcome. Solid arrows show mediated and direct paths; dashed arrows from U show possible mediator–outcome confounding that treatment randomization alone does not rule out.", "Original causal hypothesis diagram; arrows are assumptions to assess, not empirical findings."),
    "partial-identification-bounds": (partial, "A synthetic training-offer example shows observed follow-up and missing binary outcomes for treatment and control, then an effect bound from −0.029 to +0.311 that crosses zero.", "Original teaching example using synthetic rates; interval endpoints are worst-case bounds under the binary-outcome support."),
}

for module_id, (svg, alt, caption) in figures.items():
    module = by_id[module_id]
    expected_title = required[module_id]
    if module["title"] != expected_title:
        raise SystemExit(f"Unexpected title for {module_id}: {module['title']}")
    (DIAGRAMS / f"{module_id}.svg").write_text(svg + "\n")
    module["diagram"] = f"/diagrams/{module_id}.svg"
    module["diagramAlt"] = alt
    module["diagramCaption"] = caption
    (CARDS / f"{module_id}.svg").write_text(cards[module_id] + "\n")
    module["cardImage"] = f"/images/module-cards/{module_id}.svg"

DATA.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n")
print(f"Generated {len(figures)} accessible specialist diagrams and {len(cards)} matching 3:2 module-card illustrations.")
