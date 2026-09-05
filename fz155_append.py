p = "query-cosientist.md"
s = open(p).read()
ev = (" falsify 2026-09-05 (K-Z3 17時台 n 積み増し run155A–C, 同測定法 n=20 × 3 + landing control, 別接続 curl, Tokyo, 17:19–17:21 JST, 全 60/60 + control 20/20 200): "
      "run155A cold(>=0.5s) 4/20 (1.026–1.648s 前半~中盤散発, warm p50 52.2ms) / run155B cold 1/20 (1.112s 単発, p50 46.2ms) / run155C cold 0/20 (p50 45.9ms) — 計 5/60 (~8.3%), "
      "landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 53.4ms max 249.5ms と静穏で control 分離成立、cold 群は search 側に局在 (run154 型の 1s 超外れ値パターン継続, p50 は全群低位で外れ値型)。"
      "17時台帯初計測で 14/16時台 (~8.3%/~15%) と同程度の低位〜中位散発 — 帯別分布に 17時台の裾を追加。status 判定は rank に委ねる (rank 専門)")
old = "。。 |"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, "。" + ev + " |")
open(p, "w").write(s)
print("ok")
