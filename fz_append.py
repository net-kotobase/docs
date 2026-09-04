import re, subprocess

path = '/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md'
text = open(path).read()

evidence = ("bench 2026-09-05 (第40回, K-Q1 backend query path 計測第2段 — rank 第38回 NEXT, production HTTP 実測のため host load gate 外, 同一測定法: n=30 sequential + 3 warmup 除外, nearest-rank, Node https keepalive 接続再利用, Tokyo, 05:57-05:59 JST, secret 不含 — ephemeral EOA --provision 相当, 秘密鍵はメモリ内で zero-fill し記録せず): K-Q2 harness を control-plane/authn/scripts/live_biscuit_query_bench.mjs から再使用し SIWE (ephemeral EOA) → Biscuit issuance → authenticated /xrpc/datomic.q を TTFB/total 分解付きで 2 回実行 (run A/B, 各 30/30 = 200, marker read-back ok, tenant provision 201): warm query total p50 656.70/654.61ms (p95 1117.71/977.90ms, min 601.11/601.10ms) — TTFB≈total (p50 656.69/654.61ms, 差 <0.1ms) で 応答は最後に一括到着 = 待ち時間の実質すべてが gateway 以遠の backend query 実行区間。同窓の gateway auth check (/api/auth/me, Biscuit 付与) は p50 20.11/21.31ms (p95 31.27/42.40ms) — gateway 前段 + Biscuit verify hop を含めても ~20ms で、654ms との差分 ~635ms は backend query 実行区間に帰属が確定 (bench 第39回の no-auth 402 短絡 p50 15.87ms とも整合)。2 回独立実行で p50 654-657ms は再現し 2026-08-26 基準 187.35ms に対する +3.5〜3.9 倍退行 (+~470ms) が K-Q2/falsify 実測 (753/909ms) と同 magnitude で再確認 — 退行の主体は backend query 実行区間 (engine/KV 側) で gateway・Biscuit verify は棄却済み。残余の切れ手は engine 内訳 (KV read 回数/CID 構造, local engine test) でコード変更を伴うため rank/cosientist 指定待ち。status 判定は rank に委ねる。")

marker = "cosientist 2026-09-05 (K-Z3 深夜帯 0時台 帯移行観測 run102A–C"
idx = text.find(marker)
assert idx > 0, 'marker not found'
new_text = text[:idx] + evidence + "\n" + text[idx:]
open(path, 'w').write(new_text)
open('/tmp/fz_append_out.txt', 'w').write('appended at char %d\n' % idx)

# Iteration log entry
log_marker = "- 2026-09-05: bench 第39回"
lidx = new_text.find(log_marker)
log_entry = "- 2026-09-05: falsify 第39回。rank 第38回 NEXT の K-Q1 backend query path 計測第2段を実施 (K-Q2 harness 再使用 + TTFB/total 分解, n=30 × 2 run, ephemeral EOA, secret 不含): authenticated warm query total p50 656.70/654.61ms (TTFB≈total, 差 <0.1ms) — gateway auth check 同窓 p50 20.11/21.31ms との差分 ~635ms が backend query 実行区間に帰属。2 回再現し K-Q2 退行 (+~470ms vs 2026-08-26 基準) を同 magnitude で再確認、退行主体は engine/KV 側で gateway・verify は棄却済み。evidence 追記済み、status 遷移なし (rank 専門)。\n"
if lidx > 0:
    new_text2 = new_text[:lidx] + log_entry + new_text[lidx:]
    open(path, 'w').write(new_text2)
    open('/tmp/fz_append_out.txt', 'a').write('log inserted\n')
else:
    open('/tmp/fz_append_out.txt', 'a').write('log marker NOT found\n')
