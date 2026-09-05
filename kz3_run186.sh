#!/bin/bash
# K-Z3 06:00 hour: run186A-C (n=20 each) + landing control
URL_S="https://search.kotobase.net/search?q=test"
URL_L="https://kotobase.net/"
OUT="/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/kz3_run186_out.txt"
: > "$OUT"
for rid in 186A 186B 186C; do
  echo "=== run$rid search ===" >> "$OUT"
  for i in $(seq 1 20); do
    curl -o /dev/null -s -w "%{http_code} %{time_starttransfer}\n" "$URL_S" >> "$OUT"
  done
done
echo "=== landing control ===" >> "$OUT"
for i in $(seq 1 20); do
  curl -o /dev/null -s -w "%{http_code} %{time_starttransfer}\n" "$URL_L" >> "$OUT"
done
echo done
