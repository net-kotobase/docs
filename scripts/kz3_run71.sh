#!/bin/bash
# K-Z3 evening-band n accumulation: search n=20 + landing control n=20
# separate-connection curl, TTFB measured
URL_SEARCH="https://search.kotobase.net/search?q=test"
URL_LANDING="https://kotobase.net/"

run_n() {
  local label="$1" url="$2" n="$3"
  local i ttfb total code
  for i in $(seq 1 "$n"); do
    read -r ttfb total code < <(curl -s -o /dev/null -w "%{time_starttransfer} %{time_total} %{http_code}" --max-time 10 "$url")
    echo "$label $(date +%H:%M:%S) $i ttfb=$ttfb total=$total code=$code"
    sleep 0.3
  done
}

echo "=== search run A ==="
run_n search "$URL_SEARCH" 20
echo "=== landing control ==="
run_n landing "$URL_LANDING" 20
echo "=== search run B ==="
run_n search "$URL_SEARCH" 20
echo "=== search run C ==="
run_n search "$URL_SEARCH" 20
