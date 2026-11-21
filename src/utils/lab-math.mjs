/** @param {number[]} values */
export function median(values) {
  if (!values.length) return Number.NaN;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

/** Linear interpolation between adjacent order statistics. @param {number[]} values @param {number} probability */
export function quantile(values, probability) {
  if (!values.length) return Number.NaN;
  const sorted = [...values].sort((a, b) => a - b);
  const position = Math.max(0, Math.min(1, probability)) * (sorted.length - 1);
  const lower = Math.floor(position);
  const fraction = position - lower;
  return sorted[lower] + fraction * (sorted[Math.min(lower + 1, sorted.length - 1)] - sorted[lower]);
}

/** @param {number[]} values */
export function sampleStandardDeviation(values) {
  if (values.length < 2) return Number.NaN;
  const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
  return Math.sqrt(values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / (values.length - 1));
}

/** @param {number} priorAlpha @param {number} priorBeta @param {number} successes @param {number} failures */
export function betaBinomialPosterior(priorAlpha, priorBeta, successes, failures) {
  if (!(priorAlpha > 0) || !(priorBeta > 0) || successes < 0 || failures < 0) {
    throw new RangeError("Beta prior parameters must be positive and counts non-negative");
  }
  const alpha = priorAlpha + successes;
  const beta = priorBeta + failures;
  return { alpha, beta, mean: alpha / (alpha + beta) };
}

/** @param {number[]} base @param {Array<Array<[number, number]>>} neighbors @param {number} rho @param {number} iterations */
export function spatialAutoregressiveField(base, neighbors, rho, iterations = 60) {
  let values = [...base];
  for (let iteration = 0; iteration < iterations; iteration += 1) {
    values = base.map((baseline, i) => {
      const links = neighbors[i] ?? [];
      const weightTotal = links.reduce((sum, [, weight]) => sum + weight, 0);
      const neighborMean = weightTotal
        ? links.reduce((sum, [j, weight]) => sum + weight * values[j], 0) / weightTotal
        : 0;
      return baseline + rho * neighborMean;
    });
  }
  return values;
}
