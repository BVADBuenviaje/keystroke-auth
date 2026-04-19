import { Injectable } from '@nestjs/common';

@Injectable()
export class KeystrokeMathService {
  mean(values: number[]): number {
    if (!values.length) return 0;
    return values.reduce((a, b) => a + b, 0) / values.length;
  }

  stddev(values: number[], mean?: number): number {
    if (!values.length) return 0;
    const m = mean ?? this.mean(values);
    const variance = values.reduce((sum, v) => sum + Math.pow(v - m, 2), 0) / values.length;
    return Math.sqrt(variance);
  }

  zScore(value: number, mean: number, stddev: number): number {
    if (stddev === 0) return 0;
    return (value - mean) / stddev;
  }

  // Returns average Z-score for all features
  anomalyScore(
    attempt: Record<string, number>,
    means: Record<string, number>,
    stddevs: Record<string, number>
  ): number {
    const keys = Object.keys(attempt);
    if (!keys.length) return 0;
    const zScores = keys.map((k) => this.zScore(attempt[k], means[k], stddevs[k]));
    return zScores.reduce((a, b) => a + Math.abs(b), 0) / zScores.length;
  }
}
