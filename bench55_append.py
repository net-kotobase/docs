import re, io

path = "/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md"
with open(path, encoding="utf-8") as f:
    lines = f.readlines()

evidence = (
    "bench 2026-09-05 (第55回, K-Z3 19時台 n 積み増し run165A–C, bench 第54回 run163 直後の追加 n, "
    "同測定法 n=20 × 3 + landing control, 別接続 curl, Tokyo, 19:34:02–19:34 JST, 全 80/80 200, "
    "host load1 16.85 は production HTTP 実測のため gate 外): "
    "run165A cold(>=0.5s) 2/20 (1.098s 4番目, 0.854s 10番目 — 散発配置) p50 0.045s / "
    "run165B cold 0/20 p50 0.045s / run165C cold 0/20 p50 0.037s — "
    "landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 0.042s と静穏で control 分離成立、"
    "cold 群は search 側に局在。run163A 型の冒頭クラスタではなく run163 単発型/薄い散発。"
    "19時台通算は 2026-09-04 run88 (0/60) + run162 (0/60) + run163 (4/60) + 本 tick (2/60) で "
    "240 試行中 6 試行 (~2.5%) の低位帯。status 判定は rank に委ねる (rank 専門)。NEXT: 委ねる (rank 指定優先)。"
)

marker = "K-Z3 | worker |"
for i, line in enumerate(lines):
    if marker in line:
        # Append evidence at end of the table row (before trailing newline)
        new = line.rstrip("\n") + " " + evidence + "\n"
        lines[i] = new
        break
else:
    raise SystemExit("K-Z3 row not found")

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)
print("evidence appended to line", i + 1)
