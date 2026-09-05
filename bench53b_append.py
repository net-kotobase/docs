import io, subprocess, json, re

path = "/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md"
text = io.open(path, encoding="utf-8").read()
lines = text.splitlines(keepends=True)

# 1) K-Z3 row evidence append
idx = next(i for i, ln in enumerate(lines) if ln.startswith("| K-Z3 | worker |"))
row = lines[idx]
assert row.rstrip("\n").endswith("|"), row[-80:]
add = (" bench 2026-09-05 (第54回, K-Z3 19時台 n 積み増し run163A–C, rank 第53回 NEXT「委ねる」フォールバック, "
       "同測定法 n=20 × 3 + landing control, 別接続 curl, Tokyo, 19:15 JST, 全 60/60 + control 20/20 200, "
       "host load1 60.04 は production HTTP 実測のため gate 外): "
       "run163A cold(>=0.5s) 4/20 (862/1133/841/1040ms, 冒頭 10 試行以内のクラスタ) p50 87.4ms, "
       "run163B/C cold 0/20 (p50 105.9/61.4ms), search 通算 cold 4/60 ~6.7% (1s 超 4/60 すべて), "
       "landing control cold 0/20 p50 76.2ms 静穏で control 分離成立 — 19時台通算 (run162 + run88 合算分) "
       "4/180 ~2.2% 低位帯だが run163A 型の冒頭クラスタ出現 1 窓。status 判定は rank に委ねる (rank 専門) |")
lines[idx] = row.rstrip("\n")[:-1].rstrip() + " " + add + "\n"

# 2) iteration log entry (append at end)
log = ("- 2026-09-05: bench 第54回。rank 第53回 NEXT (委ねる) を受け K-Z3 19時台 n 積み増し run163A–C を同測定法で実施 "
       "(19:15 JST, production HTTP 実測のため gate 外, secret 不含): search cold(>=0.5s) 4/60 (~6.7%, "
       "862/1133/841/1040ms の 1s 超冒頭クラスタが run163A の 1 窓のみ, B/C は cold 0 で p50 61–106ms), "
       "landing control cold 0/20 p50 76.2ms と静穏で control 分離成立 — run158 型全体遅延窓ではなく search 局在型。"
       "19時台通算 (run162 + 2026-09-04 run88 合算分) 4/180 ~2.2% 低位帯。status 遷移なし (rank 専門)。"
       "NEXT: 委ねる (rank 指定優先)。\n")
if not text.endswith("\n"):
    log = "\n" + log
lines.append(log)

io.open(path, "w", encoding="utf-8").write("".join(lines))
print("row_idx", idx + 1)
print("tail:", lines[idx].rstrip()[-200:])
print("log tail:", lines[-1][:120])
