import re
p = "/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md"
doc = open(p).read()
lines = doc.split("\n")
target = None
for i, l in enumerate(lines):
    if l.startswith("| K-Z3 |"):
        target = i
        break
assert target is not None
add = (" falsify 2026-09-06 (K-Z3 6時台 1セット目 run186A–C, 同測定法 n=20 × 3 + landing control, "
       "別接続 curl, 06:16 JST, 全 80/80 200): run186A cold(>=0.5s) 9/20 p50 103.7ms (max 1242.7ms, "
       "1.0s超えを含む群発) / run186B cold 0/20 p50 45.4ms / run186C cold 0/20 p50 35.7ms — "
       "landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 41.5ms (max 48.9ms) と静穏で "
       "control 分離成立。A セットでの突発群発 (9/20) は数分後の B/C で即時非再現 — run100A/116A 型の "
       "短時間窓パターンと整合し 6時台も低位帯 (帯発現率 ~0-13%) 内の突発が深夜帯でも発生し得ることを追加支持 "
       "(深夜帯突発は traffic 依存説をさらに弱める)。status 判定は rank に委ねる (rank 専門)。")
row = lines[target].rstrip()
if row.endswith(" |"):
    lines[target] = row[:-2] + add + " |"
else:
    lines[target] = row + add + " |"
open(p, "w").write("\n".join(lines))
print("ok")
