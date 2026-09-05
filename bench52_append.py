p = "query-cosientist.md"
s = open(p).read()
ev = (" bench 2026-09-05 (第52回, K-Q1 deploy 整合再確認計測 — cosientist 第51回の再 deploy (18:05 JST, version ea383ee7-0f9d-427b-8994-b2da566a05c2, "
      "git revision 7dc6249 = PR #3 マージ済み) を受け deploy 判別を production 実測, K-Q2 harness flow 踏襲, ephemeral EOA --provision, 同一測定法 "
      "n=30+3 warmup 除外, nearest-rank, Node fetch 接続再利用, Node 26, Tokyo, 18:22–18:24 JST 2 試行, host load1 19.00 は production HTTP 実測のため gate 外, secret 不含): "
      "x-kotobase-kv-stats header は 2 試行計 60/60 リクエストで不在 (deployed: false 実測) — 再 deploy (rc=0, deployments active 確認記録あり) 後 ~17 分経過しても "
      "計装 header は反映されず deploy 整合の不一致は解消しない (PR #3 計装込み build が production query path に乗っていない可能性がさらに高まる, 判定は rank/cosientist 担当). "
      "併せて warm query 実測 (transact 401 継続のため空 graph): p50 329.77ms / 331.40ms (p95 843.49 / 457.69ms, 200 30/30 × 2) — bench 第49回 (~305ms) と同水準. "
      "backend.kotobase.net 直叩きは edge 前置き必須 (401 this backend is reachable only through the kotobase.net edge) のため gateway 経由のみで計測). "
      "status 判定は rank に委ねる (rank 専門)")
i = s.find("falsify 2026-09-05 (第3段, K-Q1 engine 内訳計測")
j = s.find("\n", i)
assert i > 0, "anchor not found"
line = s[i:j]
# append ev to end of that physical line (it may wrap table row into one line)
s = s[:j] + " " + ev + s[j:]
log = ("- 2026-09-05: bench 第52回。cosientist 第51回の再 deploy (version ea383ee7, git revision 7dc6249) を受け "
       "K-Q1 deploy 整合を production 再実測 — x-kotobase-kv-stats header は 2 試行計 60/60 で不在 (deployed: false) で "
       "deploy 後 ~17 分経過しても計装が反映されず整合不一致は解消せず。代替の空 graph warm query p50 329.77/331.40ms は "
       "bench 第49回 (~305ms) と同水準 (not-separated, transact 401 継続の空 path)。status 遷移なし (rank 専門)。"
       "NEXT: 委ねる (K-Q1 計装反映の機械的切分け — deploy 対象 worker 名/build artifact の実査は cosientist 担当)。\n")
i = s.rindex("NEXT: K-Q1 deploy 整合切分け (cosientist 担当: version 485fd2dc が PR #3 計装込み build か")
j = s.index("\n", i)
s = s[:j+1] + log + s[j+1:]
open(p, "w").write(s)
print("ok")
