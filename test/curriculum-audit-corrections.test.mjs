import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const modules = JSON.parse(fs.readFileSync(path.join(root, "src/data/modules.json"), "utf8"));
const seed = JSON.parse(fs.readFileSync(path.join(root, "seed/seed.json"), "utf8"));
const moduleById = (id) => {
  const found = modules.filter((item) => item.id === id);
  assert.equal(found.length, 1, `expected one module ${id}`);
  return found[0];
};
const lessonByTitle = (id, title) => {
  const found = moduleById(id).lessons.filter((item) => item.title === title);
  assert.equal(found.length, 1, `expected one lesson ${id}/${title}`);
  return found[0];
};
const seededModule = (id) => {
  const found = seed.content.modules.filter((item) => item.data.module_key === id);
  assert.equal(found.length, 1, `expected one CMS seed record for ${id}`);
  return found[0];
};
const seededLessons = (id) => JSON.parse(seededModule(id).data.lessons);
const seededLesson = (id, title) => {
  const found = seededLessons(id).filter((item) => item.title === title);
  assert.equal(found.length, 1, `expected one seeded lesson ${id}/${title}`);
  return found[0];
};

test("verified audit calculations and explanations remain in the curriculum source", () => {
  const thinking = moduleById("statistical-thinking");
  assert.match(thinking.quiz.explanation, /mean.*median/is);
  assert.match(lessonByTitle("statistical-thinking", "Compare center and spread with a worked example").body, /median remains −0\.30 pp/);

  assert.match(moduleById("distributions").caseStudy, /166 complete non-overlapping blocks of 60 observations \(leaving 40 draws unused\)/);
  assert.match(lessonByTitle("returns-risk", "Compound wealth and annualize with care").body, /\(1\.0395\)\^4 − 1 ≈ 16\.7% per year/);
  assert.doesNotMatch(lessonByTitle("returns-risk", "Compound wealth and annualize with care").body, /16\.8% per year/);

  const eda = lessonByTitle("exploratory-data-analysis", "Ask what one row represents").body;
  assert.match(eda, /four intended fund-month keys but only three observed return values/);
  assert.match(eda, /Fund B’s February return is missing, not 0%/);
  assert.match(lessonByTitle("bayesian", "Communicate Bayesian evidence responsibly").body, /NIST — Bayesian Methods/);
  assert.doesNotMatch(lessonByTitle("bayesian", "Communicate Bayesian evidence responsibly").body, /MIT OCW — Analytics of Finance/);

  const panel = lessonByTitle("panel-fixed-effects", "The within transformation shows what identifies a fixed-effects estimate");
  assert.match(panel.formula, /\(Xᵢₜ − X̄ᵢ\)′γ/);
  assert.match(panel.body, /time-invariant regressor becomes zero/);

  const pooling = lessonByTitle("multilevel-partial-pooling", "Why a group label can matter").body;
  assert.match(pooling, /Office A pays £20 and £24 per hour and Office B pays £26 and £30/);
  assert.match(pooling, /£28 − £22 = £6 per hour/);
  assert.doesNotMatch(pooling, /centre averages are £22 and £28/);

  const synthetic = lessonByTitle("synthetic-control", "Use placebos as a reference, not a magic test").body;
  assert.match(synthetic, /75% of the placebo gaps are smaller/);
  assert.doesNotMatch(synthetic, /80% of the gaps are smaller/);

  const spatial = lessonByTitle("spatial-dependence-regional-econometrics", "Spatial lag and spatial error tell different stories").body;
  assert.match(spatial, /spatial lags are \(−0\.5, −0\.25, 0\.25, 0\.5\)/);
  assert.match(spatial, /1\.25\/2\.5 = 0\.50/);
  assert.doesNotMatch(spatial, /1\/2\.5 = 0\.40/);

  const measurement = lessonByTitle("measurement-error-economics", "Classical predictor error can flatten a slope").body;
  assert.match(measurement, /\(9\/13\) × £40 = £27\.69/);
  assert.doesNotMatch(measurement, /£27\.70/);
  assert.doesNotMatch(lessonByTitle("price-indices-real-values", "Understand the base and the weights").body, /1\.0417\/1\.0560/);
});

test("audit citations identify the sources actually supporting each claim", () => {
  const sources = (id) => moduleById(id).sources;
  assert.ok(sources("statistical-thinking").some((s) => s.url.endsWith("/section3/histogra.htm")));
  assert.ok(sources("time-series").some((s) => s.url.endsWith("/section4/pmc446.htm")));
  const timeScaleBody = lessonByTitle("time-series", "Choose a time scale and avoid spurious patterns").body;
  assert.match(timeScaleBody, /NIST — Box-Jenkins Model Identification \(ACF and PACF\)/);
  assert.doesNotMatch(timeScaleBody, /NIST — Time Series and Autocorrelation/);
  assert.ok(sources("regression").some((s) => s.url.endsWith("/Lesson07.html")));
  assert.ok(sources("kernel-density").some((s) => s.url.includes("statsmodels.org/devel/generated/statsmodels.nonparametric.kernel_regression.KernelReg.html")));
  assert.ok(sources("heterogeneous-effects").some((s) => s.url.endsWith("/Lecture-FDR.pdf")));
  assert.ok(sources("spatial-dependence-regional-econometrics").some((s) => s.url.endsWith("/15_ML_estimation_spatial_error.html")));
  assert.match(lessonByTitle("kernel-density", "Bandwidth is the main smoothing decision").body, /SciPy’s gaussian_kde uses Scott’s factor by default/);
  assert.match(lessonByTitle("heterogeneous-effects", "Keep discovery and confirmation distinct").body, /Multiple Hypothesis Testing and False Discovery Rate Notes/);
});

test("seeded CMS lessons retain the audit corrections after catalog generation", () => {
  const seededPool = seededLesson("multilevel-partial-pooling", "Why a group label can matter").body;
  assert.match(seededPool, /Office A pays £20 and £24 per hour and Office B pays £26 and £30/);
  const seededSpatial = seededLesson("spatial-dependence-regional-econometrics", "Spatial lag and spatial error tell different stories").body;
  assert.match(seededSpatial, /1\.25\/2\.5 = 0\.50/);
  const seededReturns = seededLesson("returns-risk", "Compound wealth and annualize with care").body;
  assert.match(seededReturns, /16\.7% per year/);
  const seededDistributionCaseStudy = seededModule("distributions").data.case_study;
  assert.match(seededDistributionCaseStudy, /166 complete non-overlapping blocks of 60 observations \(leaving 40 draws unused\)/);
  assert.doesNotMatch(seededDistributionCaseStudy, /1,000 non-overlapping blocks of 60 observations/);
});

test("statistical power diagram shades the rejection tail under the specified alternative", () => {
  const svg = fs.readFileSync(path.join(root, "public/diagrams/statistical-power-planning.svg"), "utf8");
  const diagramAlt = moduleById("statistical-power-planning").diagramAlt;
  assert.match(svg, /fill="#d9f0e4"/);
  assert.match(svg, /right-tail cutoff/);
  assert.match(svg, /power under H₁/);
  assert.match(diagramAlt, /shaded right tail under the specified alternative H₁/);
});
