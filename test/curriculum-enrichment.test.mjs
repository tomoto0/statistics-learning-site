import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const modules = JSON.parse(fs.readFileSync(path.join(root, "src/data/modules.json"), "utf8"));
const bySlug = new Map(modules.map((module) => [module.slug, module]));

const additions = {
  "research-design": "The same design can identify different target effects",
  "experimental-design": "Use pre-treatment measures for precision, not post-assignment filters",
  "iv-2sls": "Weak instruments make conventional intervals fragile",
  "difference-in-differences": "Calculate the contrast before reading a regression table",
  "regression-discontinuity": "The bandwidth trades locality against precision",
  "panel-fixed-effects": "The within transformation shows what identifies a fixed-effects estimate",
  "robust-clustered-inference": "Cluster where assignment and shocks are shared",
  "matching-weighting": "Weighting choices define which population the contrast describes",
  "synthetic-control": "Compare placebo units only when their pre-policy fit is comparable",
  "limited-outcomes": "Translate nonlinear coefficients onto the probability scale",
  "selection-missing-data": "Conditioning on who is observed can change the estimand",
  "heterogeneous-effects": "Test the difference between groups directly",
  "functional-form-specification": "Trace omitted-variable bias through two relationships",
  "applied-macro-time-series": "Serial dependence means monthly rows are not monthly experiments",
};

const citedModules = [
  "research-design", "experimental-design", "iv-2sls", "difference-in-differences",
  "regression-discontinuity", "panel-fixed-effects", "robust-clustered-inference",
  "matching-weighting", "limited-outcomes", "selection-missing-data",
  "heterogeneous-effects", "functional-form-specification", "applied-macro-time-series",
  "regression",
];

test("the applied-econometrics follow-up lessons are present exactly once", () => {
  assert.equal(modules.length, 42);
  assert.equal(modules.reduce((total, module) => total + module.lessons.length, 0), 238);
  assert.equal(new Set(modules.map((module) => module.slug)).size, modules.length);
  for (const [slug, title] of Object.entries(additions)) {
    const module = bySlug.get(slug);
    assert.ok(module, `missing module ${slug}`);
    assert.equal(module.lessons.filter((lesson) => lesson.title === title).length, 1, `${slug}: ${title}`);
    assert.equal(new Set(module.lessons.map((lesson) => lesson.title)).size, module.lessons.length, `${slug} has duplicate lesson titles`);
  }
});

test("the four new topics are distinct, sourced, and have their matching interactive labs", () => {
  const expected = {
    "multilevel-partial-pooling": ["Multilevel Models & Partial Pooling", "pooling", "Multilevel Models", "https://www.pymc.io/projects/examples/en/latest/case_studies/hierarchical_partial_pooling.html"],
    "complex-survey-sampling": ["Survey Sampling & Complex Designs", "survey", "Survey Methods", "https://online.stat.psu.edu/stat506/"],
    "survival-duration-analysis": ["Survival & Duration Analysis", "survival", "Survival Analysis", "https://stats.oarc.ucla.edu/wp-content/uploads/2025/02/survival_r_full.html"],
    "spatial-dependence-regional-econometrics": ["Spatial Dependence & Regional Econometrics", "spatial", "Spatial Econometrics", "https://pysal.org/esda/stable/user-guide/global_morans_i.html"],
  };
  for (const [slug, [title, lab, category, sourceUrl]] of Object.entries(expected)) {
    const module = bySlug.get(slug);
    assert.ok(module, `missing new module ${slug}`);
    assert.equal(module.title, title);
    assert.equal(module.lab, lab);
    assert.equal(module.category, category);
    assert.ok(module.lessons.length >= 5, `${slug}: expected five distinct guided lessons`);
    assert.ok(module.sources.some((source) => source.url === sourceUrl), `${slug}: missing verified source`);
    assert.equal(new Set(module.lessons.map((lesson) => lesson.title)).size, module.lessons.length, `${slug} has duplicate lesson titles`);
    assert.ok(module.quiz?.options?.length >= 3, `${slug}: missing knowledge check`);
  }
});

