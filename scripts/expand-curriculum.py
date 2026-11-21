#!/usr/bin/env python3
"""Merge the authored applied-economics curriculum into the bundled module data."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES_PATH = ROOT / "src/data/modules.json"
modules = json.loads(MODULES_PATH.read_text())
by_id = {module["id"]: module for module in modules}

# Broaden the existing course without removing its original modules, lessons, visuals or media.
existing_categories = {
    "statistical-thinking": "Foundations", "probability": "Foundations",
    "distributions": "Foundations", "correlation": "Foundations",
    "estimation": "Inference & Research", "p-values": "Inference & Research",
    "causal": "Inference & Research", "regression": "Applied Econometrics",
    "time-series": "Economic Applications", "returns-risk": "Economic Applications",
    "portfolio": "Economic Applications", "bayesian": "Modelling",
    "backtesting": "Economic Applications", "exploratory-data-analysis": "Data & Tools",
    "kernel-density": "Modelling", "statistical-tools": "Data & Tools",
}
for module_id, category in existing_categories.items():
    if module_id in by_id:
        by_id[module_id]["category"] = category

renames = {
    "probability": ("Probability, Sampling & Economic Data", "Use probability and sampling to reason about uncertainty in surveys, policies and economic outcomes."),
    "regression": ("Regression for Economic Questions", "Read a regression as a model of conditional averages; learn what it can say about association, prediction and—only with a credible design—causation."),
    "time-series": ("Economic Time Series & Market Data", "Explore trends, persistence, changing volatility and forecasting in economic and financial time series."),
    "returns-risk": ("Measuring Returns & Risk: A Finance Application", "Use market returns as one practical setting for learning about variation, compounding and risk summaries."),
    "portfolio": ("Diversification & Portfolio Risk: A Finance Application", "Study covariance and diversification through portfolios, then carry the same statistical ideas to broader economic data."),
}
for module_id, (title, excerpt) in renames.items():
    if module_id in by_id:
        by_id[module_id]["title"] = title
        by_id[module_id]["excerpt"] = excerpt


def lesson(title, body, takeaway, formula=None, practice=None):
    result = {"title": title, "body": body, "takeaway": takeaway}
    if formula:
        result["formula"] = formula
    if practice:
        result["practice"] = practice
    return result


def module(id, title, category, level, minutes, lab, excerpt, objectives, lessons,
           case_study, misconceptions, sources, quiz):
    return {
        "id": id, "slug": id, "title": title, "category": category,
        "level": level, "minutes": minutes, "lab": lab, "excerpt": excerpt,
        "objectives": objectives, "lessons": lessons, "caseStudy": case_study,
        "misconceptions": misconceptions, "sources": sources, "quiz": quiz,
    }

MHE = {"label": "Angrist & Pischke — Mostly Harmless Econometrics (Princeton University Press)", "url": "https://press.princeton.edu/books/paperback/9780691120355/mostly-harmless-econometrics"}
MHE_SITE = {"label": "Mostly Harmless Econometrics — authors’ site and resources", "url": "https://www.mostlyharmlesseconometrics.com/"}
METRICS = {"label": "Angrist & Pischke — Mastering ’Metrics (Princeton University Press)", "url": "https://press.princeton.edu/books/paperback/9780691152844/mastering-metrics"}
WOOLDRIDGE = {"label": "Wooldridge — Introductory Econometrics (Cengage)", "url": "https://faculty.cengage.com/works/9780357900161"}
STOCK = {"label": "Stock & Watson — Introduction to Econometrics, 4th edition (Pearson)", "url": "https://www.pearson.com/en-us/subject-catalog/p/introduction-to-econometrics/P200000006421/9780136879787"}
MIXTAPE = {"label": "Cunningham — Causal Inference: The Mixtape (Yale University Press)", "url": "https://yalebooks.yale.edu/book/9780300251685/causal-inference"}
MIXTAPE_OPEN = {"label": "Causal Inference: The Mixtape — open first-edition text", "url": "https://mixtape-1ed.netlify.app/"}
WHATIF = {"label": "Hernán & Robins — Causal Inference: What If (authors’ open book)", "url": "https://miguelhernan.org/whatifbook"}
CAMERON = {"label": "Cameron & Trivedi — Microeconometrics: Methods and Applications (Cambridge University Press)", "url": "https://www.cambridge.org/highereducation/books/microeconometrics/982158DE989697607C858068ED05C7B1"}
ROS = {"label": "Gelman, Hill & Vehtari — Regression and Other Stories (Cambridge University Press)", "url": "https://www.cambridge.org/highereducation/books/regression-and-other-stories/DD20DD6C9057118581076E54E40C372C"}
ROS_SITE = {"label": "Regression and Other Stories — authors’ book site", "url": "https://sites.stat.columbia.edu/gelman/regression/"}
PANEL = {"label": "Wooldridge — Econometric Analysis of Cross Section and Panel Data (MIT Press)", "url": "https://mitpress.mit.edu/9780262232586/econometric-analysis-of-cross-section-and-panel-data/"}
WHATIF_FREE_TEXT = {"label": "Causal Inference: What If — free online text", "url": "https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/"}

new_modules = [
module(
    "research-design", "From Research Question to Credible Estimate", "Inference & Research", "Beginner", 32, "eda",
    "Turn an economic question into a defined outcome, comparison, estimand and defensible research design before opening a regression table.",
    ["State a target population, outcome, treatment and time horizon.", "Distinguish a descriptive contrast from a causal effect.", "Choose a design and list its identifying assumptions before estimating."],
    [
        lesson("Write down the question before the model", "Suppose a city offers a job-training programme and wants to know whether it raises participants’ earnings one year later. Define who is eligible, what counts as participation, which earnings measure is used, and the follow-up date. These choices define the population, treatment and outcome. A vague question such as ‘does training work?’ cannot be answered by one coefficient until those details are made explicit.", "A precise estimand starts with a population, intervention, outcome and time horizon.", practice={"question":"A report compares average earnings of graduates and non-graduates. What is missing before calling the difference a programme effect?", "hint":"Ask whether the two groups would have had the same outcomes without the programme.", "solution":"The comparison lacks a defensible counterfactual design. Eligibility, selection into training, baseline differences and the causal estimand must be specified."}),
        lesson("Name the counterfactual", "For each eligible person, imagine two potential outcomes: earnings if they participate and earnings if they do not. Only one is observed for that person, so the unobserved alternative is the counterfactual. An average treatment effect compares the mean of these potential outcomes in a stated target population. The gap between treated and untreated people is not automatically that effect when participation is selective.", "Causal inference is a comparison with an unobserved alternative, not merely a difference between observed groups.", "ATE = E[Y(1) − Y(0)]; Y(1) and Y(0) are potential outcomes under treatment and no treatment."),
        lesson("Choose an identification strategy", "A randomized offer, a policy threshold, an external instrument, or a well-supported comparison over time can create different routes to a counterfactual. Each design answers a somewhat different question and needs its own assumptions. Random assignment supports a direct comparison on average; an instrument or threshold often identifies an effect for a narrower group near the source of variation.", "Pick a design because of how treatment varies, not because a particular estimator is familiar."),
        lesson("Pre-specify checks and communicate scope", "Before interpreting estimates, record the data source, sample rules, comparison group, outcome construction, uncertainty method and planned sensitivity checks. Ask what could violate the design: selective take-up, anticipation, spillovers, measurement changes or a policy concurrent with treatment. Report the population and period to which the result applies. A careful estimate can be useful even when it does not generalize everywhere.", "Transparent design choices make a result easier to challenge, reproduce and use responsibly."),
    ],
    "A local authority evaluates a voluntary employment programme. The first task is to define an eligible population and earnings outcome, then map how the offer and take-up occurred. The comparison design—not a significance threshold—determines what effect can be defended.",
    ["A regression adjustment does not create random assignment.", "A statistically precise estimate can still target the wrong population or outcome.", "An estimate from one design need not apply to people far from its comparison group."],
    [MHE, METRICS, MIXTAPE, WHATIF],
    {"question":"What should be made explicit before estimating a policy effect?", "options":["The target population, treatment, outcome and comparison design", "Only the largest available sample", "The preferred significance threshold"], "answerIndex":0, "explanation":"These define the estimand and the counterfactual comparison. Sample size and a p-value cannot repair an undefined question or weak design."}
),
module(
    "experimental-design", "Randomized Experiments & Policy Trials", "Applied Econometrics", "Beginner", 30, "causal",
    "Learn how randomized offers create comparable groups, how non-compliance changes the question, and why trial results still need careful interpretation.",
    ["Explain random assignment and the role of a control group.", "Separate intention-to-treat from effects of actual participation.", "Check attrition, spillovers, balance and external validity."],
    [
        lesson("Random assignment builds a comparison", "When eligible units are randomly assigned to an offer, treatment status is independent of their potential outcomes on average across repeated assignments. The control group estimates what would have happened to the offered group in expectation. Randomization does not guarantee identical groups in one realized sample, so baseline differences should be described without treating a balance table as proof that the lottery was implemented correctly.", "Randomization is a design feature that supports comparability in expectation."),
        lesson("Estimate the effect of the offer first", "If some people decline the offer and some controls obtain similar services elsewhere, assignment no longer equals receipt. The intention-to-treat effect compares outcomes by original assignment and preserves the lottery. It answers the effect of offering access under the observed take-up pattern, which is often directly relevant to policy design.", "Keep assignment as assigned when estimating the intention-to-treat contrast."),
        lesson("Non-compliance changes the estimand", "The treatment-on-the-treated is not obtained by simply comparing those who took part with those who did not, because take-up may be related to motivation, health or expected earnings. Under additional assumptions, randomized assignment can instrument for participation and identify a local effect for people whose take-up responds to the offer. The assumptions and target group should be stated, not hidden behind the estimator name.", "Actual participation effects require more assumptions than the randomized offer effect."),
        lesson("Audit what happened after assignment", "Track outcomes for all assigned units, compare attrition by group, look for spillovers and verify that outcomes were measured consistently. Selective missing follow-up can undo the comparability created by randomization. Report the study setting, eligible population and implementation details because a valid trial in one place is not automatically a forecast for another setting.", "A clean lottery is valuable, but follow-up and implementation still matter."),
    ],
    "A district randomly offers a limited number of tutoring places. Report the effect of the offer on test outcomes first; if participation differs, use assignment as an instrument only when the required assumptions and target population are defensible.",
    ["Randomized groups need not look exactly alike in a small sample.", "Comparing participants with non-participants does not preserve random assignment.", "A valid trial does not guarantee the same effect in a different population."],
    [METRICS, MHE, STOCK, WHATIF],
    {"question":"When take-up is incomplete, which comparison keeps the original random assignment intact?", "options":["Compare outcomes by the initial offer assignment", "Compare participants with everyone who did not participate", "Drop people who did not comply"], "answerIndex":0, "explanation":"The intention-to-treat comparison follows original assignment. Conditioning on take-up can reintroduce selection."}
),
module(
    "iv-2sls", "Instrumental Variables & Two-Stage Least Squares", "Applied Econometrics", "Intermediate", 38, "causal",
    "Use external sources of variation to study endogeneity, then check relevance, exclusion and who an IV estimate describes.",
    ["Explain why endogenous regressors bias ordinary least squares.", "State the relevance, independence and exclusion conditions for an instrument.", "Interpret a 2SLS estimate and diagnose weak-instrument risks."],
    [
        lesson("Why ordinary regression may fail", "Suppose schooling and wages are related, but unobserved ability affects both. A regression of wages on schooling mixes the return to schooling with this omitted factor. Measurement error or reverse causation can also make a regressor correlated with the regression error. An instrument is a proposed source of variation in schooling that is not itself carrying those other influences into wages.", "An instrument is useful only when its variation isolates the causal change of interest."),
        lesson("Three conditions shape the argument", "Relevance means the instrument predicts treatment. Independence says the instrument is unrelated to unobserved determinants of the outcome, given the design and controls. Exclusion says the instrument affects the outcome only through the treatment being instrumented. These are substantive claims about institutions and behaviour; no regression output can prove exclusion by itself.", "A strong first stage is necessary, but it is not evidence for exclusion on its own."),
        lesson("Read two-stage least squares", "The first stage predicts the endogenous treatment using the instrument and allowed controls. The second stage relates the outcome to the predicted treatment. In a simple just-identified setting, the estimate is the reduced-form effect of the instrument on the outcome divided by its first-stage effect on treatment. In designs with non-compliance, the estimate can describe a local average effect for compliers under additional assumptions.", "2SLS uses instrument-driven treatment variation, not all observed treatment variation.", "β̂_IV = Cov(Z,Y) / Cov(Z,D) in a simple just-identified model; Z is the instrument, D treatment and Y outcome."),
        lesson("Check strength and scope", "A weak first stage makes IV estimates unstable and conventional uncertainty summaries unreliable. Report the first-stage relationship, weak-instrument diagnostics appropriate to the design, reduced form, confidence interval and sensitivity to controls. Explain the complier group or other target population. A plausible instrument in one institution may not identify a population-wide effect.", "Instrument credibility depends on the design story as well as first-stage statistics."),
    ],
    "A school-leaving-age reform may shift education for some cohorts. Before using it as an instrument for schooling, check whether cohorts faced other changes that affect wages directly and describe the group whose education responds to the reform.",
    ["A high first-stage statistic does not establish the exclusion restriction.", "An IV estimate may be local to people whose treatment changes because of the instrument.", "2SLS does not automatically fix all omitted variables or poor measurement."],
    [MHE, METRICS, MIXTAPE_OPEN, WOOLDRIDGE, PANEL],
    {"question":"Which IV condition says the instrument affects the outcome only through the endogenous treatment?", "options":["Relevance", "Exclusion", "A large sample"], "answerIndex":1, "explanation":"Exclusion is the substantive no-direct-effect condition. Relevance concerns prediction of treatment."}
),
module(
    "difference-in-differences", "Difference-in-Differences & Event Studies", "Applied Econometrics", "Intermediate", 38, "regression",
    "Compare outcome changes in treated and comparison groups, inspect pre-policy patterns, and avoid overclaiming from an event-study plot.",
    ["Calculate a two-period difference-in-differences contrast.", "Explain the parallel-trends assumption and event-study diagnostics.", "Recognize spillovers, changing composition and staggered-adoption complications."],
    [
        lesson("Take a difference in each group", "Imagine one region adopts a wage subsidy while a similar region does not. First calculate each region’s change from before to after the policy. Then subtract the comparison region’s change from the treated region’s change. This removes stable group differences and common time shocks only if the remaining comparison is credible.", "Difference-in-differences subtracts a before–after change in the comparison group from the treated group."),
        lesson("The key assumption concerns untreated trends", "Parallel trends says that, without the policy, the treated and comparison groups would have followed the same average outcome trend over the study period. It does not require their outcome levels to be equal. Several pre-policy periods can reveal some differences in trends or anticipation, but a visually flat pre-period is not proof of the unobserved post-policy counterfactual.", "The identifying claim is about a counterfactual trend, not equality of group averages."),
        lesson("Use event time with care", "An event-study model can display estimates for periods before and after treatment relative to a chosen baseline. Pre-treatment estimates are useful diagnostics; post-treatment estimates show timing and persistence. Be explicit about the omitted reference period, group composition and uncertainty. Looking at many pre-period coefficients and selecting only favourable results can mislead, so pair the graph with a design explanation.", "An event-study graph is a diagnostic and summary, not a substitute for the parallel-trends argument."),
        lesson("Handle policy timing and composition", "The simple two-by-two comparison is easiest to interpret when groups adopt at the same time and treatment effects are stable. With staggered adoption and heterogeneous effects, some conventional two-way fixed-effects event-study coefficients can compare already-treated units with newly treated units in unintuitive ways. Use estimators designed for the adoption pattern, report cohort and time support, and examine spillovers or changes in sample composition.", "Staggered timing can make a familiar regression coefficient combine comparisons that do not match the intended policy effect.", "DiD = (Ȳ_T,after − Ȳ_T,before) − (Ȳ_C,after − Ȳ_C,before)."),
    ],
    "To study a city transit fare change, compare ridership changes with a similar city over the same dates. Check pre-policy trends, simultaneous transport changes, spillovers across city borders and whether the chosen modern estimator matches the adoption pattern.",
    ["Parallel trends does not mean equal outcome levels.", "A non-significant pre-trend test does not prove parallel trends.", "A standard two-way fixed-effects event study can be misleading under staggered adoption and heterogeneous effects."],
    [MHE, METRICS, MIXTAPE, MIXTAPE_OPEN, STOCK],
    {"question":"What does the parallel-trends assumption concern?", "options":["Treated and comparison groups have identical outcome levels", "Their untreated outcomes would have changed by the same average amount", "The treatment has the same effect for every unit"], "answerIndex":1, "explanation":"DiD needs comparable untreated trends, not identical levels or constant treatment effects."}
),
module(
    "regression-discontinuity", "Regression Discontinuity Designs", "Applied Econometrics", "Intermediate", 36, "regression",
    "Use a policy eligibility threshold to compare units just above and below the cutoff, while checking manipulation and local scope.",
    ["Distinguish sharp and fuzzy regression discontinuity.", "Explain continuity and no-precise-manipulation assumptions.", "Interpret local estimates and test sensitivity to bandwidth and specification."],
    [
        lesson("A threshold can create a local comparison", "Suppose a training grant is offered when a score reaches 70. People scoring 69.8 and 70.2 may be similar in many ways, while their probability of receiving the grant changes at the rule. A discontinuity in outcomes at 70 can be attributed to the offer only if other determinants of outcomes do not also jump there and units cannot precisely sort around the cutoff.", "RD compares observations close to a threshold where treatment probability changes."),
        lesson("Sharp and fuzzy assignment differ", "In a sharp design, everyone on one side receives treatment and everyone on the other side does not. In a fuzzy design, crossing the threshold changes the chance of treatment but does not determine it perfectly. The fuzzy design uses threshold eligibility as an instrument for actual treatment and inherits the additional IV conditions. State whether the target is the effect of eligibility or treatment receipt.", "The assignment rule determines which RD estimand and assumptions apply."),
        lesson("Choose the local window responsibly", "The estimate can change with the bandwidth, polynomial order and weighting near the cutoff. Show the score-outcome relationship on both sides, use transparent and restrained functional forms, and report sensitivity across reasonable bandwidths. A very wide window may rely on distant comparisons; a very narrow one may be imprecise. These choices should be motivated rather than selected for a preferred result.", "Bandwidth analysis reveals the trade-off between locality and precision."),
        lesson("Probe the threshold story", "Check whether the running variable bunches at the cutoff, whether baseline covariates jump, whether outcomes change at placebo thresholds and whether another policy uses the same rule. These checks can expose threats but cannot prove that no unobserved factor changes at the cutoff. The estimate is local to units near the threshold and need not represent everyone eligible for the policy.", "RD is persuasive when institutional details support a clean local comparison."),
    ],
    "A scholarship is assigned to applicants with a score above a published threshold. Compare applicants near the cutoff, inspect score manipulation and baseline discontinuities, and describe the estimate as a local effect around that score.",
    ["An RD estimate is usually local to the cutoff, not a whole-population average.", "A plot that looks smooth cannot verify every continuity assumption.", "In fuzzy RD, eligibility and actual treatment are not interchangeable."],
    [MHE, METRICS, MIXTAPE, MIXTAPE_OPEN, WOOLDRIDGE],
    {"question":"What population does a conventional RD estimate most directly describe?", "options":["Units near the assignment threshold", "Every unit in the country", "Only units with the largest outcome"], "answerIndex":0, "explanation":"The design compares observations locally around the cutoff; broad extrapolation needs additional assumptions."}
),
module(
    "panel-fixed-effects", "Panel Data, Fixed Effects & First Differences", "Applied Econometrics", "Intermediate", 36, "regression",
    "Use repeated observations on people, firms or regions to control for stable unobserved differences and study change over time.",
    ["Identify the unit and time dimensions of panel data.", "Interpret entity and time fixed effects.", "Recognize time-varying confounding and the need to cluster dependence appropriately."],
    [
        lesson("Follow the same units over time", "A panel follows the same people, firms, schools or regions across multiple periods. Repeated observations let an analyst distinguish persistent differences between units from changes within a unit. The data structure also creates dependence: observations from one unit often share unobserved factors across time, so ordinary independent-observation formulas may understate uncertainty.", "Panel data add a within-unit time dimension; they do not automatically solve endogeneity."),
        lesson("Entity fixed effects remove stable differences", "An entity fixed-effects model allows each unit to have its own constant baseline. This absorbs characteristics that do not change over the observed period, such as persistent geography or a stable historical legacy. It cannot remove a time-varying confounder that changes alongside treatment, and it cannot estimate effects of variables that never vary within a unit.", "Fixed effects control for time-invariant unit attributes, not every unobserved cause."),
        lesson("Time effects capture common shocks", "Adding time fixed effects absorbs shocks shared across units in a period, such as a national business-cycle change. With both entity and time effects, treatment effects are identified from remaining within-unit changes relative to common period shifts. The analyst still needs a credible comparison and should inspect whether treatment timing tracks other changing local conditions.", "Two-way fixed effects remove stable unit differences and common time shocks under the model."),
        lesson("First differences and design limits", "With two periods, subtracting the first observation from the second removes the unit’s stable baseline and is closely related to an entity fixed-effects estimate. With more periods, the exact relationship depends on the model and assumptions. Track attrition, changing definitions, anticipation, treatment reversals and serial dependence. A panel is not automatically a natural experiment.", "Repeated measures help describe change, but causal interpretation still rests on design assumptions.", "Yᵢₜ = αᵢ + λₜ + βDᵢₜ + Xᵢₜ′γ + εᵢₜ; αᵢ is the unit effect and λₜ the time effect."),
    ],
    "A panel of municipalities records employment before and after a public-transport expansion. Municipality effects absorb stable local traits and year effects absorb shared shocks, but changing industry mix or targeted investment may still confound the comparison.",
    ["Fixed effects do not control for unobserved factors that change over time.", "A unit fixed effect does not identify the coefficient of a time-invariant regressor.", "Panel structure alone does not justify a causal claim."],
    [PANEL, WOOLDRIDGE, MHE, STOCK],
    {"question":"What does a unit fixed effect absorb?", "options":["All possible time-varying confounding", "Stable unit-specific factors", "Common shocks in every period"], "answerIndex":1, "explanation":"Unit fixed effects absorb stable unit-specific characteristics. Time fixed effects address common period shocks."}
),
module(
    "robust-clustered-inference", "Robust, Clustered & Design-Based Inference", "Inference & Research", "Intermediate", 34, "confidence",
    "Match uncertainty estimates to how observations were sampled, assigned and correlated rather than selecting a standard error by habit.",
    ["Distinguish heteroskedasticity-robust from cluster-robust standard errors.", "Choose clustering levels based on assignment and dependence.", "Explain small-cluster limits and design-based randomization inference."],
    [
        lesson("Uncertainty follows the data-generating design", "A coefficient estimate summarizes a sample, and its uncertainty depends on how observations could vary across repeated samples or assignments. If outcome noise changes with income or firm size, homoskedastic formulas may be inappropriate. Heteroskedasticity-robust standard errors adjust the variance calculation without changing the fitted coefficient, subject to large-sample conditions.", "Robust inference is about uncertainty calculations, not a repair for a biased design."),
        lesson("Cluster where outcomes can move together", "If a policy is assigned by school district, outcomes for pupils in one district can share shocks. Treating every pupil as independent may overstate information. Cluster-robust uncertainty often groups observations at the level of assignment or a justified dependence structure. The number of clusters—not just the number of rows—matters for accuracy.", "The cluster level should reflect the assignment and dependence process, not whichever choice produces a smaller p-value."),
        lesson("Few clusters need extra care", "Cluster-robust variance estimates can perform poorly when the number of independent clusters is small, especially with unbalanced group sizes or high-leverage clusters. Report cluster counts and consider appropriate small-sample corrections, randomization-based inference or a wild cluster bootstrap where justified. No correction can create independent assignment units that the design did not provide.", "Thousands of observations within a handful of clusters are not thousands of independent policy assignments."),
        lesson("Use the design to guide inference", "In a randomized study, randomization inference can evaluate how the estimate would vary under the assignment mechanism, if that mechanism is known and the null is clearly stated. In observational studies, inference must also acknowledge model uncertainty and identification assumptions. State the estimator, variance method, clustering level and limitations together.", "The uncertainty method should be chosen before inspecting which one gives the preferred conclusion."),
    ],
    "A minimum-wage policy changes at the state level, while a dataset contains many workers per state. The analysis should explain why states are the assignment units and how the limited number of states affects precision.",
    ["Robust standard errors do not correct omitted-variable bias or poor measurement.", "Clustering by an arbitrary variable is not a universal safeguard.", "A large row count cannot compensate for very few independent clusters."],
    [MHE, PANEL, CAMERON, STOCK],
    {"question":"If a policy is assigned to districts and outcomes share district shocks, what is a natural starting point for cluster-robust uncertainty?", "options":["Cluster at the district level, then assess whether the number of districts supports the method", "Treat every individual as independent", "Cluster at a level chosen to minimize the p-value"], "answerIndex":0, "explanation":"Assignment and dependence motivate the cluster level; few clusters still require careful inference."}
),
module(
    "matching-weighting", "Matching, Weighting & Propensity Scores", "Applied Econometrics", "Intermediate", 36, "causal",
    "Construct comparable groups using measured covariates, assess overlap, and make the untestable no-unmeasured-confounding assumption explicit.",
    ["Define propensity scores and common support.", "Use matching or weighting to balance observed covariates.", "Explain why balance cannot rule out unmeasured confounding."],
    [
        lesson("Compare units with similar observed histories", "If people choose whether to join a job programme, participants may differ from non-participants before treatment. Matching pairs or weighting can make the measured covariate distributions more similar, such as age, education and prior earnings. The causal interpretation still requires that these measured variables capture all confounding needed for the comparison.", "Matching and weighting balance observed information; they do not randomize treatment."),
        lesson("The propensity score is a balancing summary", "The propensity score is the probability of treatment given observed pre-treatment covariates. Under suitable conditions, conditioning on it can balance those measured covariates between treatment groups. Estimate it using variables measured before treatment and based on substantive knowledge; including post-treatment outcomes or mediators can introduce bias.", "A propensity score is a model for treatment assignment, not a probability that the causal claim is true."),
        lesson("Check overlap and balance", "After matching or weighting, inspect standardized differences and distribution plots for each important covariate. Check whether treated units have plausible comparison units and whether weights become extreme. Limited overlap means the data provide weak support for comparisons in some regions; trimming changes the target population and should be reported.", "A good balance diagnostic is necessary for the observed covariates, but not sufficient for identification."),
        lesson("State the assumptions and target", "A weighted estimate may target the average effect for all eligible units, for treated units, or another population depending on the weights. State that target and the conditional-exchangeability assumption: after adjusting for measured covariates, there are no remaining common causes of treatment and outcome. Use sensitivity analysis to show how hidden confounding could change conclusions.", "The target population and no-unmeasured-confounding assumption belong beside the estimate."),
    ],
    "To assess a housing voucher pilot, balance pre-program income, household composition and prior housing instability. Report overlap and the population the weights represent; unmeasured differences in application motivation may remain.",
    ["A balanced table does not prove the absence of hidden confounding.", "The propensity score is not itself an outcome model or a causal effect.", "Extreme weights can make an estimate unstable and change its effective target."],
    [MIXTAPE, WHATIF, MHE, WOOLDRIDGE],
    {"question":"What can matching on measured covariates establish?", "options":["Balance on observed variables, subject to the chosen method", "That there is no unmeasured confounding", "That treatment was randomized"], "answerIndex":0, "explanation":"Matching can improve observed balance. It cannot verify the assumption that all relevant confounders were measured."}
),
module(
    "synthetic-control", "Synthetic Control for Comparative Case Studies", "Applied Econometrics", "Intermediate", 32, "regression",
    "Build a transparent weighted comparison for one treated region or institution and judge its value from pre-treatment fit and donor-pool credibility.",
    ["Explain the donor pool and weighted synthetic comparison.", "Assess pre-treatment fit and predictor selection.", "Use placebo and sensitivity analyses while respecting single-treated-unit limits."],
    [
        lesson("Construct a comparison from donor units", "When one region adopts a policy and no single comparison region is persuasive, synthetic control combines untreated units using weights chosen to match the treated unit before adoption. The result is a data-driven comparison, not a guarantee of causal validity. The donor pool must be unaffected by treatment and sufficiently similar on relevant pre-policy histories.", "Synthetic control constructs a weighted comparison, but institutional knowledge still defines a credible donor pool."),
        lesson("Pre-treatment fit is the first check", "Plot the treated and synthetic outcome paths before the intervention and summarize the gap. Poor pre-treatment fit signals that the constructed comparison does not reproduce the treated unit’s prior trajectory. A good fit is helpful but does not prove that unobserved post-policy shocks would have matched.", "A convincing post-policy gap is hard to interpret if the pre-policy paths already diverge."),
        lesson("Inspect donors and modelling choices", "Show which donor units receive weight, whether any are unusually influential, and how the fit changes when one donor or predictor is removed. Exclude units exposed to the same policy or spillovers. Avoid choosing predictors after looking for a large post-treatment gap. These decisions affect the counterfactual and must be documented.", "The donor pool and predictor choices are part of the design, not invisible software defaults."),
        lesson("Use placebos as a reference, not a magic test", "Applying the same procedure to untreated donor units can show whether the treated unit’s post-policy gap is unusually large relative to placebo gaps. Results are most informative when placebo units have comparable pre-treatment fit and the treated unit is not an extreme outlier simply because it has a much larger sample. With one treated case, uncertainty and generalization remain limited.", "Placebo comparisons can calibrate evidence but do not turn one case into a randomized experiment."),
    ],
    "A country introduces a large carbon levy while comparable countries do not. Build a synthetic comparison from unaffected countries, examine pre-policy emissions fit and test sensitivity to donor exclusions and concurrent climate policies.",
    ["Synthetic control is not automatically randomized or bias-free.", "Poor pre-treatment fit undermines the post-treatment comparison.", "Placebo distributions do not remove all uncertainty in a single treated case."],
    [MIXTAPE, MIXTAPE_OPEN, MHE],
    {"question":"Why is pre-treatment fit central to synthetic control?", "options":["It shows how well the weighted donors reproduce the treated unit before the policy", "It proves there were no unobserved post-policy shocks", "It guarantees a population-wide average effect"], "answerIndex":0, "explanation":"Pre-treatment fit is a key diagnostic, but it cannot verify the unobserved post-treatment counterfactual."}
),
module(
    "limited-outcomes", "Binary, Count & Limited Outcomes", "Applied Econometrics", "Intermediate", 38, "probability",
    "Choose models for employment, participation, service use and event counts, then report effects on interpretable probability or outcome scales.",
    ["Compare the linear probability, logit and probit models.", "Interpret marginal effects rather than relying only on odds ratios.", "Recognize count, censoring and two-part outcome structures."],
    [
        lesson("Start with the outcome’s support", "A binary outcome such as employment is zero or one. A count such as clinic visits is a non-negative integer. Expenditure may include many zeros and a long right tail. The outcome type guides model choice, but a more complex model is not automatically better; the target may be an average probability change, a predicted count or the amount spent conditional on spending.", "Model the variable and the policy question, not a textbook label."),
        lesson("Compare linear probability and nonlinear links", "A linear probability model is easy to interpret: a coefficient of 0.04 is a four-percentage-point conditional difference, though predictions can fall outside zero and one and variance is not constant. Logit and probit map a linear index into probabilities between zero and one. Their coefficients are on a latent scale, so show average marginal effects or predicted probabilities for policy interpretation.", "Report meaningful probability changes rather than treating a logit coefficient as a percentage-point effect."),
        lesson("Choose a count model and inspect its limits", "Poisson regression links the expected count to predictors and can be useful even when the variance is not exactly equal to the mean if inference is robust. Overdispersion or unobserved heterogeneity may motivate alternatives such as negative binomial models. If many observations have zero use because they are not eligible or do not participate, distinguish a structural participation process from a count process only when the data and question support it.", "Check the observed distribution and assumptions before choosing a count model."),
        lesson("Censoring and selection need different stories", "A top-coded income is censored because values above a limit are recorded at that limit; expenditure with many true zeros is not automatically censored. Tobit-type models impose a shared latent process for the zero boundary and positive outcome, which may not fit a separate participation decision. Compare predicted outcomes and state the assumptions that connect the observed measure to the model.", "Do not use a censored-outcome model merely because the data contain zeros."),
    ],
    "A local employment service studies whether a new appointment system changes the probability of job placement and the number of appointments used. Report probability changes and count-model checks rather than presenting only nonlinear-link coefficients.",
    ["A logit coefficient is not directly a percentage-point change in probability.", "Many zeros do not by themselves justify a zero-inflated model.", "A more flexible likelihood does not fix an ill-defined estimand or confounding."],
    [CAMERON, WOOLDRIDGE, ROS, STOCK],
    {"question":"How is a logit coefficient best translated for a broad policy audience?", "options":["As a direct percentage-point change", "Using predicted probabilities or marginal effects for stated covariates", "As proof of a causal effect"], "answerIndex":1, "explanation":"Logit coefficients are on a log-odds scale; predicted probabilities or marginal effects are easier to interpret."}
),
module(
    "selection-missing-data", "Selection, Attrition & Missing Data", "Data & Tools", "Intermediate", 34, "toolkit",
    "Trace who is observed, why values are missing and how participation or follow-up can change the target population and estimates.",
    ["Distinguish common missingness mechanisms and sample selection.", "Describe attrition and compare observed baseline features.", "Use weighting or sensitivity analysis only with explicit assumptions."],
    [
        lesson("Missing rows can change the question", "A household survey may miss people who move frequently, a firm database may omit businesses that close, and a trial may lose participants at follow-up. The observed sample then represents a selected group. Describe which units or variables are missing, when they became missing, and whether selection is related to treatment or outcomes.", "Missingness is about the data-collection process, not just blank cells in a spreadsheet."),
        lesson("State the missingness assumption", "Missing completely at random means missingness is unrelated to observed or unobserved data. Missing at random allows it to depend on observed information after conditioning on that information. Missing not at random still depends on unobserved values after adjustment. These labels are assumptions about how data went missing, not properties that can usually be diagnosed from observed data alone.", "Observed patterns can challenge assumptions but cannot reveal every unobserved missing value."),
        lesson("Account for selective observation", "If follow-up depends on measured baseline variables, inverse-probability weights can reweight observed participants toward the target population under a correct observation model and adequate overlap. Extreme weights signal limited information. Multiple imputation can represent uncertainty under a stated missing-at-random model, but neither method automatically corrects unmeasured selection.", "Weighting and imputation rely on assumptions that should be explained in plain language."),
        lesson("Show sensitivity and preserve denominators", "Report the starting sample, exclusions, missing outcome rates by group and reasons for loss where known. Compare complete-case estimates with defensible alternatives. For missing-not-at-random concerns, show how results would change under plausible departures from the main assumption. Keep denominators visible so a reader can see who contributes to each estimate.", "A sensitivity analysis makes the role of missing-data assumptions visible instead of silently treating observed cases as everyone."),
    ],
    "A job-training evaluation loses more participants from the control group than from the offer group. Compare attrition and baseline data, report who remains in each analysis, and test how plausible outcome differences among missing participants affect the result.",
    ["A large sample does not remove selection bias.", "Complete-case analysis is not automatically unbiased.", "Imputation or weighting does not reveal outcomes that were never observed without assumptions."],
    [CAMERON, WOOLDRIDGE, ROS, WHATIF],
    {"question":"What does ‘missing at random’ mean in a typical analysis?", "options":["Missingness can depend on observed information after conditioning on it", "Missingness is unrelated to every variable", "All missing values are equal to zero"], "answerIndex":0, "explanation":"The assumption permits dependence on observed data but not additional dependence on the missing value after conditioning."}
),
module(
    "heterogeneous-effects", "Heterogeneous Effects & Quantile Regression", "Applied Econometrics", "Intermediate", 35, "kde",
    "Ask whether average effects hide meaningful differences across groups or outcome distributions, and avoid turning subgroup patterns into unsupported stories.",
    ["Interpret interactions as conditional differences.", "Distinguish subgroup average effects from quantile regression coefficients.", "Pre-specify heterogeneity questions and report uncertainty across groups."],
    [
        lesson("An average can hide variation", "A policy can affect people differently because baseline resources, constraints or local conditions differ. The average treatment effect summarises one mean contrast and does not imply that every unit experiences that amount. Before exploring subgroups, name a mechanism and a small number of groups that matter for the decision.", "Heterogeneity is a question about how effects vary, not a licence to search endlessly for significant groups."),
        lesson("Read interaction terms carefully", "An interaction between treatment and a pre-treatment characteristic allows the treatment contrast to vary across that characteristic. In a linear model, the treatment coefficient may describe the effect at the reference value, while the interaction describes how the slope changes. For nonlinear models, coefficient interactions do not translate directly into probability-scale treatment-effect interactions; compute predictions or marginal effects on the scale of interest.", "Explain the scale and reference group when presenting an interaction."),
        lesson("Quantile regression answers a distributional question", "Quantile regression models a conditional quantile, such as the median outcome given covariates. Its slope describes how a covariate relates to that conditional quantile under the model. It is not automatically the effect for the same individuals who would occupy a particular rank under both treatment states; treatment-effect distributions require additional methods and assumptions.", "A conditional quantile coefficient is not automatically an individual-level treatment effect."),
        lesson("Keep discovery and confirmation distinct", "Subgroup analysis can produce many comparisons, especially when analysts try several outcomes, cut points and models. Pre-specify a few policy-relevant contrasts, show confidence intervals and sample sizes, and treat exploratory findings as hypotheses for further study. Where treatment effects differ, report the groups and context rather than implying a universal ranking of people.", "Transparent subgroup plans reduce selective emphasis and support fair interpretation."),
    ],
    "A childcare subsidy may affect labour-force participation differently for parents with different baseline care access. Define groups before analysis, estimate probability-scale contrasts, and report uncertainty without labelling exploratory differences as definitive.",
    ["A quantile coefficient does not directly identify the effect for a person at that rank.", "A significant subgroup and a non-significant subgroup do not prove their effects differ.", "Many data-driven subgroup searches inflate false-positive risk."],
    [MHE, CAMERON, ROS, MIXTAPE],
    {"question":"What does a conditional median-regression slope describe most directly?", "options":["A relationship with the conditional median outcome", "The treatment effect for the same person at the median in every counterfactual state", "A guarantee that half of every subgroup benefits"], "answerIndex":0, "explanation":"Conditional quantile regression describes a feature of the outcome distribution given covariates; it does not automatically identify individual treatment-effect ranks."}
),
module(
    "functional-form-specification", "Functional Form, Interactions & Model Checks", "Modelling", "Beginner", 32, "regression",
    "Use units, plots and economic mechanisms to choose functional forms, then check whether model simplifications change the conclusion.",
    ["Interpret level, log and polynomial specifications in their units.", "Use interactions and indicators without losing the reference category.", "Use residual and sensitivity checks to challenge a model."],
    [
        lesson("Keep units attached to every coefficient", "A level-on-level slope describes outcome units per one-unit change in a predictor. A log outcome with a level predictor often describes an approximate percentage difference per predictor unit; a log-log slope is an elasticity under the model. These are approximations whose accuracy depends on the change size and transformation. State units before translating coefficients into economic meaning.", "Functional form changes the interpretation, so report the variables and units used."),
        lesson("Allow curvature when the question calls for it", "A squared term can represent a changing slope, such as the association between experience and wages that rises then flattens. The marginal association depends on the value of the predictor, so interpret the combined expression or predicted curve rather than the squared-term coefficient alone. Polynomials can behave erratically outside the observed range, making extrapolation especially risky.", "A nonlinear term is a modelling choice that should match the supported data range and theory."),
        lesson("Interactions compare conditional slopes", "An interaction lets the relationship between one predictor and the outcome depend on another, such as a training association that differs by prior education. With a binary indicator, the main coefficient is tied to its reference group. Show predicted values or marginal contrasts for meaningful combinations, and avoid interpreting one term in isolation.", "Name the reference category and show the combined comparison people actually care about."),
        lesson("Check specification without chasing a preferred fit", "Plot residuals against fitted values, key predictors and time; examine influential observations; and compare a small number of substantively motivated specifications. Changes in coefficients may reveal sensitivity to controls or sample rules. Higher R-squared alone does not demonstrate correct specification, causal identification or out-of-sample value.", "Model checks can reveal trouble, but no single diagnostic certifies a model as true."),
    ],
    "A study of commuting time and employment uses a nonlinear relationship because transport access may matter more for some distances than others. Plot predictions over the observed range, define the reference group and avoid extrapolating to unobserved commute distances.",
    ["A coefficient cannot be interpreted without units and reference values.", "Adding terms until fit improves does not establish causality.", "A polynomial fit may be unreliable beyond the observed data range."],
    [WOOLDRIDGE, STOCK, ROS, MHE],
    {"question":"In a model with a treatment-by-group interaction, what should be shown for an interpretable group comparison?", "options":["The main coefficient alone", "The combined predicted or marginal contrast for the stated reference groups", "Only the model R-squared"], "answerIndex":1, "explanation":"The main and interaction terms work together. Predictions or marginal contrasts make the relevant group comparison explicit."}
),
module(
    "applied-macro-time-series", "Applied Macro Time Series & Forecasting", "Economic Applications", "Intermediate", 38, "volatility",
    "Study persistence, trends and dynamic responses in inflation, unemployment, output and rates while separating forecasting from causal claims.",
    ["Recognize trend, persistence, seasonality and structural change.", "Use lagged models and forecast evaluation with time-ordered data.", "Interpret dynamic responses and uncertainty cautiously."],
    [
        lesson("Inspect time order and measurement first", "Macroeconomic observations are ordered and often revised, seasonal and affected by changes in definitions. Plot levels and changes, record frequency and units, and mark major institutional breaks. A rising nominal series can reflect inflation rather than real growth, while annualising a monthly rate changes the scale. Preserve data vintages when a real-time forecast question matters.", "Time-series interpretation depends on dates, units, revisions and the measurement process."),
        lesson("Separate trend from persistence", "A series may move slowly because shocks persist, because it follows a deterministic trend, or because it contains a stochastic trend. Regressing unrelated trending levels can produce a persuasive but spurious relationship. Consider transformations such as growth rates or differences when they fit the question, and state what long-run information those transformations discard.", "A high fit between trending series is not evidence that one causes the other."),
        lesson("Build forecasts using only past information", "A time-ordered training and test split avoids using future observations to predict the past. Compare a simple benchmark with models containing lags or predictors that would have been available at the forecast date. Evaluate errors across multiple forecast origins and show intervals, not just one point prediction. Revisions or data leakage can make a historical backtest look better than a real-time forecast.", "Forecast evaluation should reproduce when information would actually have been available."),
        lesson("Dynamic responses are model-dependent", "Distributed-lag and autoregressive models can summarize how outcomes move after a shock. The response depends on lag length, stability, the meaning of the shock and assumptions about simultaneity. HAC standard errors can address certain forms of autocorrelation and heteroskedasticity for inference, but do not make an endogenous shock causal. State the model and show uncertainty across horizons.", "Dynamic estimates are not causal impulse responses unless the shock identification is defended."),
    ],
    "An analyst studies whether a tax change affected inflation and employment. The series should be plotted, revisions and concurrent policies documented, a time-ordered comparison designed, and any dynamic response reported with its identification assumptions.",
    ["A forecast can be useful without identifying a cause.", "Differencing can help with trends but changes the question and may remove long-run relationships.", "HAC standard errors do not identify an exogenous shock."],
    [STOCK, WOOLDRIDGE, MHE, ROS],
    {"question":"What does a time-ordered test set help prevent?", "options":["Using future observations to train a model that predicts the past", "All structural breaks", "All causal confounding"], "answerIndex":0, "explanation":"Chronological evaluation helps prevent look-ahead leakage; it does not solve structural breaks or causal identification."}
),
]

# Append only missing IDs so the operation is safe to rerun.
for item in new_modules:
    if item["id"] not in by_id:
        modules.append(item)
        by_id[item["id"]] = item

# Extend key methods using original explanations guided by the supplied book's
# chapter coverage. Keep this idempotent so every seed/build is safe to repeat.
topic_enrichments = {
    "regression": [
        lesson(
            "Conditional averages are not automatically causal",
            "Ordinary least squares is a best linear summary of observed conditional averages for the regressors and sample that were chosen. The conditional mean E[Y | X = x] may be curved even when a straight line is used to approximate it. A causal interpretation needs an identification argument beyond the regression calculation. Timing matters for controls: adjusting for a post-treatment mediator can remove part of an effect, while conditioning on a collider can create a spurious path. A good fit to observed averages does not supply the missing counterfactual.",
            "Regression summarizes conditional averages; design and control timing determine whether a coefficient is causal.",
            "E[Y | X = x] is an observed conditional mean; it equals a causal response only under additional assumptions."
        )
    ],
    "iv-2sls": [
        lesson(
            "The Wald ratio shows whose effect an instrument identifies",
            "Suppose a randomized offer raises programme take-up by 0.20 and raises average annual earnings by £300. The reduced-form change divided by the first stage is £300 / 0.20 = £1,500 per participant induced by the offer. Under random assignment, exclusion, a non-zero first stage and monotonicity, this is a local average treatment effect for compliers—people whose participation changes because of the offer. It is not automatically the average effect for every eligible person. Report the two component differences and their units, not just the ratio.",
            "The Wald ratio can identify a local effect for compliers, not a universal treatment effect.",
            "Wald estimate = reduced-form outcome change / first-stage treatment change.",
            {"question":"An offer increases participation by 0.25 and raises mean earnings by £500. What is the Wald ratio before interpreting it?", "hint":"Divide the outcome change by the change in participation.", "solution":"£500 / 0.25 = £2,000 per induced participant. A causal interpretation still depends on the IV assumptions and describes compliers."}
        )
    ],
    "panel-fixed-effects": [
        lesson(
            "Fixed effects and lagged outcomes answer different questions",
            "Unit fixed effects remove stable additive differences and identify coefficients from within-unit changes. A lagged dependent variable instead conditions on the previous outcome to describe a dynamic relationship. In short panels, that lag can be correlated with the transformed error in a fixed-effects model, so the estimator may be biased. Neither approach is a mechanical substitute for the other: choose based on the data-generating story, timing and assumptions, and consider whether treatment changes with time-varying confounders.",
            "Fixed effects remove time-constant unit differences; adding a lagged outcome is a separate modelling choice with its own assumptions."
        )
    ],
    "heterogeneous-effects": [
        lesson(
            "Conditional quantiles are not individual treatment effects",
            "A quantile regression can describe, for example, the conditional median of earnings among people with specified observed covariates. A quantile treatment effect instead compares quantiles of potential-outcome distributions under a design that supports a causal contrast. Neither reveals which particular person's treatment effect is large, and a change in a conditional quantile need not equal a change in the marginal population quantile. Name the distribution, conditioning variables, target group and identification assumptions before making a distributional claim.",
            "Quantile regression describes conditional distributions; causal quantile effects require a design and a clearly stated target.",
            "QTE at quantile τ = Q[Y(1), τ] − Q[Y(0), τ]."
        )
    ],
    "applied-macro-time-series": [
        lesson(
            "An AR(1) forecast mean-reverts toward its long-run mean",
            "For the zero-mean stationary process in this module, yₜ = φyₜ₋₁ + εₜ with |φ| < 1, the h-step conditional mean is φʰyₜ, so it decays toward zero. It is not the last observation plus another copy of its projected value. With innovation variance σ², the h-step forecast variance is σ²(1 + φ² + … + φ²⁽ʰ⁻¹⁾); the band widens with horizon and approaches the long-run variance. A different intercept or deterministic trend changes the long-run mean, so the model specification must be stated.",
            "A stationary zero-mean AR(1) forecast moves toward zero; forecast uncertainty accumulates with the horizon.",
            "E[yₜ₊ₕ | yₜ] = φʰyₜ; Var(errorₜ₊ₕ) = σ² Σⱼ₌₀ʰ⁻¹ φ²ʲ."
        )
    ],
}
for module_id, additions in topic_enrichments.items():
    if module_id not in by_id:
        raise ValueError(f"Cannot enrich missing module {module_id}")
    existing_titles = {item.get("title") for item in by_id[module_id].get("lessons", [])}
    for addition in additions:
        if addition["title"] not in existing_titles:
            by_id[module_id].setdefault("lessons", []).append(addition)
            existing_titles.add(addition["title"])

# Add original, applied follow-up lessons that make the identification target,
# assumptions, and inferential trade-offs explicit for each related method.
advanced_enrichments = {
    "research-design": [
        lesson(
            "The same design can identify different target effects",
            "Imagine a city offers job training, but some invited residents decline and some uninvited residents find another course. The outcome difference by original invitation is the intention-to-treat effect. Dividing that outcome difference by the invitation's effect on take-up can identify a local average treatment effect for people whose participation changed because of the invitation, but only under the IV assumptions. A threshold design is local to people near its cutoff; a difference-in-differences design targets a treated group's change relative to a credible comparison trend. These are not automatically estimates of one universal effect. State who, what treatment contrast, outcome, and horizon the number describes before comparing estimates.",
            "A method's source of variation helps define the estimand; the estimator name alone does not say who the result is about.",
            "ITT = E[Y|Z=1] − E[Y|Z=0]; under IV assumptions, LATE = ITT / (E[D|Z=1] − E[D|Z=0]).",
            {"question":"A policy team wants the effect of completing training, but only the invitation was randomized. Which effect can be estimated directly from assignment?", "hint":"Keep the original randomized variable separate from take-up.", "solution":"The intention-to-treat effect of the invitation is directly estimated by comparing outcomes by assigned offer. The effect of completing training requires additional IV assumptions and generally applies to compliers, not automatically to everyone."}
        )
    ],
    "experimental-design": [
        lesson(
            "Use pre-treatment measures for precision, not post-assignment filters",
            "If a baseline test score was measured before a randomized tutoring offer, it can predict the follow-up score. A pre-specified regression adjustment for that baseline measure can improve precision while retaining the assigned-offer comparison as the intention-to-treat target. Report the assignment contrast and explain the adjustment rather than choosing controls after inspecting which model looks most favourable. A variable measured after assignment may itself be changed by the offer; controlling for attendance, effort, or another post-assignment outcome can block part of the effect or create selection. Randomization protects the assignment comparison, not every regression specification an analyst might try.",
            "Baseline covariates can sharpen a randomized comparison; post-treatment controls need a separate causal justification.",
            practice={"question":"A trial analyst wants to control for tutoring attendance measured after the offer. Why is that not equivalent to adjusting for a baseline score?", "hint":"Ask whether assignment could change the proposed control.", "solution":"The offer can change attendance, so attendance is post-treatment. Conditioning on it can remove part of the offer's effect or introduce selection; a pre-offer score cannot be affected by the assignment."}
        )
    ],
    "iv-2sls": [
        lesson(
            "Weak instruments make conventional intervals fragile",
            "Suppose eligibility for a grant changes programme participation by only 0.02. A small reduced-form earnings difference is then divided by a very small first stage, so modest sampling noise can move the IV ratio substantially. In common settings, weak instruments can pull finite-sample 2SLS estimates toward the confounded OLS result, while conventional t-tests and confidence intervals may have poor coverage. Show the first-stage estimate and uncertainty, the reduced form, and diagnostics suited to the design; consider weak-instrument-robust inference where appropriate. No single first-stage threshold proves an instrument is valid: strength addresses relevance, not independence or exclusion.",
            "A weak first stage threatens both stability and ordinary inference; it does not make the other IV assumptions more credible.",
            practice={"question":"An instrument has a strong first stage but may affect earnings directly through a separate grant channel. Which issue remains?", "hint":"Separate how much treatment moves from whether the instrument has another route to the outcome.", "solution":"The exclusion restriction remains in doubt. Relevance is about predicting treatment; a direct instrument-to-outcome path violates exclusion even when the first stage is strong."}
        )
    ],
    "difference-in-differences": [
        lesson(
            "Calculate the contrast before reading a regression table",
            "Use illustrative group means measured in the same outcome units. The treated region rises from 50 to 56, a change of 6; the comparison region rises from 48 to 51, a change of 3. The two-period difference-in-differences estimate is 6 − 3 = 3 units. It is not the treated group's six-unit before–after change, nor the three-unit difference in final levels. A causal interpretation requires the comparison change to represent the treated region's unobserved no-policy change, alongside credible timing, measurement, composition, and spillover conditions. With staggered adoption or changing effects, choose an estimator that matches the treatment timing rather than assuming a basic two-way fixed-effects coefficient has the desired meaning.",
            "Difference-in-differences subtracts the comparison group's change, and the counterfactual trend—not the arithmetic—is the key causal assumption.",
            "DiD = (56 − 50) − (51 − 48) = 3 outcome units.",
            {"question":"In the illustrative example, what is the estimate and what assumption gives it a causal interpretation?", "hint":"Subtract changes, then name the missing no-policy comparison.", "solution":"The estimate is 3 units. It is causal only if, absent the policy, the treated region would have changed like the comparison region on average, with no other design-breaking changes such as spillovers or selective composition shifts."}
        )
    ],
    "regression-discontinuity": [
        lesson(
            "The bandwidth trades locality against precision",
            "Suppose a scholarship rule changes at a score of 75 and estimated enrolment rises by 6 percentage points just at that threshold. This is evidence about applicants close to 75, not automatically about those far below or above it. A narrower bandwidth compares more similar scores and can reduce reliance on a broad functional-form extrapolation, but it leaves fewer observations and usually increases uncertainty. A wider window adds information while asking the fitted curves to describe more distant units. Show the cutoff, observations on each side, the chosen local specification, uncertainty, and sensitivity to reasonable bandwidths. Smooth covariates and no visible bunching can support the design story, but do not prove every continuity assumption.",
            "The local window is part of the RD design: explain its bias–precision trade-off and keep the claim local to the cutoff.",
            {"question":"An RD estimate is stable near a score cutoff. Can it be reported as the average effect for all scholarship applicants?", "hint":"Identify which units supply the comparison.", "solution":"Not without additional assumptions. The design directly compares units near the cutoff, so broad generalization beyond that local group needs separate evidence."}
        )
    ],
    "panel-fixed-effects": [
        lesson(
            "The within transformation shows what identifies a fixed-effects estimate",
            "For each firm, subtract its own time average from each variable. A stable characteristic such as persistent management style then disappears from both the outcome and treatment deviations. The treatment coefficient is identified from how treatment and outcome move within the same firm over time, after any included period effects. A variable that never changes within a firm cannot have its separate coefficient estimated this way. Nor does demeaning remove a time-varying shock that changes alongside treatment, such as a local demand surge that triggers both investment and hiring. Describe the remaining source of treatment variation, not just the phrase ‘fixed effects’.",
            "Fixed-effects identification comes from within-unit changes that remain after removing stable unit differences and included time effects.",
            "Yᵢₜ − Ȳᵢ = β(Dᵢₜ − D̄ᵢ) + (εᵢₜ − ε̄ᵢ), before any included time-effect adjustment."
        )
    ],
    "robust-clustered-inference": [
        lesson(
            "Cluster where assignment and shocks are shared",
            "Suppose a programme is assigned to 30 schools, with 20 pupils observed in each. There are 600 pupil records but only 30 independently assigned school-level units. If pupils in a school share teachers, neighbourhood shocks, or the same treatment, their errors can move together; treating all 600 as independent can make uncertainty look too small. A simple equal-size intuition is the design effect 1 + (m − 1)ρ, where m is pupils per school and ρ is within-school correlation. With few schools, ordinary cluster-robust standard errors can themselves be unreliable, so report the number and size of clusters and use inference appropriate to the assignment design, such as randomization-based or small-sample methods when justified.",
            "The number of rows is not the number of independent treatment assignments; choose inference at the design's shared-variation level.",
            "Equal-cluster-size intuition: design effect ≈ 1 + (m − 1)ρ; this is not a substitute for a design-specific variance estimator.",
            {"question":"If treatment is assigned to schools, which count is more relevant to the independent assignment information: 600 pupils or 30 schools?", "hint":"Use the unit that received the assignment.", "solution":"The 30 schools. Pupils within a school may provide outcome detail, but they do not create 600 independent school-level assignments."}
        )
    ],
    "matching-weighting": [
        lesson(
            "Weighting choices define which population the contrast describes",
            "Matching or weighting can make treated and comparison units more alike on measured pre-treatment covariates, but different weights answer different target-population questions. For example, weighting comparison units to resemble the treated group supports an effect-on-the-treated target under conditional exchangeability and overlap; other weights may target an average effect for a broader population. Units with almost no comparable counterparts receive extreme weights or no credible match. Show balance after weighting, overlap, influential weights, and the effective sample size. Trimming unsupported regions may improve stability, but it also changes who the estimate represents and must be reported as a target-population choice.",
            "Balance is about measured covariates; the weighting rule and overlap determine the target population and the remaining assumptions.",
            {"question":"A treated group has no comparable controls for the highest baseline-risk units. What should an analyst not do?", "hint":"Ask whether a weight can create information where no comparison exists.", "solution":"Do not hide the lack of overlap behind a large weight or extrapolate without qualification. Report the unsupported group and state how any trimming changes the target population."}
        )
    ],
    "synthetic-control": [
        lesson(
            "Compare placebo units only when their pre-policy fit is comparable",
            "A post-policy gap for the treated region is easier to interpret when the weighted donors tracked it closely before the policy. Applying the same procedure to untreated donor units can show whether the treated gap is unusual, but a donor with a very poor pre-policy match is not a fair placebo comparator. Report pre-policy fit for each placebo, the treated unit's place in that distribution, donor weights, and sensitivity to removing influential donors or changing the pre-policy window. With one treated case, this is a structured comparison rather than a large-sample experiment; uncertainty and generalization remain limited.",
            "Placebo gaps are informative only alongside comparable pre-treatment fit and a transparent donor pool."
        )
    ],
    "limited-outcomes": [
        lesson(
            "Translate nonlinear coefficients onto the probability scale",
            "For a binary outcome, a logit coefficient is a change in log odds, not a fixed percentage-point change in participation. If a model predicts a probability rising from 0.40 to 0.46 for a stated comparison, the difference is 0.06, or 6 percentage points. In a logit model that probability contrast depends on the starting covariate values; report predicted probabilities or an average marginal effect and show the population over which it is averaged. A linear probability coefficient is already on the probability scale but can predict outside zero and one and needs appropriate inference. Neither functional form makes the contrast causal without a design that supports that claim.",
            "Report probability changes at stated covariate values or averaged over a defined sample; do not read log-odds as percentage points.",
            "0.46 − 0.40 = 0.06 = 6 percentage points.",
            {"question":"A logit coefficient is 0.06. Does that mean the outcome probability rises by 6 percentage points for everyone?", "hint":"Check the scale of the coefficient and whether the probability link is nonlinear.", "solution":"No. The coefficient is on the log-odds scale. The probability change depends on baseline covariates; calculate a predicted-probability contrast or marginal effect."}
        )
    ],
    "selection-missing-data": [
        lesson(
            "Conditioning on who is observed can change the estimand",
            "Suppose a training programme can affect whether a person is employed, and wages are recorded only for employed people. Comparing wages among observed workers conditions on a status that may itself be changed by treatment. The result is then about selected observed workers, not automatically the programme's effect on earnings for everyone offered training; selection can also open a non-causal association between treatment and unobserved determinants of employment. Report employment and wage outcomes separately where possible, retain the assigned groups and denominators, and explain any bounds or sensitivity analysis used for wages that are unobserved. Accurate wage measurement among workers does not solve the missing counterfactual for those not working.",
            "When observation depends on a post-treatment outcome or status, the observed-case comparison may answer a different question from the policy estimand.",
            {"question":"If treatment changes who is employed, what is the risk of comparing wages only among currently employed people?", "hint":"Ask whether employment is fixed before treatment or can be changed by it.", "solution":"Employment is post-treatment and may select different people into the wage sample in each group. The wage comparison among workers need not be the effect for the original assigned population."}
        )
    ],
    "heterogeneous-effects": [
        lesson(
            "Test the difference between groups directly",
            "Imagine a training effect estimate of 0.4 for younger applicants and 0.1 for older applicants. One estimate having a confidence interval that excludes zero while the other does not is not itself evidence that the two effects differ. Estimate the group contrast, often with a pre-specified treatment-by-group interaction, and report its uncertainty and the group sample sizes. Choose characteristics measured before treatment when defining subgroups, and limit the number of comparisons or label them exploratory. A real average-effect difference across groups still does not reveal every individual's treatment effect or establish a universal ranking of who benefits most.",
            "Evidence that one subgroup effect differs from zero is not a test that it differs from another subgroup effect.",
            "Group contrast = τ₁ − τ₂; assess its uncertainty directly rather than comparing two separate significance labels.",
            {"question":"Group A's estimate is statistically significant and Group B's is not. What additional quantity should be examined before claiming different effects?", "hint":"Form the contrast of the estimates.", "solution":"Estimate τ_A − τ_B and its uncertainty, such as the interaction contrast from a pre-specified model. Separate p-values do not test equality of effects."}
        )
    ],
    "functional-form-specification": [
        lesson(
            "Trace omitted-variable bias through two relationships",
            "In a simple linear setting, omitting a variable U that affects the outcome can shift the treatment coefficient in proportion to two links: how U predicts the outcome after included controls, and how U is associated with treatment after those controls. If recent unemployment raises take-up of a training programme but lowers later earnings, omitting it can push the training coefficient downward. If prior ability raises both take-up and earnings, omitting it can push the coefficient upward. The sign is not determined by whether a variable sounds important; it depends on both relationships and the conditioning set. A formula is a guide to the direction under a simple model, not a replacement for a causal design or a reason to control for post-treatment variables.",
            "The direction of omitted-variable bias depends on both the outcome link and the treatment association, conditional on included controls.",
            "In a simple one-omitted-variable model: bias in β̂_D ≈ γ × δ, where γ is U's outcome slope and δ is U's treatment slope.",
            {"question":"An unobserved factor raises programme take-up (δ > 0) but lowers earnings (γ < 0). What direction does the simple omitted-variable-bias formula predict?", "hint":"Multiply the signs of the two links.", "solution":"The product is negative, so the estimated programme coefficient is biased downward in this simplified setup. The result depends on the stated model and conditional relationships."}
        )
    ],
    "applied-macro-time-series": [
        lesson(
            "Serial dependence means monthly rows are not monthly experiments",
            "Inflation or unemployment observed month after month often carries persistent shocks forward. If adjacent errors are correlated, treating each month as an independent observation can make a standard error too small even when the coefficient calculation is unchanged. Heteroskedasticity-and-autocorrelation-consistent methods can address specified forms of serial dependence for some inferential targets, but the lag window and sample length matter; in a short series, uncertainty can remain substantial. Such standard errors do not repair a structural break, omitted policy change, trend misspecification, or an endogenous shock. Describe the time span and dependence assumptions alongside any interval.",
            "A long sequence can contain far fewer independent pieces of information than its row count suggests; robust inference does not create causal identification."
        )
    ],
}
for module_id, additions in advanced_enrichments.items():
    if module_id not in by_id:
        raise ValueError(f"Cannot add advanced lesson to missing module {module_id}")
    existing_titles = {item.get("title") for item in by_id[module_id].get("lessons", [])}
    for addition in additions:
        if addition["title"] not in existing_titles:
            by_id[module_id].setdefault("lessons", []).append(addition)
            existing_titles.add(addition["title"])

# Link to the publisher's record and identify the book chapter/section relevant
# to each method. Synthetic control is not covered by this book, so it is not
# given a misleading MHE chapter citation.
mhe_url = "https://press.princeton.edu/books/paperback/9780691120355/mostly-harmless-econometrics"
mhe_chapters = {
    "research-design": "Chs. 1–2",
    "experimental-design": "Ch. 2, §§2.2–2.3",
    "iv-2sls": "Ch. 4, §§4.1–4.6",
    "difference-in-differences": "Ch. 5, §5.2",
    "regression-discontinuity": "Ch. 6, §§6.1–6.2",
    "panel-fixed-effects": "Ch. 5, §§5.1, 5.3",
    "robust-clustered-inference": "Ch. 8, §§8.1–8.3",
    "matching-weighting": "Ch. 3, §§3.3.1–3.3.3, 3.4.1",
    "limited-outcomes": "Ch. 3, §3.4.2; Ch. 4, §4.6.3",
    "selection-missing-data": "Ch. 2, §2.1; Ch. 3, §3.2",
    "heterogeneous-effects": "Ch. 3, §3.3; Ch. 7, §§7.1–7.2",
    "functional-form-specification": "Ch. 3, §§3.1–3.2.3",
    "applied-macro-time-series": "Ch. 8, §8.2.2 (serial correlation in panels and DiD)",
    "regression": "Ch. 3, §§3.1–3.2.3",
}
for module_id, chapter_text in mhe_chapters.items():
    if module_id not in by_id:
        raise ValueError(f"Cannot cite missing module {module_id}")
    source = {
        "label": f"Angrist & Pischke (2008), Mostly Harmless Econometrics, {chapter_text}",
        "url": mhe_url,
    }
    sources = by_id[module_id].setdefault("sources", [])
    if source["label"] not in {item.get("label") for item in sources}:
        sources.append(source)

# Synthetic control is not discussed in Mostly Harmless Econometrics; retain the
# dedicated synthetic-control texts rather than implying a chapter covers it.
if "synthetic-control" in by_id:
    by_id["synthetic-control"]["sources"] = [
        source for source in by_id["synthetic-control"].get("sources", [])
        if source.get("label") != MHE["label"]
    ]

# Reuse existing clips only in the matching foundational modules. Register a
# caption track only when its WebVTT file is actually present.
existing_video_assets = {
    "statistical-thinking": "statistical-thinking",
    "probability": "probability",
    "distributions": "distributions",
    "estimation": "estimation",
    "p-values": "p-values",
    "regression": "regression",
    "causal": "causal",
    "time-series": "time-series",
    "returns-risk": "returns-risk",
    "portfolio": "portfolio",
    "bayesian": "bayesian",
    "backtesting": "backtesting",
    "correlation": "correlation",
    "kernel-density": "kernel-density",
}
for module_id, asset_name in existing_video_assets.items():
    if module_id not in by_id:
        continue
    video_file = ROOT / "public/videos" / f"{asset_name}.mp4"
    caption_file = ROOT / "public/videos" / f"{asset_name}.vtt"
    if video_file.is_file():
        by_id[module_id]["video"] = f"/videos/{asset_name}.mp4"
    if caption_file.is_file():
        by_id[module_id]["captions"] = f"/videos/{asset_name}.vtt"

MODULES_PATH.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n")
print(f"Applied economics curriculum ready: {len(modules)} modules, {sum(len(m.get('lessons', [])) for m in modules)} lessons.")
