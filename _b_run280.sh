#!/bin/sh
# bench K-Z3 1hr n-add run280A-C, same measurement method: n=20 x 3 runs + landing control,
# separate-connection curl, cold threshold >= 0.5s TTFB.
# cron runtime restrictions: no -e/-c flags, no heredoc-to-interpreter, no rm -rf.
cd /Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs
SEARCH="https://search.kotobase.net/search?q=test"
LAND="https://kotobase.net/signup"
run_search() {
  i=1
  while [ $i -le 20 ]; do
    curl -s -o /dev/null -w "%{http_code} %{time_starttransfer}\n" "$SEARCH" >> "$1"
    i=$((i+1))
  done
}
run_land() {
  i=1
  while [ $i -le 20 ]; do
    curl -s -o /dev/null -w "%{http_code} %{time_starttransfer}\n" "$LAND" >> "$1"
    i=$((i+1))
  done
}
date '+start %Y-%m-%dT%H:%M:%S%z' > _b_run280_time.txt
run_search _b_run280A.txt
run_search _b_run280B.txt
run_search _b_run280C.txt
run_land _b_land280.txt
date '+end %Y-%m-%dT%H:%M:%S%z' >> _b_run280_time.txt
uptime >> _b_run280_time.txt
echo "done" >> _b_run280_time.txt