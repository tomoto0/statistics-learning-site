#!/usr/bin/env python3
"""Apply verified, source-backed curriculum audit corrections after catalog generation."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES_PATH = ROOT / "src/data/modules.json"
BASELINE_PATH = ROOT / "test/curriculum-structure-baseline.json"
modules = json.loads(MODULES_PATH.read_text())
baseline = json.loads(BASELINE_PATH.read_text())
by_id = {module["id"]: module for module in modules}
if len(modules) != 42 or sum(len(m.get("lessons", [])) for m in modules) != 238:
    raise SystemExit("Audit corrections require the existing 42-module/238-lesson curriculum")
if [m["id"] for m in modules] != [m["id"] for m in baseline["modules"]]:
    raise SystemExit("Module order/IDs differ from the audited structural baseline")
for actual, expected in zip(modules, baseline["modules"]):
    if actual.get("slug") != expected.get("slug") or actual.get("title") != expected.get("title"):
        raise SystemExit(f"Module identity changed: {actual.get('id')}")
    if [l["title"] for l in actual.get("lessons", [])] != [l["title"] for l in expected.get("lessons", [])]:
        raise SystemExit(f"Lesson title/order changed: {actual.get('id')}")

changed = 0

def replace_once(text, old, new, label):
    global changed
    count = text.count(old)
    if count == 1:
        changed += 1
        return text.replace(old, new, 1)
    if count == 0 and new in text:
        return text  # Idempotent after a previous seed.
    raise SystemExit(f"Expected exactly one pre-correction phrase for {label}; found {count}")


def module(mid):
    if mid not in by_id:
        raise SystemExit(f"Missing module {mid}")
    return by_id[mid]


def lesson(mid, title):
    matches = [item for item in module(mid).get("lessons", []) if item.get("title") == title]
    if len(matches) != 1:
        raise SystemExit(f"Expected one lesson {mid}/{title}; found {len(matches)}")
    return matches[0]


def edit_lesson(mid, title, field, old, new, label=None):
    item = lesson(mid, title)
    if field not in item or not isinstance(item[field], str):
        raise SystemExit(f"Missing text field {mid}/{title}/{field}")
    item[field] = replace_once(item[field], old, new, label or f"{mid}/{title}/{field}")


def edit_module_field(mid, field, old, new):
    item = module(mid)
    if not isinstance(item.get(field), str):
        raise SystemExit(f"Missing module text field {mid}/{field}")
    item[field] = replace_once(item[field], old, new, f"{mid}/{field}")


def edit_source(mid, old_url, new_label, new_url=None, old_label=None):
    sources = module(mid).get("sources", [])
    matches = [s for s in sources if s.get("url") == old_url and (old_label is None or s.get("label") == old_label)]
    target_url = new_url or old_url
    already = [s for s in sources if s.get("url") == target_url and s.get("label") == new_label]
    if len(matches) == 1:
        matches[0]["label"] = new_label
        matches[0]["url"] = target_url
    elif len(matches) == 0 and len(already) == 1:
        return
    else:
        raise SystemExit(f"Expected one source to update in {mid}; found {len(matches)}")


def add_source(mid, label, url):
    sources = module(mid).setdefault("sources", [])
    if any(s.get("url") == url for s in sources):
        return
    sources.append({"label": label, "url": url})


def replace_in_module_strings(mid, old, new):
    """Replace a bibliographic phrase in all learner-facing strings in one module."""
    def walk(value):
        global changed
        if isinstance(value, str):
            if old in value:
                changed += value.count(old)
                return value.replace(old, new)
            return value
        if isinstance(value, list):
            for index, child in enumerate(value):
                value[index] = walk(child)
            return value
        if isinstance(value, dict):
            for key, child in list(value.items()):
                value[key] = walk(child)
            return value
        return value
    walk(module(mid))

# The explanation must answer the quiz question it accompanies.
quiz = module("statistical-thinking").get("quiz", {})
quiz["explanation"] = replace_once(
    quiz.get("explanation", ""),
    "The p-value is conditional on the null model; it does not give the probability either hypothesis is true.",
    "The mean uses every value and is sensitive to extremes, whereas the median depends on the ordered middle position(s). A few extreme changes can therefore move the mean while barely changing the median.",
    "statistical-thinking/module quiz explanation",
)
edit_lesson(
    "statistical-thinking", "Compare center and spread with a worked example", "body",
    "In both settings, the median remains −0.4 pp:",
    "In both settings, the median remains −0.30 pp (the average of −0.4 and −0.2 pp):",
)
edit_source(
    "statistical-thinking", "https://www.itl.nist.gov/div898/handbook/eda/section1/eda14.htm",
    "NIST/SEMATECH — Histogram", "https://www.itl.nist.gov/div898/handbook/eda/section3/histogra.htm",
)

# Case-study sample accounting and a histogram's actual mark type.
edit_module_field(
    "distributions", "caseStudy",
    "Generate 10,000 draws from a heavy-tailed distribution with a mean of 0.04% per day, then form 1,000 non-overlapping blocks of 60 observations and calculate each block mean.",
    "Generate 10,000 draws from a heavy-tailed distribution with a mean of 0.04% per day, then form 166 complete non-overlapping blocks of 60 observations (leaving 40 draws unused) and calculate each block mean.",
)

# Accurate titles and locations for the cited regression material.
edit_source(
    "regression", "https://www.itl.nist.gov/div898/handbook/pmd/section2/pmd2.htm",
    "NIST — Underlying Assumptions for Process Modeling",
    old_label="NIST — Linear Least Squares Regression",
)
edit_source(
    "regression", "https://online.stat.psu.edu/stat501/Lesson04.html",
    "Penn State STAT 501 — Regression Inference and Prediction Intervals (Lesson 7)",
    "https://online.stat.psu.edu/stat501/Lesson07.html",
)
edit_lesson(
    "regression", "Start with a question, units and a fitted line", "body",
    "For a fuller treatment, see ‘NIST — Linear Least Squares Regression’ in the linked sources.",
    "For an introduction to fitting and interpreting a linear regression, see ‘OpenIntro Statistics — Ch. 8: Introduction to Linear Regression’ in the linked sources.",
)
edit_lesson(
    "regression", "Validate predictions on data the model did not see", "body",
    "For a fuller treatment, see ‘NIST — Linear Least Squares Regression’ in the linked sources.",
    "For residual diagnostics and validation practice, see ‘NIST — Residual Diagnostics’ in the linked sources.",
)
edit_lesson(
    "regression", "Separate mean-response uncertainty from prediction", "body",
    "‘Penn State STAT 501 — Regression’",
    "‘Penn State STAT 501 — Regression Inference and Prediction Intervals (Lesson 7)’",
)

# Remove unsupported institutional attribution; MIT is the repository's license, not publisher.
for mid in [m["id"] for m in modules]:
    replace_in_module_strings(
        mid,
        "Causal Inference for the Brave and True; MIT",
        "Causal Inference for the Brave and True; open-source handbook",
    )

# Stationarity remains cited to its actual NIST page; add the ACF/PACF identification source.
edit_source(
    "time-series", "https://www.itl.nist.gov/div898/handbook/pmc/section4/pmc442.htm",
    "NIST — Stationarity", old_label="NIST — Time Series and Autocorrelation",
)
add_source(
    "time-series", "NIST — Box-Jenkins Model Identification (ACF and PACF)",
    "https://www.itl.nist.gov/div898/handbook/pmc/section4/pmc446.htm",
)
for title in ["Choose a time scale and avoid spurious patterns", "Look for dependence in direction and magnitude"]:
    body = lesson("time-series", title)["body"]
    body = body.replace("NIST — Time Series and Autocorrelation", "NIST — Box-Jenkins Model Identification (ACF and PACF)")
    lesson("time-series", title)["body"] = body

# (1.0395)^4 − 1 is approximately 16.7%; keep the verified value unchanged.

# A Monte Carlo lecture is relevant to simulation, not to causal identification in this sentence.
edit_lesson(
    "bayesian", "Communicate Bayesian evidence responsibly", "body",
    " For a fuller treatment, see ‘MIT OCW — Analytics of Finance’ in the linked sources.",
    " For Bayesian methods and interpretation, see ‘NIST — Bayesian Methods’ in the linked sources.",
)

# Bibliographic corrections in the multiple-testing module.
edit_source(
    "backtesting", "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659",
    "Harvey, Liu & Zhu — …and the Cross-Section of Expected Returns",
    "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2249314",
)
edit_source(
    "backtesting", "https://www.stat.berkeley.edu/~hhuang/STAT141/Lecture-FDR.pdf",
    "UC Berkeley STAT C141 — Multiple Hypothesis Testing and False Discovery Rate Notes",
    old_label="Harvard — False Discovery Rate Notes",
)
edit_lesson(
    "backtesting", "Validate, stress and account for multiplicity", "body",
    "‘Harvard — False Discovery Rate Notes’",
    "‘UC Berkeley STAT C141 — Multiple Hypothesis Testing and False Discovery Rate Notes’",
)

# Distinguish expected fund-month keys from observed nonmissing values.
edit_lesson(
    "exploratory-data-analysis", "Ask what one row represents", "body",
    "First validate the key (fund, month): these three observed values are not four observations, and the blank is not 0%.",
    "First validate the key (fund, month): there are four intended fund-month keys but only three observed return values; Fund B’s February return is missing, not 0%.",
)

# Separate KDE references from regression references and state software defaults precisely.
add_source("kernel-density", "Hyndman et al. — Normal Reference Rule for Kernel Density Estimation", "https://otexts.com/weird/univariate.html")
add_source("kernel-density", "Bruce Hansen — Kernel Density Estimation (normal-reference rule)", "https://www.ssc.wisc.edu/~bhansen/709/kernel.pdf")
add_source("kernel-density", "statsmodels — KernelReg", "https://www.statsmodels.org/devel/generated/statsmodels.nonparametric.kernel_regression.KernelReg.html")
edit_lesson(
    "kernel-density", "Bandwidth is the main smoothing decision", "formula",
    "Normal-reference starting point: h ≈ 1.06 s n⁻¹ᐟ⁵",
    "Univariate Gaussian normal-reference starting point: h ≈ 1.06 s n⁻¹ᐟ⁵; software defaults vary.",
)
edit_lesson(
    "kernel-density", "Bandwidth is the main smoothing decision", "body",
    "For bandwidth context, see “Scikit-learn User Guide — Density Estimation” in the linked sources.",
    "This is a univariate normal-reference rule, not a universal optimum. Defaults vary: SciPy’s gaussian_kde uses Scott’s factor by default, and its Silverman factor is a multivariate rule rather than this exact univariate formula. For the normal-reference derivation, see “Hyndman et al. — Normal Reference Rule for Kernel Density Estimation” and “Bruce Hansen — Kernel Density Estimation (normal-reference rule)”; for SciPy’s default, see “SciPy Reference — gaussian_kde.”",
)
edit_lesson(
    "kernel-density", "Kernel regression estimates a local conditional mean", "body",
    "For implementation details, see “Scikit-learn User Guide — Density Estimation” in the linked sources.",
    "For implementation details on kernel regression, see “statsmodels — KernelReg” in the linked sources.",
)
edit_lesson(
    "kernel-density", "Local polynomials and a careful workflow", "body",
    "For density-estimation guidance, see “Scikit-learn User Guide — Density Estimation” in the linked sources.",
    "For kernel-regression implementation details, see “statsmodels — KernelReg” in the linked sources.",
)

# A pandas table-inspection guide is not a source for economic measurement definitions.
edit_lesson(
    "statistical-tools", "Make a small data dictionary", "body",
    "For a fuller treatment, see ‘pandas User Guide — 10 Minutes to pandas’ in the linked sources.",
    "For pandas table inspection and column metadata, see ‘pandas User Guide — 10 Minutes to pandas’; economic definitions must be justified from the relevant data source.",
)

# Randomized offers identify assignment/offer effects, not automatically take-up effects.
edit_lesson(
    "research-design", "Write down the question before the model", "body",
    "A randomized offer could make selection independent in expectation, whereas voluntary take-up still requires assumptions about who complies and whose outcome is measured.",
    "Random assignment makes the offer independent of potential outcomes in expectation, so the intention-to-treat effect is identified under suitable follow-up and measurement conditions. Actual take-up can remain selective; an effect of participation therefore needs additional instrumental-variable assumptions and is generally interpreted for compliers.",
)

# Difference-in-differences: heterogeneity is not itself an identifying failure under common timing.
edit_lesson(
    "difference-in-differences", "Handle policy timing and composition", "body",
    "The simple two-by-two comparison is easiest to interpret when groups adopt at the same time and treatment effects are stable.",
    "The simple two-by-two comparison is easiest to interpret when groups adopt at the same time. Treatment effects may vary across units; under parallel trends and no spillovers, the contrast can still identify an appropriate average effect for the treated.",
)

# The within transform applies to every included time-varying regressor.
edit_lesson(
    "panel-fixed-effects", "The within transformation shows what identifies a fixed-effects estimate", "formula",
    "Yᵢₜ − Ȳᵢ = β(Dᵢₜ − D̄ᵢ) + (εᵢₜ − ε̄ᵢ), before any included time-effect adjustment.",
    "Yᵢₜ − Ȳᵢ = β(Dᵢₜ − D̄ᵢ) + (Xᵢₜ − X̄ᵢ)′γ + (εᵢₜ − ε̄ᵢ), when time effects are excluded; otherwise include the demeaned period-effect term too.",
)
within_lesson = lesson("panel-fixed-effects", "The within transformation shows what identifies a fixed-effects estimate")
within_note = "Every included time-varying regressor is demeaned too; a time-invariant regressor becomes zero and is not separately identified by the within transformation."
if within_note not in within_lesson["body"]:
    within_lesson["body"] = within_lesson["body"].rstrip() + "\n\n" + within_note

# Regression coefficient units are outcome units per regressor unit, and observed outcomes are not causal effects.
edit_lesson(
    "robust-clustered-inference", "Uncertainty follows the data-generating design", "body",
    "Robust standard errors change the estimated uncertainty, not the fitted relationship. Illustrative synthetic example: suppose a regression estimates that one additional hour of weekly training is associated with $18 more weekly earnings, and the conventional standard error is $4 per hour while the heteroskedasticity-robust standard error is $6 per hour. The coefficient remains $18 per hour; a rough 95% interval changes from $18 ± 1.96×$4 = $18 ± $7.84, or $10.16 to $25.84 per hour, to $18 ± 1.96×$6 = $18 ± $11.76, or $6.24 to $29.76 per hour. These are earnings units, not percentage points. Robustness does not remove omitted-variable bias, reverse causality, or small-sample problems. For a fuller treatment, see ‘Wooldridge — Econometric Analysis of Cross Section and Panel Data (MIT Press)’ in the linked sources.",
    "Robust standard errors change the estimated uncertainty, not the fitted relationship. Illustrative synthetic example: suppose a regression estimates that one additional weekly training hour is associated with $18 in weekly earnings; the conventional standard error is $4 and the heteroskedasticity-robust standard error is $6, each measured in weekly-earnings dollars per additional training hour. The coefficient remains $18 in those same slope units. A rough 95% interval changes from $18 ± 1.96×$4 = $18 ± $7.84, or $10.16 to $25.84 in weekly-earnings dollars per additional training hour, to $18 ± 1.96×$6 = $18 ± $11.76, or $6.24 to $29.76 in the same units. These intervals describe an association, not a causal training effect. Robustness does not remove omitted-variable bias, reverse causality, or small-sample problems. For a fuller treatment, see ‘Wooldridge — Econometric Analysis of Cross Section and Panel Data (MIT Press)’ in the linked sources.",
)
edit_lesson(
    "robust-clustered-inference", "Few clusters need extra care", "body",
    "clinic effects, in percentage points, are",
    "clinic-level outcome changes, in percentage points, are",
)

# The propensity-score chapter, rather than the cited regression chapter, supports this weighting paragraph.
edit_lesson(
    "matching-weighting", "Weighting choices define which population the contrast describes", "body",
    "For a fuller treatment, see ‘Angrist & Pischke (2008), Mostly Harmless Econometrics, Ch. 3, §§3.3.1–3.3.3, 3.4.1’ in the linked sources.",
    "For propensity-score weighting, overlap, and the role of extreme weights, see ‘Matheus Facure — Ch. 11: Propensity Scores (Causal Inference for the Brave and True; open-source handbook)’ in the linked sources.",
)

# Correct the placebo ranking percentage (3/4 = 75%).
edit_lesson(
    "synthetic-control", "Use placebos as a reference, not a magic test", "body",
    "Three of four placebo gaps are smaller than 12, so the treated gap ranks fourth among five units, or 80% of the gaps are smaller.",
    "Three of four placebo gaps are smaller than 12, so the treated gap ranks fourth among five units; 75% of the placebo gaps are smaller.",
)

# Cite an FDR source for multiplicity, not the CATE chapter.
add_source(
    "heterogeneous-effects", "UC Berkeley STAT C141 — Multiple Hypothesis Testing and False Discovery Rate Notes",
    "https://www.stat.berkeley.edu/~hhuang/STAT141/Lecture-FDR.pdf",
)
edit_lesson(
    "heterogeneous-effects", "Keep discovery and confirmation distinct", "body",
    "For a fuller treatment, see “Matheus Facure — Ch. 18: Heterogeneous Treatment Effects (Causal Inference for the Brave and True; open-source handbook)” in the linked sources.",
    "For multiple-testing and false-discovery-rate context, see “UC Berkeley STAT C141 — Multiple Hypothesis Testing and False Discovery Rate Notes” in the linked sources.",
)

# Make the within- and between-office arithmetic internally consistent.
edit_lesson(
    "multilevel-partial-pooling", "Why a group label can matter", "body",
    "Separate a within-group contrast from a between-group contrast: if two synthetic job centres each have wages of £20 and £24 per hour, the within-centre difference is £4 per hour; if their centre averages are £22 and £28 per hour, the between-centre difference is £6 per hour.",
    "Separate within-office from between-office comparisons. Suppose Office A pays £20 and £24 per hour and Office B pays £26 and £30. The within-office range is £4 in each office, while the difference in office means is £28 − £22 = £6 per hour.",
)

# Correct the hand calculation and use model-specific sources for spatial regression.
spatial = lesson("spatial-dependence-regional-econometrics", "Spatial lag and spatial error tell different stories")
spatial["body"] = replace_once(
    spatial["body"],
    "The resulting spatial lags are (−0.5, 0, 0, 0.5). Using the same row-normalized convention as the lab, the numerator is Σzᵢ(Wz)ᵢ = (−1)(−0.5) + (−0.5)(0) + (0.5)(0) + (1)(0.5) = 1. The denominator is Σzᵢ² = 1 + 0.25 + 0.25 + 1 = 2.5, so the Moran-style ratio is 1/2.5 = 0.40.",
    "The resulting spatial lags are (−0.5, −0.25, 0.25, 0.5). Using the same row-normalized convention as the lab, the numerator is Σzᵢ(Wz)ᵢ = (−1)(−0.5) + (−0.5)(−0.25) + (0.5)(0.25) + (1)(0.5) = 1.25. The denominator is Σzᵢ² = 1 + 0.25 + 0.25 + 1 = 2.5, so the Moran-style ratio is 1.25/2.5 = 0.50.",
    "spatial Moran-style hand calculation",
)
edit_lesson(
    "spatial-dependence-regional-econometrics", "Spatial lag and spatial error tell different stories", "body",
    "For a fuller treatment, see ‘PySAL esda — Global Spatial Autocorrelation with Moran’s I’ in the linked sources.",
    "For spatial-lag IV estimation and spatial-error models, see ‘PySAL spreg — Spatial Lag IV Estimation’ and ‘PySAL spreg — Spatial Error ML Estimation’; the esda source below supports the Moran-style calculation.",
)
add_source("spatial-dependence-regional-econometrics", "PySAL spreg — Spatial Lag IV Estimation", "https://pysal.org/spreg/notebooks/14_IV_estimation_spatial_lag.html")
add_source("spatial-dependence-regional-econometrics", "PySAL spreg — Spatial Error ML Estimation", "https://pysal.org/spreg/notebooks/15_ML_estimation_spatial_error.html")

# Correct an arithmetic rounding error under the stated classical measurement-error assumptions.
edit_lesson(
    "measurement-error-economics", "Classical predictor error can flatten a slope", "body",
    "the expected slope using the noisy hours measure would be about 0.692 × £40 = £27.70.",
    "the expected slope using the noisy hours measure would be (9/13) × £40 = £27.69, approximately.",
)

# The incorrect price-index equivalence was not present in the current generated lesson; guard against its return.
price_lesson = lesson("price-indices-real-values", "Understand the base and the weights")
if "1.0417/1.0560" in price_lesson.get("body", ""):
    raise SystemExit("Unexpected stale price-index equivalence returned; review before applying an automatic patch")

# Explain coefficient-scale dependence of ridge and lasso penalties correctly.
edit_lesson(
    "regularization-cross-validation", "What Ridge and LASSO penalties change", "body",
    "Otherwise the penalty treats a one-unit change in income and a one-unit change in a tiny-rate variable as if their scales were comparable.",
    "Otherwise the penalty acts on coefficients expressed in different units, so an equivalent economic effect can receive different shrinkage solely because one predictor is measured in dollars and another in a small rate. Standardize continuous predictors using training data only so the penalty operates on comparable predictor scales.",
)

# Distinguish raw from normalized random-effects weights.
edit_lesson(
    "meta-analysis-evidence-synthesis", "Allow effects to vary across settings", "body",
    "When τ² is larger, weights become more balanced, so small studies can contribute more than under a fixed-effect model.",
    "When τ² is larger, normalized weights become more balanced: a small or imprecise study can receive a larger share of the pooled mean than under fixed-effect weighting, although adding τ² reduces every study’s raw inverse-variance weight.",
)

# Name the scale of mediation sensitivity parameters and distinguish the lab's slope-scale u.
edit_lesson(
    "causal-mediation-mechanisms", "Use sensitivity analysis and report the limits", "body",
    "Sensitivity analysis can be shown with hypothetical scenarios. Suppose an illustrative synthetic analysis estimates an indirect effect of 4 percentage points when the mediator–outcome bias parameter is 0. If a chosen scenario subtracts 1.5 percentage points of bias, the adjusted illustrative value is 4 − 1.5 = 2.5 percentage points; a stronger scenario subtracting 4 points gives 0 percentage points. These are not observed data or discoveries about a real confounder. Report the parameter’s meaning, units, range, and whether the total effect changes. A pathway that reaches zero under a plausible scenario is assumption-sensitive, while a stable total effect does not validate that pathway. Sensitivity analysis cannot identify the hidden variable or prove robustness beyond the scenarios examined. For a fuller treatment, see ‘Imai, Keele & Yamamoto (2010) — Identification, Inference and Sensitivity Analysis for Causal Mediation Effects’ in the linked sources.",
    "Sensitivity analysis can be shown with explicitly defined hypothetical parameters. Suppose an illustrative synthetic analysis estimates an indirect effect of 4 percentage points at u = 0. If a separate scenario parameter u_ind is defined directly on the indirect-effect scale, setting u_ind = 1.5 percentage points gives 4 − 1.5 = 2.5 percentage points; u_ind = 4 gives zero. This is not the lab’s u: the lab defines u on the mediator–outcome slope scale and adjusts the indirect effect through a(b − u). Do not subtract a slope-scale u directly from an indirect effect. These are hypothetical values, not observed data or discoveries about a real confounder. Report the parameter’s meaning, units, range, and whether the total effect changes. A pathway that reaches zero under a plausible scenario is assumption-sensitive; sensitivity analysis cannot identify the hidden variable or prove robustness beyond the scenarios examined. For a fuller treatment, see ‘Imai, Keele & Yamamoto (2010) — Identification, Inference and Sensitivity Analysis for Causal Mediation Effects’ in the linked sources.",
)

# Missing-outcome bounds for randomized offers refer to the ITT effect, not necessarily treatment receipt.
edit_lesson(
    "partial-identification-bounds", "Derive worst-case bounds for missing binary outcomes", "body",
    "Therefore the six-month effect, in employment-probability units, lies between 0.63 − 0.68 = −0.05 and 0.73 − 0.48 = 0.25: from 5 percentage points lower to 25 points higher.",
    "Therefore the six-month intention-to-treat effect of being offered the course, in employment-probability units, lies between 0.63 − 0.68 = −0.05 and 0.73 − 0.48 = 0.25: from 5 percentage points lower to 25 points higher. If not everyone offered the course participates, these are not bounds on the effect of attending; that estimand requires additional compliance assumptions.",
)
edit_lesson(
    "partial-identification-bounds", "Derive worst-case bounds for missing binary outcomes", "body",
    "it does not establish whether the course helped or harmed.",
    "it does not establish whether the offer improved or worsened employment.",
)

# Preserve all curriculum structure after patching.
if len(modules) != 42 or sum(len(m.get("lessons", [])) for m in modules) != 238:
    raise SystemExit("A curriculum patch unexpectedly changed the module/lesson count")
MODULES_PATH.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n")
print(f"Applied {changed} verified curriculum/source text corrections; kept 42 modules and 238 lessons.")
