#!/bin/sh
# falsify 第89回: K-Z3 15時台 n 積み増し run215A-C (n=20 x 3) + landing control (/signup)
OUT=_f89_run215_out.txt
: > $OUT
date '+%Y-%m-%dT%H:%M:%S%z' >> $OUT
for r in A B C; do
  i=0
  while [ $i -lt 20 ]; do
    t=$(curl -o /dev/null -s -w '%{http_code} %{time_total}' --connect-timeout 10 "https://search.kotobase.net/search?q=test")
    echo "run215$r $t" >> $OUT
    i=$((i+1))
  done
  sleep 5
done
i=0
while [ $i -lt 20 ]; do
  t=$(curl -o /dev/null -s -w '%{http_code} %{time_total}' --connect-timeout 10 "https://kotobase.net/signup")
  echo "control $t" >> $OUT
  i=$((i+1))
done
date '+%Y-%m-%dT%H:%M:%S%z' >> $OUT