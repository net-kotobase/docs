import re
p = 'query-cosientist.md'
s = open(p).read()
entry = """- 2026-09-05: falsify (cosientist 第43回相当)。K-Z3 9時台 n 積み増し run122A–C (09:31–09:32 JST, 同測定法 n=20 × 3 + landing control, 別接続 curl, Tokyo, 全 60/60 + control 20/20 200, host load1 15.3 は production HTTP 実測のため gate 外)。122A cold(≥0.5s) 4/20 (p50 0.041s, p90 0.887s, max 0.925s), 122B cold 1/20 (p50 0.041s, max 1.452s 突発 1 件), 122C cold 0/20 (p50 0.038s) — 計 5/60 発現。landing control は cold 0/20 (p50 0.045s, max 0.287s) と静穏で control 分離成立。9時台は 8時台 (0/120 完全静穏) に続き最初の試行セットで cold 突発が出た — traffic 上昇に転じる 9時台で発現率が上がるという K-Z3 traffic 依存説の方向を支持 (単一サンプルのため確定はしない、追加 n 要)。status 遷移なし (rank 専門)。NEXT: 委ねる (rank 判断 — 9時台 n 積み増し継続を優先推奨)。
"""
marker = '- 2026-09-05: rank 第42回。'
i = s.index(marker)
s2 = s[:i] + entry + s[i:]
open(p, 'w').write(s2)
print('inserted at char', i)
