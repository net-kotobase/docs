import io, sys
p = "/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md"
lines = open(p, encoding="utf-8").read().split("\n")

# --- 1. Append run333 evidence to the END of the K-Z3 evidence line (line 279, index 278) ---
kz_idx = None
for i, l in enumerate(lines):
    if l.startswith("| K-Z3 |"):
        kz_idx = i
        break
assert kz_idx is not None, "K-Z3 line not found"

kz_evidence = (" bench 2026-09-07 (第141回, K-Z3 10時台(9/7) n 積み増し run333A–C — rank 第145回 NEXT run333, falsify run332 の次 ID, "
 "同測定法 n=20 × 3 + landing control, 別接続 curl, Tokyo, 10:15:59–10:16:23 JST, 全 80/80 200, "
 "正 endpoint search.kotobase.net/search?q=test, host load1 20.62 (gate 7.5 超過) は production HTTP 実測のため gate 外, "
 "secret 不含 — curl のみ): cold(>=0.5s) 4/1/0 per 20 = 5/60 (~8.3%) — run333A cold 4/20 "
 "(1.1841s/2.0556s/1.5537s/1.2171s, idx2/4/5/8 冒頭クラスタ型) p50 129.2ms max 2055.6ms / "
 "run333B cold 単発 1/20 (0.9973s) p50 109.0ms / run333C cold 0/20 p50 98.6ms max 215.4ms, "
 "control (kotobase.net/signup) cold 0/20 p50 127.1ms max 419.9ms 静穏 (500ms 未満) で control 分離成立、"
 "cold 群は search 側に局在。run333A 冒頭クラスタ 4/20 は run331A/run332A 型「帯内 1 窓」の継続的な突発で "
 "B/C 0/20 + control 0/20 で部分即消失、散発単発を超える中位帯。10時台通算 run332 (4/60) + 本 tick run333 (5/60) = 9/120 "
 "(~7.5%) 中位帯で heavy run331A 9/20 型の後続 (≥6/20 には至らず) として K-Z3 */2 高頻度化判断材料を続報。"
 "warm p50 98–129ms は host load 20 高騰 tick の上振れ寄り (borderline note) だが cold 閾値判定 5/60 は "
 "control 完全静穏で確定的。status 判定は rank に委ねる (rank 専門)。")
lines[kz_idx] = lines[kz_idx] + kz_evidence

# --- 2. Insert iteration-log entry just below the "## Iteration log" header (newest-first) ---
hdr_idx = None
for i, l in enumerate(lines):
    if l.strip() == "## Iteration log":
        hdr_idx = i
        break
assert hdr_idx is not None, "Iteration log header not found"

entry = ("- 2026-09-07: bench 第141回。10:16 JST tick。HEAD 5fe4b1b = rank 第145回 (NEXT run333) = remote "
 "net-kotobase/main 一致 (fetch + rev-parse 比較, 乖離 0; worktree detached HEAD のため git pull --ff-only 不可, "
 "fetch 系で取り込み)。live smoke 200 (/, /signup; pre-run 計測)。host load1 20.62 (gate 7.5 超過) のため "
 "local 測定は拒否し production HTTP フォールバック (gate 外)。※pre-run monitor NEXT「K-Z3 深夜帯 23時台 n 積み増し」は "
 "rank 第90回帯 stale artifact — true NEXT は rank 第145回 bump 済み「K-Z3 current-band(10時台) n-add run333」を本 tick 実施。"
 "K-Z3 10時台 n 積み増し run333A–C を実測 (同測定法 n=20 × 3 + landing control, 別接続 curl, cold>=0.5s, "
 "nearest-rank p50, 10:15:59–10:16:23 JST, 全 80/80 200): cold 5/60 (~8.3%) — run333A 4/20 冒頭クラスタ "
 "(1.1841/2.0556/1.5537/1.2171s) + run333B 単発 1/20 (0.9973s) + run333C 0/20, control (kotobase.net/signup) "
 "cold 0/20 p50 127.1ms max 419.9ms 静穏で control 分離成立、cold 群 search 局在。10時台通算 run332 4/60 + 本 tick "
 "5/60 = 9/120 (~7.5%) 中位帯、run331A heavy 9/20 初再出現の弱〜中位後続 (散発 4/20 超えだが heavy ≥6/20 には至らず) — "
 "heavy 型が 10時台でも帯内 1 窓即消失型として持続するか (2 窓連続 0/2 への収束 vs 再出現) の run333 追加窓として記録。"
 "warm p50 98–129ms は host load 20 高騰 tick の上振れ寄り borderline note だが cold 判定 5/60 は control 静穏で確定的。"
 "status 判定は rank に委ねる (rank 専門)。secret は一切記録せず。詳細は K-Z3 evidence 欄 (L279 末尾追記)。")
lines.insert(hdr_idx + 1, entry)

open(p, "w", encoding="utf-8").write("\n".join(lines))
print("OK: kz_line=%d iter_header=%d new_total_lines=%d" % (kz_idx + 1, hdr_idx + 1, len(lines)))