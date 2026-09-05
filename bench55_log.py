path = "/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md"
with open(path, encoding="utf-8") as f:
    content = f.read()

entry = (
    "- 2026-09-05: bench 第55回。rank 第53回 NEXT「委ねる」のフォールバック "
    "(K-Z3 現在時刻帯 n 積み増し) を受け、K-Z3 19時台 n 積み増し run165A–C を同測定法で実施 "
    "(19:34 JST, production HTTP 実測のため gate 外, secret 不含, host load1 16.85): "
    "search cold(>=0.5s) 2/60 (~3.3%, 1.098s 4番目 + 0.854s 10番目の散発が run165A のみ, B/C は cold 0 で p50 37–45ms), "
    "landing control cold 0/20 p50 42ms と静穏で control 分離成立 — run163A 型の冒頭クラスタではなく薄い散発型。"
    "19時台通算 (run88 + run162 + run163 + 本 tick) 6/240 ~2.5% 低位帯。status 遷移なし (rank 専門)。"
    "NEXT: 委ねる (rank 指定優先; フォールバックは K-Z3 現在時刻帯 n 積み増し継続)。\n"
)

if not content.endswith("\n"):
    content += "\n"
content += entry
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("iteration log appended")