test("the four new applied-statistics topics have sources, diagrams, cards and dedicated labs", () => {
  const expected = {
    "bootstrap-inference": ["Bootstrap Inference & Resampling", "bootstrap", "https://www.itl.nist.gov/div898/handbook/eda/section3/bootplot.htm"],
    "statistical-power-planning": ["Statistical Power & Sample-Size Planning", "powerplan", "https://online.stat.psu.edu/statprogram/reviews/statistical-concepts/power-analysis"],
    "measurement-error-economics": ["Measurement Error in Economic Data", "measurement", "https://unstats.un.org/unsd/hhsurveys/pdf/chapter_9.pdf"],
    "price-indices-real-values": ["Price Indices & Real Economic Values", "priceindex", "https://www.bls.gov/opub/hom/cpi/concepts.htm"],
  };
  for (const [slug, [title, lab, sourceUrl]] of Object.entries(expected)) {
    const module = bySlug.get(slug);
    assert.ok(module, `missing module ${slug}`);
    assert.equal(module.title, title);
    assert.equal(module.lab, lab);
    assert.ok(module.lessons.length >= 5, `${slug}: expected five guided lessons`);
    assert.ok(module.sources.some((source) => source.url === sourceUrl), `${slug}: missing opened source`);
    assert.ok(module.diagram?.endsWith(`${slug}.svg`), `${slug}: missing diagram`);
    assert.ok(module.diagramAlt && module.diagramCaption, `${slug}: missing accessible diagram text`);
    assert.equal(module.cardImage, `/images/module-cards/${slug}.svg`);
    assert.equal(new Set(module.lessons.map((lesson) => lesson.title)).size, module.lessons.length);
    assert.ok(module.quiz?.options?.length >= 3, `${slug}: missing quiz`);
  }
  const requiredSources = {
    "bootstrap-inference": [
      "https://online.stat.psu.edu/stat555/node/119/",
      "https://www.degruyterbrill.com/document/doi/10.1515/9781400829828-013/html",
      "https://ocw.mit.edu/courses/14-387-applied-econometrics-mostly-harmless-big-data-fall-2014/pages/readings/",
    ],
    "statistical-power-planning": [
      "https://online.stat.psu.edu/stat509/Lesson08.html",
      "https://www.degruyterbrill.com/document/doi/10.1515/9781400829828-007/html",
      "https://mixtape.scunning.com/04-potential_outcomes_and_randomization",
    ],
    "measurement-error-economics": [
      "https://www.degruyterbrill.com/document/doi/10.1515/9781400829828-008/html",
    ],
  };
  for (const [slug, urls] of Object.entries(requiredSources)) {
    const module = bySlug.get(slug);
    for (const url of urls) assert.ok(module.sources.some((source) => source.url === url), `${slug}: missing teaching/textbook source ${url}`);
  }
  assert.ok(bySlug.get("bootstrap-inference").lessons.some((lesson) => lesson.title === "Choose a bootstrap model and inspect its output"));
  assert.ok(bySlug.get("bootstrap-inference").lessons.some((lesson) => lesson.title === "Connect bootstrap intervals to econometric inference"));
  assert.ok(bySlug.get("statistical-power-planning").lessons.some((lesson) => lesson.title === "Choose a precision target or a power target"));
  assert.ok(bySlug.get("statistical-power-planning").lessons.some((lesson) => lesson.title === "Start with a decision-relevant causal target"));
  assert.ok(bySlug.get("statistical-power-planning").lessons.some((lesson) => lesson.title === "Power cannot repair a weak design"));
});

test("four distinct curriculum gaps have original lessons, verified sources, diagrams, cards and labs", () => {
  const expected = {
    "regularization-cross-validation": ["Regularization, Cross-Validation & Prediction", "regularization", "Modelling", "https://www.statlearning.com/"],
    "meta-analysis-evidence-synthesis": ["Meta-Analysis & Evidence Synthesis for Economics", "metaanalysis", "Inference & Research", "https://chabefer.github.io/STCI/meta.html"],
    "causal-mediation-mechanisms": ["Causal Mediation & Mechanism Analysis", "mediation", "Applied Econometrics", "https://imai.fas.harvard.edu/research/files/BaronKenny.pdf"],
    "partial-identification-bounds": ["Partial Identification, Bounds & Sensitivity", "partialid", "Inference & Research", "https://theeffectbook.net/ch-PartialIdentification.html"],
  };
  for (const [slug, [title, lab, category, sourceUrl]] of Object.entries(expected)) {
    const module = bySlug.get(slug);
    assert.ok(module, `missing gap-filling module ${slug}`);
    assert.equal(module.title, title);
    assert.equal(module.lab, lab);
    assert.equal(module.category, category);
    assert.ok(module.lessons.length >= 5, `${slug}: expected five guided lessons`);
    assert.equal(new Set(module.lessons.map((lesson) => lesson.title)).size, module.lessons.length, `${slug}: duplicate lesson titles`);
    assert.ok(module.sources.some((source) => source.url === sourceUrl), `${slug}: missing opened source`);
    assert.ok(module.diagram?.endsWith(`${slug}.svg`), `${slug}: missing teaching diagram`);
    assert.ok(module.diagramAlt && module.diagramCaption, `${slug}: missing accessible diagram text`);
    assert.equal(module.cardImage, `/images/module-cards/${slug}.svg`);
    assert.ok(module.quiz?.options?.length >= 3, `${slug}: missing knowledge check`);
  }
});

test("existing inference and panel lessons add focused, non-duplicative bridges", () => {
  assert.equal(bySlug.get("robust-clustered-inference").lessons.filter((lesson) => lesson.title === "Sampling clusters and assignment clusters play different roles").length, 1);
  assert.equal(bySlug.get("panel-fixed-effects").lessons.filter((lesson) => lesson.title === "Nearby units can share changing shocks").length, 1);
});

test("book sources link to the publisher and identify relevant chapters", () => {
  const publisherUrl = "https://press.princeton.edu/books/paperback/9780691120355/mostly-harmless-econometrics";
  for (const slug of citedModules) {
    const module = bySlug.get(slug);
    const reference = module.sources.find((source) => source.label.startsWith("Angrist & Pischke (2008), Mostly Harmless Econometrics, Ch"));
    assert.ok(reference, `${slug} is missing its chapter-specific book citation`);
    assert.equal(reference.url, publisherUrl, `${slug} citation should point to the publisher record`);
  }
  assert.equal(bySlug.get("synthetic-control").sources.some((source) => source.label.startsWith("Angrist & Pischke (2008), Mostly Harmless Econometrics, Ch")), false,
    "do not cite a book chapter for synthetic control when the text does not cover that method");
});
