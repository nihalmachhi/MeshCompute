export interface PeriodicityResult {
  score: number;
  period_s: number;
  interval_cv: number;
  within_ten_percent: number;
  mad_s: number;
  robust_cv: number;
  autocorrelation: number;
}

function median(values: number[]): number {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

function lagAutocorrelation(values: number[], lag = 1): number {
  if (values.length <= lag) return 0;
  const left = values.slice(0, values.length - lag);
  const right = values.slice(lag);
  const lm = left.reduce((a, b) => a + b, 0) / left.length;
  const rm = right.reduce((a, b) => a + b, 0) / right.length;
  const num = left.reduce((s, v, i) => s + (v - lm) * (right[i] - rm), 0);
  const lv = left.reduce((s, v) => s + (v - lm) ** 2, 0);
  const rv = right.reduce((s, v) => s + (v - rm) ** 2, 0);
  const den = Math.sqrt(lv * rv);
  if (den === 0) return 1;
  return Math.max(-1, Math.min(1, num / den));
}

export function periodicityScore(times: number[]): PeriodicityResult {
  const ordered = [...times].sort((a, b) => a - b);
  const intervals = ordered.slice(1).map((v, i) => v - ordered[i]);
  if (intervals.length < 3) {
    return { score: 0, period_s: 0, interval_cv: 0, within_ten_percent: 0, mad_s: 0, robust_cv: 0, autocorrelation: 0 };
  }
  const center = median(intervals);
  const deviations = intervals.map((v) => Math.abs(v - center));
  const mad = median(deviations);
  const robust_cv = center ? (1.4826 * mad) / center : 0;
  const mean = intervals.reduce((a, b) => a + b, 0) / intervals.length;
  const variance = intervals.reduce((s, v) => s + (v - mean) ** 2, 0) / intervals.length;
  const classic_cv = center ? Math.sqrt(variance) / center : 0;
  const regular = intervals.filter((v) => Math.abs(v - center) <= center * 0.1).length / intervals.length;
  const autocorrelation = lagAutocorrelation(intervals);
  const score = 0.55 * regular + 0.3 * (1 - Math.min(robust_cv, 1)) + 0.15 * Math.max(0, autocorrelation);
  return {
    score: Math.max(0, Math.min(1, Number(score.toFixed(4)))),
    period_s: Number(center.toFixed(3)),
    interval_cv: Number(classic_cv.toFixed(4)),
    within_ten_percent: Number(regular.toFixed(4)),
    mad_s: Number(mad.toFixed(4)),
    robust_cv: Number(robust_cv.toFixed(4)),
    autocorrelation: Number(autocorrelation.toFixed(4)),
  };
}