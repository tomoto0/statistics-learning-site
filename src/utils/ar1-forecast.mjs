export function forecastAR1(lastObserved, persistence, horizon, innovationSd) {
  if (!Number.isFinite(lastObserved)) throw new RangeError("lastObserved must be finite");
  if (!Number.isFinite(persistence) || Math.abs(persistence) >= 1) throw new RangeError("persistence must be finite and stationary");
  if (!Number.isInteger(horizon) || horizon < 1) throw new RangeError("horizon must be a positive integer");
  if (!Number.isFinite(innovationSd) || innovationSd < 0) throw new RangeError("innovationSd must be finite and non-negative");

  const means = [];
  const standardDeviations = [];
  let forecastVariance = 0;
  for (let step = 1; step <= horizon; step += 1) {
    means.push(Math.pow(persistence, step) * lastObserved);
    forecastVariance = innovationSd ** 2 + persistence ** 2 * forecastVariance;
    standardDeviations.push(Math.sqrt(forecastVariance));
  }
  return { means, standardDeviations };
}
