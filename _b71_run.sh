#!/bin/bash
# K-Z3 6時台 n 積み増し run191A-C: 同測定法 n=20 x 3 + landing control, 別接続 curl
# endpoint: search.kotobase.net /search?q=test (K-Z3 標準), control: kotobase.net/
OUT=_b71_meas.txt
: > "$OUT"
run_seq() {  # $1 label, $2 url
  local label="$1" url="$2"
  for i in $(seq 1 20); do
    t=$(curl -s -o /dev/null -w '%{time_total} %{http_code}' --no-keepalive "$url")
    echo "$label $i $t" >> "$OUT"
  done
}
run_seq A "https://search.kotobase.net/search?q=test"
run_seq B "https://search.kotobase.net/search?q=test"
run_seq C "https://search.kotobase.net/search?q=test"
run_seq CTRL "https://kotobase.net/"
echo "DONE $(date '+%F %T %Z')" >> "$OUT"
