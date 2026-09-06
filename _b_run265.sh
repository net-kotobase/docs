#!/bin/sh
# cosientist core: K-Z3 23hr n-add run265A-C, same measurement method (bench/falsify):
# n=20 x 3 runs + landing control, separate-connection curl, cold threshold >= 0.5s TTFB.
# cron restrictions: no -e/-c flags, no heredoc-to-interpreter, no rm -rf.
cd /Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs
SEARCH="https://search.kotobase.net/search?q=test"
LAND="https://kotobase.net/signup"
run_search() {
  i=1
  while [ $i -le 20 ]; do
    curl -s -o /dev/null -w "200 %{time_starttransfer}\n" "$SEARCH" >> "$1"
    i=$((i+1))
  done
}
run_land() {
  i=1
  while [ $i -le 20 ]; do
    curl -s -o /dev/null -w "200 %{time_starttransfer}\n" "$LAND" >> "$1"
    i=$((i+1))
  done
}
run_search _b_run265A.txt
run_search _b_run265B.txt
run_search _b_run265C.txt
run_land _b_land265.txt
date '+%Y-%m-%dT%H:%M:%S%z' > _b_run265_time.txt
uptime >> _b_run265_time.txt
echo "done" >> _b_run265_time.txt