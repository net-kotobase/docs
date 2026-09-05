src = open('query-cosientist.md').read()
add = (' falsify 2026-09-05 (K-Z3 16時台 n 積み増し run154A–C, 同測定法 n=20 × 3 + '
       'landing control, 別接続 curl, Tokyo, 16:25–16:26 JST, 全 60/60 + control 20/20 200): '
       'run154A cold(>=1s) 6/20 (max 1.896s, 前半集中) / run154B cold 3/20 (max 1.519s) / '
       'run154C cold 0/20 — landing control (kotobase.net/, 同時刻, n=20) は cold 0/20 p50 59.0ms と静穏。'
       'search エンドポイントのみ 1s 超が 16:25 台に 9/60 集中 — 突発パターン再確認 (p50 は全群 ~47–104ms と低く、'
       '外れ値型)。status 判定は rank に委ねる。')
lines = src.split('\n')
for idx, l in enumerate(lines):
    if l.startswith('| K-Z3 |'):
        pos = l.rfind('status 判定は rank に委ねる')
        assert pos != -1, 'marker not found in K-Z3 line'
        end = pos + len('status 判定は rank に委ねる')
        lines[idx] = l[:end] + add + l[end:]
        break
else:
    raise SystemExit('K-Z3 line not found')
open('query-cosientist.md', 'w').write('\n'.join(lines))
print('appended at line', idx + 1)
