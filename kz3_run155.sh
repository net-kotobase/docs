#!/bin/bash
# K-Z3 17時台 n 積み増し run155A-C (n=20 each) + landing control, 同測定法
URL_S="https://search.kotobase.net/search?q=test"
URL_L="https://kotobase.net/"
OUT="/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/kz3_run155_out.txt"
: > "$OUT"
echo "start $(date)" >> "$OUT"
for rid in 155A 155B 155C; do
  echo "=== run$rid search ===" >> "$OUT"
  for i in $(seq 1 20); do
    curl -o /dev/null -s -w "%{http_code} %{time_starttransfer}\n" "$URL_S" >> "$OUT"
  done
done
echo "=== landing control ===" >> "$OUT"
for i in $(seq 1 20); do
  curl -o /dev/null -s -w "%{http_code} %{time_starttransfer}\n" "$URL_L" >> "$OUT"
done
echo "end $(date)" >> "$OUT"
echo done
