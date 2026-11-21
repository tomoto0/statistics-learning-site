#!/usr/bin/env python3
"""Add new intermediate-foundation topics and focused follow-up lessons idempotently."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES_PATH = ROOT / "src/data/modules.json"
modules = json.loads(MODULES_PATH.read_text())
by_id = {item["id"]: item for item in modules}


def lesson(title, body, takeaway, formula=None, practice=None):
    item = {"title": title, "body": body, "takeaway": takeaway}
    if formula:
        item["formula"] = formula
    if practice:
        item["practice"] = practice
    return item


def module(id, title, category, level, minutes, lab, excerpt, objectives,
           lessons, case_study, misconceptions, sources, quiz):
    return {
        "id": id, "slug": id, "title": title, "category": category,
        "level": level, "minutes": minutes, "lab": lab, "excerpt": excerpt,
        "objectives": objectives, "lessons": lessons,
        "caseStudy": case_study, "misconceptions": misconceptions,
        "sources": sources, "quiz": quiz,
    }

ROS = {"label": "Gelman, Hill & Vehtari — Regression and Other Stories (Cambridge University Press)",
       "url": "https://www.cambridge.org/highereducation/books/regression-and-other-stories/DD20DD6C9057118581076E54E40C372C"}
ROS_AUTHORS = {"label": "Regression and Other Stories — authors’ book site and chapter resources",
               "url": "https://sites.stat.columbia.edu/gelman/regression/"}
PYMC = {"label": "PyMC example — Hierarchical Partial Pooling",
        "url": "https://www.pymc.io/projects/examples/en/latest/case_studies/hierarchical_partial_pooling.html"}
PSU = {"label": "Penn State STAT 506 — Sampling Theory and Methods (open course notes)",
       "url": "https://online.stat.psu.edu/stat506/"}
PSU_STRATA = {"label": "Penn State STAT 506 — Stratified Sampling",
              "url": "https://online.stat.psu.edu/stat506/Lesson06.html"}
PSU_CLUSTER = {"label": "Penn State STAT 506 — Cluster and Systematic Sampling",
               "url": "https://online.stat.psu.edu/stat506/Lesson07.html"}
STATCAN = {"label": "Zins & Burgard — Considering interviewer and design effects when planning sample sizes (Statistics Canada)",
           "url": "https://www150.statcan.gc.ca/n1/pub/12-001-x/2020001/article/00005-eng.pdf"}
UCLA_SURVIVAL = {"label": "UCLA OARC — Introduction to Survival Analysis in R (open workshop notes)",
                 "url": "https://stats.oarc.ucla.edu/wp-content/uploads/2025/02/survival_r_full.html"}
SURVIVAL_REVIEW = {"label": "Schober & Vetter — Survival Analysis and Interpretation of Time-to-Event Data (open-access review)",
                   "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6110618/"}
PYSAL = {"label": "PySAL esda — Global Spatial Autocorrelation with Moran’s I",
         "url": "https://pysal.org/esda/stable/user-guide/global_morans_i.html"}
GEODA = {"label": "GeoDa Center — Global Spatial Autocorrelation workbook",
         "url": "https://geodacenter.github.io/workbook/5a_global_auto/lab5a.html"}

new_modules = [
    module(
        "multilevel-partial-pooling", "Multilevel Models & Partial Pooling", "Multilevel Models", "Beginner–Intermediate", 38, "pooling",
        "Model outcomes nested within schools, regions or firms while balancing group-level patterns against noisy local estimates.",
        ["Recognize grouped data and separate within-group from between-group variation.",
         "Compare complete pooling, no pooling and partial pooling.",
         "Interpret varying intercepts, group-level predictors and the limits of small-group data."],
        [
            lesson("Why a group label can matter", "Suppose a labour economist compares earnings across local job centres. People within a centre share local employers and services, so their outcomes may be more alike than outcomes from unrelated centres. A single regression that ignores that grouping can misstate uncertainty or miss meaningful variation. A multilevel model represents both an overall relationship and group-specific departures, while keeping the level of each variable clear.", "Grouping is part of the data structure; it is not automatically a causal design."),
            lesson("The two extremes: pool everything or nothing", "Complete pooling estimates one common group mean and treats observed differences as noise. No pooling estimates each group independently, so a small centre with only a few cases can appear unusually high or low by chance. Neither extreme is ideal when groups are related but not identical. The model should allow differences while sharing information in a way justified by the group structure.", "Complete pooling can hide real group variation; no pooling can overreact to noisy small groups."),
            lesson("Partial pooling tempers noisy group estimates", "Partial pooling estimates an overall level and a distribution of group effects. A group with abundant, precise information stays closer to its own data; a small or noisy group is pulled more toward the overall pattern. This shrinkage is not an arbitrary correction: it follows from the assumed distribution of group effects and within-group uncertainty. The amount of pooling is learned or specified through the model, not chosen to make a preferred ranking.", "Groups with less information are generally shrunk more, with uncertainty retained."),
            lesson("Read a varying-intercept model", "A random-intercept model can be written as Yᵢⱼ = α + βXᵢⱼ + uⱼ + εᵢⱼ, where j indexes groups, i indexes people, uⱼ is a group deviation, and εᵢⱼ is an individual deviation. The group effects are commonly modeled as coming from a shared distribution with variance τ². A group-level predictor, such as local unemployment, can explain some between-group variation, but its coefficient is not automatically causal and can mix within- and between-group comparisons if the question is not carefully defined.", "A group effect describes residual group variation under the model, not a proven group-level cause.", "Yᵢⱼ = α + βXᵢⱼ + uⱼ + εᵢⱼ; Var(uⱼ)=τ² and Var(εᵢⱼ)=σ²."),
            lesson("Know what the design can support", "Many observations within a handful of groups do not provide the same information as many independent groups. Report both the number of groups and the number of observations per group, inspect whether group sizes are uneven, and check sensitivity to the distributional assumptions. Predictions for an already observed group use its data; predictions for a new group also include uncertainty about the distribution of group effects. A varying-slope model is useful only when the data support group-specific relationships and the added complexity serves the question.", "Distinguish inference about existing groups from prediction for a new group.", practice={"question":"Two districts have the same observed mean wage, but one mean comes from 8 workers and the other from 800. Which district estimate should usually be pulled more toward the overall mean in a partial-pooling model?", "hint":"Compare how much sampling noise each group mean is likely to contain.", "solution":"The estimate from 8 workers is usually less precise and is therefore pulled more strongly toward the overall mean, subject to the model’s variance assumptions."}),
        ],
        "A regional employment service compares job-placement outcomes across 35 offices. Office sizes vary widely. Partial pooling can prevent very small offices from dominating league tables because of chance variation, while retaining evidence that some places may have systematically different outcomes. The estimates describe modeled differences; they do not by themselves explain why offices differ.",
        ["Partial pooling does not make every group identical.", "Shrinkage is not proof that a group’s true effect equals the overall mean.", "A large number of individuals cannot replace information from having more independent groups.", "A group-level association is not automatically causal."],
        [ROS, ROS_AUTHORS, PYMC],
        {"question":"Which group estimate is usually shrunk more toward the overall mean?", "options":["A small group estimate with high sampling uncertainty", "A large group estimate with high precision", "Every group by exactly the same amount regardless of its data"], "answerIndex":0, "explanation":"Partial pooling uses group-level uncertainty. Less precise estimates generally receive more shrinkage, conditional on the model."}
    ),
    module(
        "complex-survey-sampling", "Survey Sampling & Complex Designs", "Survey Methods", "Beginner–Intermediate", 36, "survey",
        "Move from a target population to defensible survey estimates by tracking inclusion probabilities, strata, clusters, weights and design-aware uncertainty.",
        ["Define the target population, sampling frame and unit before interpreting a survey estimate.",
         "Explain why unequal selection probabilities lead to survey weights.",
         "Distinguish stratification, cluster sampling, nonresponse adjustment and design-based uncertainty."],
        [
            lesson("Start with the population, frame and selection process", "A survey of household energy costs should say which households, geography and reference period it represents. The sampling frame is the operational list or process from which units can be selected; it can omit eligible households or include outdated records. A probability sample gives each eligible unit a known, non-zero chance of selection under the design. A very large sample cannot repair a frame that systematically excludes the population of interest.", "Population coverage and selection probabilities matter before sample size does."),
            lesson("Weights reflect unequal chances of selection", "If unit i has inclusion probability πᵢ, its basic design weight is 1/πᵢ: units selected less often represent more of the population. A Horvitz–Thompson total sums the observed value multiplied by that base weight. Production survey weights may add nonresponse adjustments and calibration to known population totals. These steps can improve representation under their assumptions, but a weight is not a magic correction for unmeasured coverage or response bias; extreme weights can also make estimates less precise.", "Weights encode a stated selection or adjustment process; report how they were built.", "Base design weight dᵢ = 1/πᵢ; estimated population total = Σᵢ∈sample dᵢYᵢ."),
            lesson("Strata and clusters solve different field problems", "Stratification partitions the population into groups before selection and samples within each group. It can ensure subgroup coverage and improve precision when units within a stratum are similar on the outcome. Cluster sampling selects groups such as neighbourhoods or schools, often to reduce travel or listing cost. Members of a selected cluster may be similar, so collecting many people in a few clusters can yield less independent information than the row count suggests. A design can use strata and multiple sampling stages together.", "Strata organize selection across groups; primary sampling units describe clustered selection."),
            lesson("Let the sample design govern uncertainty", "An unweighted standard error that assumes independent, equally selected observations may not describe a stratified, clustered or unequal-probability sample. Analysts need the released design variables or replicate weights and the documented variance method. For an equal-size cluster illustration, the design effect is approximately 1 + (m − 1)ρ, where m is cluster size and ρ is the within-cluster correlation; real survey design effects depend on the estimator, weights and full design. A design-based standard error describes sampling variation, not confounding in a causal comparison.", "Weights alone do not specify the variance estimator or make a causal design."),
            lesson("Treat nonresponse as a separate stage", "The design weight is based on selection, while a response adjustment relies on additional assumptions about who responds. Calibration may align weighted totals with trusted benchmarks, but it cannot guarantee that respondents and nonrespondents have the same outcome within adjustment cells. Publish response rates, coverage limitations, weight construction and design-aware uncertainty. If conclusions may depend on nonresponse assumptions, add a sensitivity analysis rather than claiming that weighting removes all bias.", "Selection, response, calibration and variance estimation are related but distinct parts of survey analysis.", practice={"question":"A sample has a large number of respondents but oversamples one region by design. What should an analyst check before reporting the raw mean as a national average?", "hint":"Ask what each respondent represents and how the regional selection probabilities differ.", "solution":"Check the target population and region-specific inclusion probabilities, then use appropriate survey weights and design-aware variance estimation. Also assess coverage and nonresponse assumptions."}),
        ],
        "A national survey deliberately samples remote districts at a higher rate so that their labour-market conditions can be reported. The raw respondent average therefore does not represent the national workforce by itself. The analyst uses the documented selection weights, retains the strata and primary sampling units for uncertainty estimates, and separately explains nonresponse adjustments.",
        ["A weight does not prove that nonresponse bias has been removed.", "A large respondent count does not make a convenience sample representative.", "Stratification and clustering have different roles and can appear together.", "A design effect is tied to an estimator and design; it is not a fixed property of a survey."],
        [PSU, PSU_STRATA, PSU_CLUSTER, STATCAN],
        {"question":"What is the basic design weight for a unit with inclusion probability πᵢ?", "options":["1/πᵢ", "πᵢ²", "The sample size divided by its outcome"], "answerIndex":0, "explanation":"The inverse inclusion probability represents how many population units the sampled unit stands for under the design. Later adjustments may be added and need their own assumptions."}
    ),
    module(
        "survival-duration-analysis", "Survival & Duration Analysis", "Survival Analysis", "Intermediate", 38, "survival",
        "Study the time until an event—such as re-employment—while using partial follow-up instead of discarding censored observations or treating them as events.",
        ["Represent follow-up time and event status separately.",
         "Interpret right-censoring, risk sets and the Kaplan–Meier survival curve.",
         "Distinguish survival probabilities from hazards and interpret Cox hazard ratios cautiously."],
        [
            lesson("Duration outcomes contain time and status", "For an unemployment-spell study, record how long each person is followed and whether re-employment is observed during that period. Someone still searching when the study ends contributes a known spell lasting at least until their last observed date. Their event time is unknown beyond that point, but their observed follow-up is not useless. Preserve the time scale, origin, event definition and status flag for every eligible spell.", "A duration outcome combines follow-up time with an event indicator."),
            lesson("Right-censoring is partial information, not a zero", "Right-censoring occurs when an event has not been observed by the end of follow-up or a person leaves observation. The data tell us the event time exceeds the recorded follow-up. A censored spell should not be coded as if the event occurred at that time or as if the duration were zero. Kaplan–Meier estimation uses those who remain at risk at each event time; censoring reduces later risk sets without causing a downward step in the survival estimate at that instant. Informative loss to follow-up can still bias the result.", "A censored observation remains informative up to its last known time, subject to censoring assumptions."),
            lesson("Read the survival curve and median", "The survival function S(t) is the probability that the event time is later than t. The Kaplan–Meier curve estimates this function as a stepwise product of the event-free proportions at observed event times. Its median duration is the first time at which the estimated survival probability reaches one half; if the curve never falls that far during follow-up, the median is not observed within the study horizon. The curve is a probability over time, not a count of events.", "The Kaplan–Meier curve changes at event times and accounts for the changing risk set.", "Ŝ(t) = ∏_{tₖ≤t}(1 − dₖ/nₖ), where dₖ events occur among nₖ units at risk."),
            lesson("Hazard is conditional on still being at risk", "The hazard describes the instantaneous event rate around time t among units that have not yet had the event. The survival probability is cumulative; it describes the chance of remaining event-free beyond a time. A Cox proportional-hazards model compares hazards over time while leaving the baseline hazard unspecified. Its hazard ratio is a relative rate among the risk sets under the proportional-hazards assumption—not a percentage-point change in the probability of re-employment or an expected number of extra months.", "A hazard ratio is not a risk ratio, a survival-probability difference or a duration difference."),
            lesson("Check whether the comparison remains credible over time", "The proportional-hazards assumption says that a covariate’s hazard ratio is stable over the modeled time scale. Plot group-specific survival curves, inspect diagnostics and consider time-varying effects if the policy association changes across the spell. State whether time begins at benefit eligibility, spell start or another landmark; delayed entry, competing events and repeated spells may require further methods. Censoring should be plausibly independent of the event time after conditioning on modeled information, or addressed through an appropriate design or sensitivity analysis.", "Time scale, risk-set definition and censoring process are part of the estimand."),
        ],
        "An employment service follows benefit claimants from the start of an unemployment spell. Some return to work during observation; others remain unemployed when the administrative window closes or move out of the data system. A duration analysis can use each person’s observed time without pretending that all censored spells ended in re-employment, while making the follow-up and censoring assumptions explicit.",
        ["Censoring does not mean that an event occurred at the last observed time.", "A hazard ratio is not a change in the probability of an event by a fixed date.", "A Kaplan–Meier curve does not correct for informative loss to follow-up by itself.", "A model with a fitted hazard is not automatically a causal evaluation."],
        [UCLA_SURVIVAL, SURVIVAL_REVIEW],
        {"question":"What does a right-censored unemployment spell tell the analyst?", "options":["The person was still event-free at least through the recorded follow-up", "The event happened exactly at the censoring date", "The person's duration was zero"], "answerIndex":0, "explanation":"Right-censoring gives a lower bound on the event time. The person contributes observed time at risk up to censoring."}
    ),
    module(
        "spatial-dependence-regional-econometrics", "Spatial Dependence & Regional Econometrics", "Spatial Econometrics", "Intermediate", 40, "spatial",
        "Describe how nearby regions resemble one another, define the neighbourhood rule, and distinguish spatial association from causal spillovers.",
        ["Define a spatial weights matrix and a spatial lag.",
         "Interpret global Moran’s I and a spatial-randomization reference distribution.",
         "Distinguish spatially lagged outcomes from spatially correlated errors and assess sensitivity to neighbourhood choices."],
        [
            lesson("A map is data with a geography", "Regional unemployment or house prices are attached to defined spatial units such as districts or grid cells. Before comparing regions, document boundaries, dates, population denominators and whether the values are rates, totals or model residuals. Aggregation can hide variation within a region, and changing the boundary system can change patterns—a version of the modifiable areal unit problem. A visually appealing map is a useful first check, not an inference method.", "Geographic units and scale shape what spatial patterns can be observed."),
            lesson("Neighbourhoods become a weights matrix", "A spatial weights matrix records which locations count as neighbours and how strongly they contribute. Contiguity links touching polygons; distance bands or nearest neighbours suit other settings. Row-standardizing weights makes a spatial lag resemble a weighted average of neighbouring values, but isolated locations and boundary choices still need explicit handling. There is no universally correct neighbourhood rule: it should reflect the substantive process and be tested for sensitivity.", "The neighbour definition is a modeling decision that changes spatial summaries."),
            lesson("Moran’s I summarizes global similarity among neighbours", "Global Moran’s I compares each region’s deviation from the overall mean with the spatially weighted deviations around it. Positive values indicate that similar values tend to be neighbours; negative values indicate that dissimilar values tend to be neighbours. A permutation reference distribution can show how unusual the observed statistic is under a chosen spatial-randomness null. Neither a large statistic nor a small permutation p-value proves a causal spillover or locates which neighbourhoods drive the pattern.", "Moran’s I is a global association summary conditional on a specified weights matrix.", "I = (n/S₀) · [ΣᵢΣⱼ wᵢⱼ zᵢzⱼ] / [Σᵢ zᵢ²], with zᵢ = yᵢ − ȳ and S₀ = ΣᵢΣⱼwᵢⱼ."),
            lesson("Spatial lag and spatial error tell different stories", "A spatial-lag model includes a weighted average of neighbouring outcomes, which may represent an outcome feedback or spillover mechanism. A spatial-error model instead allows unobserved shocks to be correlated across nearby locations. These are different data-generating stories and require estimators designed for spatial dependence; ordinary least squares with a neighbouring-outcome term is generally not a valid shortcut because that term is endogenous. Economic institutions and timing should determine which story is plausible.", "A spatial lag in outcomes and spatial correlation in unobserved shocks are not interchangeable."),
            lesson("Stress-test the geography and causal claim", "Repeat descriptive diagnostics under defensible alternative weights, check influential regions, inspect residual spatial dependence and report how the map was constructed. A cross-sectional pattern can reflect shared industries, sorting, policies or measurement—not necessarily diffusion across borders. To estimate policy spillovers, define exposure to neighbouring treatment and a comparison strategy that addresses interference and common shocks. Keep the geographic estimand local to the units and network represented in the data.", "Spatial adjustment can describe dependence; causal spillovers still need a research design."),
        ],
        "A regional analyst studies rental inflation around a new commuter rail line. Neighbouring districts may share housing demand, commuters cross boundaries, and treatment exposure depends on distance as well as contiguity. The analyst starts with a transparent spatial weights matrix, maps the outcome and its spatial lag, checks global autocorrelation, then treats any causal spillover as a separate identification question.",
        ["Positive spatial autocorrelation is not evidence that one region caused its neighbour’s outcome.", "Moran’s I depends on the chosen weights matrix and data scale.", "A spatial-lag coefficient should not be estimated by simply adding neighbouring outcomes to ordinary least squares.", "A significant global statistic does not identify which regions form local clusters."],
        [PYSAL, GEODA],
        {"question":"What is a defensible interpretation of positive global Moran’s I?", "options":["Similar values tend to occur among neighbours under the chosen weights", "Changing one region's outcome caused the same change next door", "Every local cluster is statistically significant"], "answerIndex":0, "explanation":"Moran’s I summarizes global spatial association for a specified weights matrix. Causal spillovers and local significance need additional methods and assumptions."}
    ),
]

for item in new_modules:
    if item["id"] not in by_id:
        modules.append(item)
        by_id[item["id"]] = item

follow_up_lessons = {
    "robust-clustered-inference": [
        lesson("Sampling clusters and assignment clusters play different roles", "A district can be a primary sampling unit because it was selected from a survey frame, an assignment cluster because a policy lottery happened at district level, or both. Survey weights and design-based variance estimation describe how sampled units represent the population; cluster-robust causal inference addresses shared treatment assignment or residual shocks. The correct variance method follows the actual sampling and assignment process, and the target population still follows the estimand. Do not assume that calling a variable ‘cluster’ resolves both questions.", "Sampling design and treatment assignment can create different sources of dependence.")
    ],
    "panel-fixed-effects": [
        lesson("Nearby units can share changing shocks", "Unit and time fixed effects remove stable unit differences and common period shocks, but they do not necessarily remove a time-varying shock shared by neighbouring regions. A plant closure, transport disruption or local epidemic can affect nearby units differently over time and leave spatially correlated residuals. Map residual patterns and describe plausible cross-unit links; if spatial dependence is material, use an estimator and uncertainty method matched to the specific lag, error or spillover process. Fixed effects alone do not identify those mechanisms.", "Two-way fixed effects do not automatically absorb changing spatially correlated shocks.")
    ]
}
for module_id, additions in follow_up_lessons.items():
    target = by_id[module_id]
    existing_titles = {item.get("title") for item in target.get("lessons", [])}
    for item in additions:
        if item["title"] not in existing_titles:
            target.setdefault("lessons", []).append(item)
            existing_titles.add(item["title"])

MODULES_PATH.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n")
print(f"Curriculum deepened: {len(modules)} modules, {sum(len(item.get('lessons', [])) for item in modules)} lessons.")
