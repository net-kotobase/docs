#!/bin/bash
# K-Z3 falsify run178A-C (search, 1時台) + landing control, same method as prior runs.
OUT=/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/falsify69_run178_out.txt
: > "$OUT"
date >> "$OUT"
uptime >> "$OUT"
for run in A B C; do
  echo "=== run178$run search ===" >> "$OUT"
  for i in $(seq 1 20); do
    ttfb=$(curl -s -o /dev/null -w '%{time_starttransfer} %{http_code}' "https://search.kotobase.net/search?q=test")
    echo "178$run $i $ttfb" >> "$OUT"
  done
done
echo "=== landing control ===" >> "$OUT"
for i in $(seq 1 20); do
  ttfb=$(curl -s -o /dev/null -w '%{time_starttransfer} %{http_code}' "https://kotobase.net/")
  echo "LC $i $ttfb" >> "$OUT"
done
date >> "$OUT"
