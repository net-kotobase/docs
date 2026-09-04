#!/bin/bash
# falsify K-Z3 evening n accumulation: run79A-C (n=20 each) + landing control
URL_S="https://search.kotobase.net/search?q=test"
URL_L="https://kotobase.net/"
for rid in 79A 79B 79C; do
  echo "=== run$rid search ==="
  for i in $(seq 1 20); do
    curl -o /dev/null -s -w "%{http_code} %{time_starttransfer}\n" "$URL_S"
  done
done
echo "=== landing control ==="
for i in $(seq 1 20); do
  curl -o /dev/null -s -w "%{http_code} %{time_starttransfer}\n" "$URL_L"
done
