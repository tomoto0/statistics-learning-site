import test from 'node:test';
import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = process.cwd();
const diagramsDir = resolve(root, 'public/diagrams');
const cardsDir = resolve(root, 'public/images/module-cards');
const read = (path) => readFileSync(resolve(root, path), 'utf8');

test('the two-group, two-period DiD lesson, card, and interactive lab agree', () => {
  const modules = JSON.parse(read('src/data/modules.json'));
  const module = modules.find((item) => item.slug === 'difference-in-differences');
  assert.ok(module, 'DiD module is present');
  assert.equal(module.lab, 'did');
  assert.equal(module.diagram, '/diagrams/difference-in-differences.svg');

  const svg = read('public/diagrams/difference-in-differences.svg');
  for (const label of [
    'Pre', 'Post', 'Mean outcome (illustrative units)',
    'Treated · observed', 'Comparison · observed',
    'Treated · untreated counterfactual', '50', '48', '56', '53 · unobserved', '51',
    'DiD = 3 units', '(56 − 50) − (51 − 48) = 3', 'parallel trends',
    'ORIGINAL SCHEMATIC · NOT DATA'
  ]) assert.ok(svg.includes(label), `specialist DiD figure includes ${label}`);

  const card = read('public/images/module-cards/difference-in-differences.svg');
  for (const label of ['50', '48', '56', '53', '51', 'difference in changes']) {
    assert.ok(card.toLowerCase().includes(label.toLowerCase()), `DiD card includes ${label}`);
  }

  const lab = read('src/scripts/applied-econometrics-labs.ts');
  assert.ok(lab.includes('preT=50,preC=48,postC=51'));
  assert.ok(lab.includes('postT=preT+(postC-preC)+tau+violation'));
  assert.ok(lab.includes('Treated change ΔT'));
  assert.ok(lab.includes('Comparison change ΔC'));
  assert.ok(lab.includes('DiD = (Tpost − Tpre) − (Cpost − Cpre)'));
  assert.ok(lab.includes('gapX=652'));
  assert.ok(lab.includes('txt(svg,gapX+10'));
});

test('IV figures show the confounder pointing to treatment and outcome, with no direct instrument path', () => {
  const specialist = read('public/diagrams/iv-2sls.svg');
  assert.ok(specialist.includes('x1="416" y1="164" x2="416" y2="111"'));
  assert.ok(specialist.includes('x1="437" y1="176" x2="566" y2="135"'));
  assert.ok(specialist.includes('No direct Z → Y path (exclusion)'));
  assert.ok(!specialist.includes('x1="416" y1="111" x2="416" y2="164"'), 'the causal arrow is not reversed');

  const card = read('public/images/module-cards/iv-2sls.svg');
  assert.ok(card.includes('x1="300" y1="242" x2="300" y2="161"'));
  assert.ok(card.includes('x1="326" y1="256" x2="412" y2="224"'));
  assert.equal((card.match(/Exclusion assumption: no direct Z → Y path/g) ?? []).length, 1, 'the exclusion explanation is not duplicated');
});

test('all specialist diagrams have accessible names and distinguish schematic from data', () => {
  const files = readdirSync(diagramsDir).filter((file) => file.endsWith('.svg')).sort();
  assert.equal(files.length, 22, 'all 22 specialist diagram assets are present');
  for (const file of files) {
    const svg = read(`public/diagrams/${file}`);
    assert.match(svg, /<title\b[^>]*>/, `${file} has a title`);
    assert.match(svg, /<desc\b[^>]*>/, `${file} has a description`);
    assert.match(svg, /(?:ORIGINAL SCHEMATIC|CONCEPT) · NOT DATA/, `${file} states it is not measured data`);
  }
});

