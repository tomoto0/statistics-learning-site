import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { extractTutorText } from "../src/utils/tutor-answer.mjs";
import { forecastAR1 } from "../src/utils/ar1-forecast.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const modules = JSON.parse(fs.readFileSync(path.join(root, "src/data/modules.json"), "utf8"));
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");
const keysFrom = (source, expression) => {
  const match = source.match(expression);
  assert.ok(match, `could not find mapping: ${expression}`);
  return new Set([...match[1].matchAll(/(?:^|,)\s*([A-Za-z][A-Za-z0-9_-]*)\s*:/gm)].map((item) => item[1]));
};
const keysFromAll = (source, expression) => new Set([...source.matchAll(expression)].flatMap((match) => [...match[1].matchAll(/(?:^|,)\s*([A-Za-z][A-Za-z0-9_-]*)\s*:/gm)].map((item) => item[1])));

test("all 42 module cards have a unique, accessible 3:2 SVG illustration", () => {
  assert.equal(modules.length, 42);
  const images = modules.map((module) => module.cardImage);
  assert.equal(new Set(images).size, 42);
  for (const module of modules) {
    assert.match(module.cardImage, /^\/images\/module-cards\/[a-z0-9-]+\.svg$/);
    const svg = fs.readFileSync(path.join(root, "public", module.cardImage.slice(1)), "utf8");
    assert.match(svg, /viewBox="0 0 600 400"/);
    assert.match(svg, /<title\b/);
    assert.match(svg, /<desc\b/);
    for (const asset of [module.visual, module.diagram].filter(Boolean)) {
      assert.ok(fs.existsSync(path.join(root, "public", asset.replace(/^\//, ""))), `${module.id}: missing ${asset}`);
    }
    assert.ok(module.lessons.length >= 4, `${module.id}: expected guided lessons`);
  }
  const home = read("src/pages/index.astro");
  const css = read("src/styles/site.css");
  assert.match(home, /cardImage:.*bundled\?\.cardImage/s);
  assert.match(home, /module\.cardImage && <img class="module-card-visual"/);
  assert.match(css, /\.module-card-visual\{[^}]*aspect-ratio:3\/2/);
  assert.doesNotMatch(css, /\.module-card-visual\{[^}]*height:132px/);
});

test("every module has controls, a label, a description and a chart renderer", () => {
  const page = read("src/pages/modules/[slug].astro");
  const basic = read("src/scripts/learning-lab.ts");
  const applied = read("src/scripts/applied-econometrics-labs.ts");
  const controls = keysFrom(page, /const controlSets:[\s\S]*?=\s*\{([\s\S]*?)\n\};/);
  const oldRenderer = keysFrom(basic, /const drawByKind:[\s\S]*?=\s*\{([\s\S]*?)\};/);
  const appliedRenderer = keysFrom(applied, /const draw:Record[\s\S]*?=\s*\{([\s\S]*?)\};/);
  const labels = new Set([
    ...keysFrom(page, /const labTitles:[\s\S]*?=\s*\{([\s\S]*?)\n\};/),
    ...keysFromAll(page, /Object\.assign\(labTitles,\s*\{([\s\S]*?)\}\);/g),
  ]);
  const descriptions = new Set([
    ...keysFrom(page, /const labDescriptions:[\s\S]*?=\s*\{([\s\S]*?)\n\};/),
    ...keysFromAll(page, /Object\.assign\(labDescriptions,\s*\{([\s\S]*?)\}\);/g),
  ]);
  for (const module of modules) {
    assert.ok(controls.has(module.lab), `${module.id}: no controls for ${module.lab}`);
    assert.ok(labels.has(module.lab), `${module.id}: no title for ${module.lab}`);
    assert.ok(descriptions.has(module.lab), `${module.id}: no description for ${module.lab}`);
    assert.ok(oldRenderer.has(module.lab) || appliedRenderer.has(module.lab), `${module.id}: no renderer for ${module.lab}`);
  }
});

test("Ask extracts learner-facing text but never exposes internal reasoning", () => {
  assert.equal(extractTutorText({ choices: [{ message: { content: "  A p-value is conditional on the null.  " } }] }), "A p-value is conditional on the null.");
  assert.equal(extractTutorText({ response: "Fallback answer" }), "Fallback answer");
  assert.equal(extractTutorText({ choices: [{ message: { content: [{ type: "text", text: "First part" }, { type: "text", text: "Second part" }] } }] }), "First part\nSecond part");
  assert.equal(extractTutorText({ choices: [{ message: { content: null, reasoning_content: "private reasoning" } }] }), "");
});

test("interactive lab edge controls keep points in view and calculations explicit", () => {
  const page = read("src/pages/modules/[slug].astro");
  const basic = read("src/scripts/learning-lab.ts");
  const applied = read("src/scripts/applied-econometrics-labs.ts");
  assert.match(page, /pvalue:\[\{key:"effect",label:[^,]+,min:-\.6,max:\.6/);
  assert.match(page, /key:"failures",label:"Observed failures"/);
  assert.match(basic, /xMax=Math\.max\(5,Math\.ceil\(Math\.abs\(z\)\+1\)\)/);
  assert.match(basic, /rawMin=Math\.min\(\.\.\.means\),rawMax=Math\.max\(\.\.\.means\)/);
  assert.match(applied, /xMax=Math\.ceil\(Math\.max\(300,n,req\)\/100\)\*100/);
  assert.match(applied, /chosenOnRight\?chosenX-7:chosenX\+7/);
  assert.match(applied, /bootSe=sampleStandardDeviation\(boot\)/);
  assert.match(applied, /const values=spatialAutoregressiveField\(base,neighbors,rho,60\)/);
  assert.ok(applied.includes("Period (1–2 = pre; 3 = post)"));
  assert.ok(applied.includes("Treatment begins"));
  assert.ok(applied.includes("Difference in changes (DiD)"));
  assert.ok(applied.includes("The lesson covers the spatial-randomization reference distribution"));
  assert.ok(page.includes("randomization-reference inference is covered in the lesson"));
});

test("AR(1) forecasts shrink toward the zero long-run mean and uncertainty accumulates", () => {
  const result = forecastAR1(10, 0.5, 3, 0.6);
  assert.deepEqual(result.means, [5, 2.5, 1.25]);
  assert.deepEqual(result.standardDeviations.map((value) => Number(value.toFixed(6))), [0.6, 0.67082, 0.687386]);
  assert.throws(() => forecastAR1(10, 1, 3, 0.6), /stationary/);
  const macroLab = read("src/scripts/applied-econometrics-labs.ts");
  assert.match(macroLab, /forecastAR1\(last,phi,h,\.6\)/);
  assert.match(macroLab, /el\("polygon"/);
  assert.doesNotMatch(macroLab, /last\+val/);
});
