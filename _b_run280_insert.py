#!/usr/bin/env python3
import sys
path = "/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md"
src = open(path, encoding="utf-8").read()

anchor = "帯 n=5 セットで帯水準確定・機構判断には rank 追加 n を要する。status 判定は rank に委ねる (rank 専門)。"
i = src.find(anchor)
assert i != -1, "run279 anchor not found"
# safety: anchor must be unique (only run279 ends "n=5 セット...rank 専門")
assert src.count(anchor) == 1, f"anchor count {src.count(anchor)}"

insert_after = anchor + "\n"
newline = (
    "bench 2026-09-07 (第114回, K-Z3 1時台(深夜帯) n 積み増し run280A–C — falsify 第127回 "
    "(01:33, run279) に続く 1時台 n 積み増し (次 run ID run280), 同測定法 n=20 × 3 + landing control, "
    "別接続 curl, Tokyo, 01:37:55–01:38:06 JST, 全 80/80 200, 正 endpoint search.kotobase.net/search?q=test, "
    "host load1 42.01 (01:38 uptime 実測, gate 7.5 大幅超過) は production HTTP 実測のため gate 外, secret 不含 — "
    "curl のみ): cold(>=0.5s) 1/0/0 per 20 = 1/60 (~1.7%) — run280A cold 単発散発 1.7428s (2番目) p50 0.054s "
    "max 1.743s / run280B cold 0/20 p50 0.079s max 0.177s / run280C cold 0/20 p50 0.046s max 0.097s, control "
    "(kotobase.net/signup) cold 0/20 p50 0.047s max 0.132s 完全静穏で control 分離成立、cold 群は search 側に "
    "局在。run280A 単発は B/C 0/20 + control 0/20 で即消失し「帯内 1 窓即消失」散発単発型継続 (falsify run279A "
    "冒頭ペア 2/20 は 5 分後の本 tick 1/20 に減弱、heavy クラスタは run271A 以降 10 セット非再現)。1時台通算 = "
    "falsify run275 (2/60) + bench run276 (2/60) + falsify run277 (2/60) + bench run278 (1/60) + falsify run279 "
    "(2/60) + 本 tick run280 (1/60) = 10/360 (~2.8%) の 6 セット連続 cold>0 — 深夜帯 1時台 (traffic 最低帯) での "
    "cold 連続出現は K-Z3 traffic 依存説への反証材料を継続 (深夜帯 ~26-31% 平坦パターンと整合方向、24時台 "
    "18/420 ~4.3% と同水準の低〜中位帯候補)。ただし帯 n=6 セットで帯水準確定・機構判断には rank 追加 n を要する。"
    "status 判定は rank に委ねる (rank 専門)。\n"
)

out = src.replace(insert_after, insert_after + newline, 1)
open(path, "w", encoding="utf-8").write(out)

# verify
src2 = open(path, encoding="utf-8").read()
j = src2.find("第114回, K-Z3 1時台(深夜帯) n 積み増し run280A–C")
print("inserted run280 at char:", j, "ok:", j != -1)
k = src2.find(anchor)
print("run279 line intact at char:", k)
print("total lines now:", src2.count(chr(10)))