import re,io
p='/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md'
txt=open(p,encoding='utf-8').read()
assert '\n' in txt
evidence=" falsify 2026-09-06 (第89回, K-Z3 15時台帯初計測 run215A-C, 同測定法 n=20 x 3 + landing control, 別接続 curl, Tokyo, 15:01-15:02 JST, 全 80/80 200, 正 endpoint search.kotobase.net/search?q=test, host load1 18.46 (gate 7.5 超過) は production HTTP 実測のため gate 外): run215A cold(>=0.5s) 0/20 (max 0.231s) p50 134ms / run215B cold 1/20 (1.167s 18番目の単発) p50 71ms / run215C cold 1/20 (1.033s 6番目の単発) p50 98ms — landing control (kotobase.net/signup, 同時刻, n=20, 全 200) は cold 0/20 p50 119ms max 512ms だが末尾 2 試行 (0.331/0.512s) と 0.241s が上振れで control 完全静穏は不成立 (0.7s 超 cold はなし, 閾値内)。search cold 2/60 (~3.3%) 単発散在で run215B/C 同時 cold ならず (run212A→run213A 型「帯内 1 窓即消失」ではなく same-window 同時上振れなし)。15時台通算 2/60 (~3.3%) は 14時台通算 (10/240 ~4.2%) / 9/5 run152 と同水準の低位帯残界で、13-15時帯連続で低位帯続く。status 遷移なし (rank 専門)。secret は一切記録せず (curl のみ)。"
lines=txt.split('\n')
idx=None
for i,l in enumerate(lines):
    if l.startswith('| K-Z3 |'):
        idx=i; break
assert idx is not None, "K-Z3 row not found"
lines[idx]=lines[idx]+evidence
open(p,'w',encoding='utf-8').write('\n'.join(lines))
print("appended at line",idx+1,"len",len(lines[idx]))