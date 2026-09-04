#!/bin/bash
# K-Z3 n accumulation: run94A-C (n=20 each) + landing control (cosientist 第8回)
URL_S="https://search.kotobase.net/search?q=test"
URL_L="https://kotobase.net/"
for rid in 94A 94B 94C; do
  echo "=== run$rid search ==="
  for i in $(seq 1 20); do
    curl -o /dev/null -s -w "%{http_code} %{time_starttransfer}\n" "$URL_S"
  done
done
echo "=== landing control ==="
for i in $(seq 1 20); do
  curl -o /dev/null -s -w "%{http_code} %{time_starttransfer}\n" "$URL_L"
done
