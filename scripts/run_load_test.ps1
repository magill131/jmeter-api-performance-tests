# Runs the JMeter test plan for one scenario and checks the results.
# Usage: .\scripts\run_load_test.ps1 -Scenario smoke|load|stress
# JMeter is found through $env:JMETER_HOME, or "jmeter" on the PATH.
param(
    [ValidateSet("smoke", "load", "stress")]
    [string]$Scenario = "smoke"
)

$scenarios = @{
    smoke  = @{ threads = 1;  rampup = 1;  loops = 1 }
    load   = @{ threads = 20; rampup = 20; loops = 10 }
    stress = @{ threads = 40; rampup = 30; loops = 10 }
}
$s = $scenarios[$Scenario]
$out = "results/$Scenario"

if (Test-Path $out) { Remove-Item -Recurse -Force $out }
New-Item -ItemType Directory -Force -Path $out | Out-Null

if ($env:JMETER_HOME) {
    $jmeter = Join-Path $env:JMETER_HOME "bin/jmeter.bat"
} else {
    $jmeter = "jmeter"
}

& $jmeter -n -t jmeter/api_load_test.jmx `
    -l "$out/results.jtl" -e -o "$out/report" `
    "-Jthreads=$($s.threads)" "-Jrampup=$($s.rampup)" "-Jloops=$($s.loops)"

python scripts/check_results.py "$out/results.jtl"
exit $LASTEXITCODE
