#!/bin/bash
# K-Z3 falsify run159A-C (search) + landing control, same method as prior runs:
# n=20 per run, separate curl connections, record TTFB per request.
OUT=/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/fz_run159_out.txt
: > "$OUT"
date >> "$OUT"
for run in A B C; do
  echo "=== run159$run search ===" >> "$OUT"
  for i in $(seq 1 20); do
    ttfb=$(curl -s -o /dev/null -w '%{time_starttransfer} %{http_code}' "https://search.kotobase.net/search?q=test")
    echo "159$run $i $ttfb" >> "$OUT"
  done
done
echo "=== landing control ===" >> "$OUT"
for i in $(seq 1 20); do
  ttfb=$(curl -s -o /dev/null -w '%{time_starttransfer} %{http_code}' "https://kotobase.net/")
  echo "LC $i $ttfb" >> "$OUT"
done
date >> "$OUT"
