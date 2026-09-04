#!/bin/bash
# K-Z3 night-band 21h n accumulation: run93A-C (n=20 each) + landing control
URL_S="https://search.kotobase.net/search?q=test"
URL_L="https://kotobase.net/"
OUT="kz3_run93_out.txt"
: > "$OUT"
for rid in 93A 93B 93C; do
  echo "=== run$rid search ===" | tee -a "$OUT"
  for i in $(seq 1 20); do
    curl -o /dev/null -s -w "%{http_code} %{time_starttransfer}\n" "$URL_S" | tee -a "$OUT"
  done
done
echo "=== landing control ===" | tee -a "$OUT"
for i in $(seq 1 20); do
  curl -o /dev/null -s -w "%{http_code} %{time_starttransfer}\n" "$URL_L" | tee -a "$OUT"
done
