#!/bin/bash
# K-Z3 夜帯 n 積み増し run89A-C (同一測定法: n=20, 別接続 curl, Tokyo)
# search.kotobase.net /search?q=test TTFB + landing page control
set -u
out="kz3_run89_out.txt"
: > "$out"
for r in A B C; do
  echo "== run89$r search $(date '+%H:%M:%S') ==" >> "$out"
  for i in $(seq 1 20); do
    t=$(curl -o /dev/null -s -w '%{http_code} %{time_starttransfer}' "https://search.kotobase.net/search?q=test")
    echo "$i $t" >> "$out"
    sleep 0.1
  done
done
echo "== landing control $(date '+%H:%M:%S') ==" >> "$out"
for i in $(seq 1 20); do
  t=$(curl -o /dev/null -s -w '%{http_code} %{time_starttransfer}' "https://kotobase.net/")
  echo "$i $t" >> "$out"
  sleep 0.1
done
echo "host load1: $(uptime)" >> "$out"
