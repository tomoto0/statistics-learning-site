import assert from "node:assert/strict";
import test from "node:test";
import { betaBinomialPosterior, median, quantile, sampleStandardDeviation, spatialAutoregressiveField } from "../src/utils/lab-math.mjs";

 test("median averages the two central observations for even samples", () => {
  assert.equal(median([-0.4, -0.2, 0.1, 0.3]), -0.05);
  assert.equal(median([5, 1, 9]), 5);
});

test("linear quantiles interpolate and sample standard deviation uses n - 1", () => {
  assert.equal(quantile([0, 10], 0.25), 2.5);
  assert.equal(sampleStandardDeviation([1, 3]), Math.SQRT2);
});

test("Beta-Binomial update uses the observed successes and failures", () => {
  const posterior = betaBinomialPosterior(2, 8, 3, 2);
  assert.equal(posterior.alpha, 5);
  assert.equal(posterior.beta, 10);
  assert.equal(posterior.mean, 1 / 3);
  assert.throws(() => betaBinomialPosterior(0, 8, 3, 2), /positive/);
});

test("spatial autoregressive iteration converges to the fixed-baseline equation", () => {
  const values = spatialAutoregressiveField([1, 0], [[[1, 1]], [[0, 1]]], 0.5, 60);
  assert.ok(values.every(Number.isFinite));
  assert.ok(Math.abs(values[0] - 4 / 3) < 1e-9);
  assert.ok(Math.abs(values[1] - 2 / 3) < 1e-9);
  assert.ok(Math.abs(values[0] - (1 + 0.5 * values[1])) < 1e-9);
  assert.ok(Math.abs(values[1] - 0.5 * values[0]) < 1e-9);
});
