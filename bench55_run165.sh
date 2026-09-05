#!/bin/bash
# K-Z3 bench run165A-C (search) + landing control, same method as prior runs:
# n=20 per run, separate curl connections, record TTFB per request.
OUT=/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/bench55_run165_out.txt
: > "$OUT"
date >> "$OUT"
uptime >> "$OUT"
for run in A B C; do
  echo "=== run165$run search ===" >> "$OUT"
  for i in $(seq 1 20); do
    ttfb=$(curl -s -o /dev/null -w '%{time_starttransfer} %{http_code}' "https://search.kotobase.net/search?q=test")
    echo "165$run $i $ttfb" >> "$OUT"
  done
done
echo "=== landing control ===" >> "$OUT"
for i in $(seq 1 20); do
  ttfb=$(curl -s -o /dev/null -w '%{time_starttransfer} %{http_code}' "https://kotobase.net/")
  echo "LC $i $ttfb" >> "$OUT"
done
date >> "$OUT"
