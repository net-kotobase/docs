#!/bin/bash
# K-Z3 5時台 run114A-C (n=20 x3 + landing control) — same method as run113.sh
URL_S="https://search.kotobase.net/search?q=test"
URL_L="https://kotobase.net/"
OUT="/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/kz3_run114_out.txt"
: > "$OUT"
echo "start $(date '+%F %T %z')" >> "$OUT"
uptime >> "$OUT"
for r in A B C; do
  echo "=== run114$r $(date '+%T') ===" >> "$OUT"
  for i in $(seq 1 20); do
    curl -o /dev/null -s -w "%{http_code} %{time_starttransfer}\n" --max-time 10 "$URL_S" >> "$OUT"
    sleep 0.2
  done
done
echo "=== landing control $(date '+%T') ===" >> "$OUT"
for i in $(seq 1 20); do
  curl -o /dev/null -s -w "%{http_code} %{time_starttransfer}\n" --max-time 10 "$URL_L" >> "$OUT"
  sleep 0.2
done
echo "end $(date '+%F %T %z')" >> "$OUT"
uptime >> "$OUT"
echo done
