path = "query-cosientist.md"
s = open(path, encoding="utf-8").read()
anchor = "| K-Z2 | worker |"
assert s.count(anchor) == 1, s.count(anchor)
ev = (" falsify 2026-09-06 (K-Z3 1時台帯初計測 run178A–C, 同測定法 n=20 × 3 + landing control, "
"別接続 curl, Tokyo, 01:28:25–01:28:42 JST, 全 80/80 200, host load1 7.32 は production HTTP 実測のため gate 外): "
"run178A cold(>=0.5s) 10/20 (0.834–1.678s 散発配置, 1–5番目連続 + 中盤以降散発, run71A/run105A 型 cold 多発クラスタ — "
"ただし warm 10 件は 33–65ms 帯で p50 834ms は cold 濃度による median 位置の結果, warm 群自体の遅延上振れはなし) / "
"run178B cold 0/20 p50 38.9ms (max 181ms) / run178C cold 0/20 p50 38.8ms (max 59.1ms) — "
"landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 50.1ms (max 274ms) と静穏で control 分離成立、"
"cold 群は search 側に局在。1時台帯初計測で 3 試行中 1 試行 cold>0 (10/60 集中) — 深夜帯 23時台/0時台 (~4.4–31% 日差あり) に続き "
"traffic 最低帯での多発クラスタ出現は K-Z3 traffic 依存説への反証材料を継続 (run178A 多発は即時非再現で帯内 1 窓)。"
"status 判定は rank に委ねる (rank 専門)。")
s = s.replace(anchor, ev + " " + anchor)
open(path, "w", encoding="utf-8").write(s)
print("appended")
