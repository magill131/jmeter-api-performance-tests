#!/usr/bin/env bash
# Runs the JMeter test plan for one scenario and checks the results.
# Usage: ./scripts/run_load_test.sh smoke|load|stress
# JMeter is found through $JMETER_HOME, or "jmeter" on the PATH.
set -euo pipefail

scenario="${1:-smoke}"
case "$scenario" in
  smoke)  threads=1;  rampup=1;  loops=1 ;;
  load)   threads=20; rampup=20; loops=10 ;;
  stress) threads=40; rampup=30; loops=10 ;;
  *) echo "Usage: $0 smoke|load|stress"; exit 2 ;;
esac

out="results/$scenario"
rm -rf "$out"
mkdir -p "$out"

if [ -n "${JMETER_HOME:-}" ]; then
  jmeter="$JMETER_HOME/bin/jmeter"
else
  jmeter="jmeter"
fi

"$jmeter" -n -t jmeter/api_load_test.jmx \
  -l "$out/results.jtl" -e -o "$out/report" \
  -Jthreads="$threads" -Jrampup="$rampup" -Jloops="$loops"

python3 scripts/check_results.py "$out/results.jtl"
