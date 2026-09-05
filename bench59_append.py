import io

path = '/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md'
entry = ("- 2026-09-05: bench 第59回。rank 第59回 NEXT フォールバック (K-Z3 現在時刻帯 n 積み増し) を受け、"
         "K-Z3 22時台初計測 run172A–C を同測定法で実施 (22:17:43–22:17:55 JST, production HTTP 実測のため gate 外, "
         "secret 不含, host load1 7.56→6.07): run172A cold(>=0.5s) 3/20 (0.963/1.189/0.987s, 2/8/10番目) p50 46ms / "
         "run172B cold 2/20 (2.055/0.994s, 1/8番目) p50 59ms / run172C cold 0/20 p50 47ms — 合計 5/60 (~8.3%), "
         "landing control cold 0/20 p50 53ms と静穏で control 分離成立、cold 群は search 側に局在 "
         "(run168/169 型薄い cold 散発, C で消失)。21時台 (~58%) とは明確に異なり低位側だが、"
         "18–20時台 (~2-3%) よりやや高めの 1 tick 分。22時台帯レート確定には追加 n 要。"
         "status 遷移なし (rank 専門)。NEXT: 委ねる (rank 指定優先; フォールバックは K-Z3 現在時刻帯 n 積み増し継続)。\n")

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# insert before the rank 第59回 entry (last entry)
idx = max(i for i, l in enumerate(lines) if 'rank 第59回' in l)
# find start of that entry line (line begins with '- 2026-09-05: rank 第59回')
for i, l in enumerate(lines):
    if l.startswith('- 2026-09-05: rank 第59回'):
        idx = i
        break
lines.insert(idx, entry)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('inserted at', idx)
