p = "query-cosientist.md"
s = open(p).read()
tail = "status 判定は rank に委ねる (rank 専門) |"
i = s.find("K-Z3 | worker |")
j = s.find("\n", i)
row = s[i:j]
assert row.count(tail) == 1, row.count(tail)
ev = (" bench 2026-09-05 (第51回, K-Z3 17時台 n 積み増し run158A–C ※ bench 第50回 run156 と同一スクリプト流用による ID 衝突回避で run158 とする, 同測定法 n=20 × 3 run + landing control, "
      "別接続 curl, Tokyo, 17:54–17:55 JST, 全 80/80 200, host load1 13.78 は production HTTP 実測のため gate 外): "
      "run158A cold(>=0.5s) 0/20 p50 107.4ms (p90 181.2ms, max 256.3ms) / run158B cold 0/20 p50 101.8ms / run158C cold 0/20 p50 62.6ms (max 148.8ms) — "
      "landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 77.7ms (max 132.6ms) と静穏で control 分離成立。全 3 run 完全静穏 (17時台 3 セット目)。"
      "warm p50 は 63–107ms 帯で run156/157 (46–62ms) より上振れしたが cold 0/60 で 17時台通算は 120→180 試行中 1 試行 (~0.6%) の低位帯を維持。"
      "status 判定は rank に委ねる (rank 専門)")
new_row = row.replace(tail, ev + " |")
s = s[:i] + new_row + s[j:]
open(p, "w").write(s)
print("ok", len(new_row))
