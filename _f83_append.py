import re
p = 'query-cosientist.md'
s = open(p).read()
anchor = '| K-Z2 |'
i = s.index(anchor)
line_start = s.rindex('\n', 0, i) + 1
ev = "falsify 第83回 run207A-C (11:55 JST, 11時台 2セット目, n=20x3 + landing control): cold 4/0/1 = 5/60 (~8.3%), A冒頭集中クラスタ 0.840-1.027s 4件即消失 (B 0, C 単発 1.335s), warm p50 52-62ms, control cold 0/20 p50 77ms max 405ms 静穏 — 11時台通算 9/120 ~7.5% で 12時台 ~8.3% 水準, 日中帯 traffic 依存パターンと整合し K-Z3 traffic 依存説を支持方向。"
if ev[:40] not in s:
    s = s[:line_start] + ev + '\n' + s[line_start:]
    open(p,'w').write(s)
    print('APPENDED')
else:
    print('ALREADY')
