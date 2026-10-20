"""Summarize a JMeter results file (.jtl, CSV) and fail if thresholds are broken.

Usage:
    python scripts/check_results.py results/load/results.jtl
    python scripts/check_results.py results.jtl --max-error-pct 1 --max-p95-ms 2000
"""
import argparse
import csv
import math
import sys
from collections import defaultdict


def percentile(values, pct):
    ordered = sorted(values)
    index = max(0, math.ceil(pct / 100 * len(ordered)) - 1)
    return ordered[index]


def main():
    parser = argparse.ArgumentParser(description="Check JMeter results against thresholds.")
    parser.add_argument("jtl", help="Path to the results.jtl CSV file")
    parser.add_argument("--max-error-pct", type=float, default=1.0,
                        help="Fail if the overall error rate is above this percent (default 1)")
    parser.add_argument("--max-p95-ms", type=float, default=2000.0,
                        help="Fail if the overall 95th percentile response time is above this (default 2000)")
    args = parser.parse_args()

    by_label = defaultdict(list)
    errors = defaultdict(int)
    with open(args.jtl, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            label = row["label"]
            by_label[label].append(int(row["elapsed"]))
            if row["success"].strip().lower() != "true":
                errors[label] += 1

    if not by_label:
        print("No samples found in the results file.")
        return 2

    print(f"{'Request':<28}{'Samples':>8}{'Avg ms':>9}{'p95 ms':>9}{'Max ms':>9}{'Errors':>9}")
    all_times = []
    total_errors = 0
    for label, times in by_label.items():
        all_times.extend(times)
        total_errors += errors[label]
        pct = errors[label] / len(times) * 100
        print(f"{label:<28}{len(times):>8}{sum(times) / len(times):>9.0f}"
              f"{percentile(times, 95):>9}{max(times):>9}{pct:>8.1f}%")

    error_pct = total_errors / len(all_times) * 100
    p95 = percentile(all_times, 95)
    print("-" * 71)
    print(f"{'ALL':<28}{len(all_times):>8}{sum(all_times) / len(all_times):>9.0f}"
          f"{p95:>9}{max(all_times):>9}{error_pct:>8.1f}%")

    failed = False
    if error_pct > args.max_error_pct:
        print(f"FAIL: error rate {error_pct:.1f}% is above {args.max_error_pct}%")
        failed = True
    if p95 > args.max_p95_ms:
        print(f"FAIL: p95 {p95} ms is above {args.max_p95_ms:.0f} ms")
        failed = True
    if not failed:
        print("PASS: error rate and p95 are within thresholds")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
