export declare function forecastAR1(
  lastObserved: number,
  persistence: number,
  horizon: number,
  innovationSd: number,
): { means: number[]; standardDeviations: number[] };
