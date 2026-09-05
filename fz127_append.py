p='/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md'
txt=open(p).read()
lines=txt.split('\n')
i=178  # K-Z3 row, 0-indexed
assert lines[i].startswith('| K-Z3 |')
ev=" falsify 2026-09-05 (K-Z3 11時台 n 積み増し run127A–C, 同測定法 n=20 × 3 + landing control, 別接続 curl, Tokyo, 11:16–11:17 JST, 全 60/60 + control 20/20 200, host load1 17.6 (tick 実測 11:16) は production HTTP 実測のため gate 外): run127A cold(>=0.5s) 0/20 (p50 0.036s, max 0.056s) / run127B cold 0/20 (p50 0.034s, max 0.058s) / run127C cold 0/20 (p50 0.034s, max 0.044s) — landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 (p50 0.051s, max 0.064s) と静穏で control 分離成立。11時台 2 セット目は bench 第46回 run126A–C (10/60) と正反対の完全静穏 — 11時台通算 10/120 は run126 1 セットのみの寄与で, 帯内でも発現/消失が交互に出る突発性 (時間窓依存) が再確認された。traffic 依存説への判定材料としては対称性のある 2 サンプルとなり追加 n の限界利得は低下傾向。status 判定は rank に委ねる"
lines[i]=lines[i].rstrip()+ev
open(p,'w').write('\n'.join(lines))
# verify
chk=open(p).read()
assert 'run127A' in chk and chk.count('run127A')==1
open('/tmp/fz127_verify.txt','w').write(f"appended ok, row len={len(lines[i])}\n")