test('quantitative specialist figures name their axes, units, and plotting scale', () => {
  const expectedLabels = {
    'regression-discontinuity.svg': ['Assignment score (illustrative units; cutoff = 0)', 'Outcome (illustrative units)', '>0</text>', '>10</text>', '>20</text>'],
    'synthetic-control.svg': ['Time (periods)', 'Outcome (illustrative units)', '>0</text>', '>5</text>', '>10</text>'],
    'matching-weighting.svg': ['Standardized mean difference (SD units)', 'Before match/weight', 'After match/weight'],
    'heterogeneous-effects.svg': ['Effect estimate (illustrative outcome units)', 'Zero effect', '>-3</text>', '>3</text>'],
    'limited-outcomes.svg': ['Predicted probability', 'Count outcome value', 'Binary outcome Y ∈ {0,1}'],
    'functional-form-specification.svg': ['Predictor X (illustrative units)', 'Outcome (units)', 'Residual (units)', 'Fitted value (illustrative units)'],
    'applied-macro-time-series.svg': ['Time (periods)', 'Series value (illustrative units)', '>0</text>', '>10</text>', '>20</text>', '>16</text>'],
    'bootstrap-inference.svg': ['Observed', 'Empirical', 'n with replacement', 'T* by resample number', 'Histogram of T*', 'Trace: replicate stability'],
    'statistical-power-planning.svg': ['Choose meaningful δ', 'Evaluate power', 'P(reject H₀ | δ)', 'right-tail cutoff', 'power under H₁', 'Power across independent n', 'Precision plans target interval width'],
    'measurement-error-economics.svg': ['Latent quantity X', 'X* = X + measurement error u', 'Slope may flatten only under classical-error assumptions'],
    'price-indices-real-values.svg': ['weighted basket', 'base period = 100', 'Real value = nominal', '÷ (index / 100)']
    ,'regularization-cross-validation.svg': ['Coefficient paths', 'validation', 'bias–variance trade-off']
    ,'meta-analysis-evidence-synthesis.svg': ['Individual estimates', 'Fixed summary', 'Random-effects summary']
    ,'causal-mediation-mechanisms.svg': ['Treatment, mediator, outcome', 'possible mediator–outcome confounding', 'direct path c′']
    ,'partial-identification-bounds.svg': ['Compatible treatment-effect set', '−0.029 to +0.311', 'Binary outcome']
  };
  for (const [file, labels] of Object.entries(expectedLabels)) {
    const svg = read(`public/diagrams/${file}`);
    for (const label of labels) assert.ok(svg.includes(label), `${file} includes ${label}`);
  }
  const labs = read('src/scripts/applied-econometrics-labs.ts');
  assert.ok(labs.includes('Bootstrap trace · T* by replicate'));
  assert.ok(labs.includes('Bootstrap distribution · median T*'));
  assert.ok(labs.includes('Bootstrap SE of median'));
  assert.ok(labs.includes('sampleStandardDeviation(boot)'));
  assert.ok(labs.includes('Bootstrap median (synthetic units)'));
});

test('module-card legends clarify the key encodings that could otherwise be confused', () => {
  const expectedLabels = {
    'statistical-thinking.svg': ['mean (coral)', 'median (mint)', 'distant tail bin'],
    'panel-fixed-effects.svg': ['Unit 1', 't1', 't5', 'Outcome (illustrative units)'],
    'matching-weighting.svg': ['Treated', 'Comparison', 'After weights'],
    'synthetic-control.svg': ['Weighted synthetic', 'Treated'],
    'limited-outcomes.svg': ['Linear probability', 'Logit'],
    'applied-macro-time-series.svg': ['Observed', 'Forecast mean', 'Uncertainty'],
    'spatial-dependence-regional-econometrics.svg': ['Cell shading', 'Neighbor link'],
    'bootstrap-inference.svg': ['Resample with replacement', 'statistic distribution'],
    'statistical-power-planning.svg': ['Power rises with n', 'meaningful effect'],
    'measurement-error-economics.svg': ['Latent X', 'noisy X*', 'attenuation'],
    'price-indices-real-values.svg': ['Basket weights', 'price index', 'real value']
  };
  for (const [file, labels] of Object.entries(expectedLabels)) {
    const svg = read(`public/images/module-cards/${file}`);
    for (const label of labels) assert.ok(svg.includes(label), `${file} includes ${label}`);
  }
});

test('the complete set of 42 module-card illustrations is generated', () => {
  const files = readdirSync(cardsDir).filter((file) => file.endsWith('.svg'));
  assert.equal(files.length, 42);
});
