import subprocess

def run(cmd, timeout=60):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd='/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs')
    return (p.stdout + p.stderr).strip()

evidence = "falsify 2026-09-05 (K-Z3 深夜帯 5時台 n 積み増し run114A–C, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 05:24–05:27 JST, 全 80/80 200, host load1 4.55 は production HTTP 実測のため gate 外): run114A cold(>=0.5s) 0/20 p50 0.039s / run114B cold 0/20 p50 0.039s / run114C cold 0/20 p50 0.039s — landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 0.041s と静穏で control 分離成立。全 3 run 完全静穏 (初の 0/60)。追加プローブ (05:23, curl 詳細分解 dns/conn/tls/ttfb, 各 3 回): search TTFB 52–72ms / landing TTFB 45–57ms で全て静穏。5時台通算は run112A–C (cold 1/60) + run114A–C (cold 0/60) で 120 試行中 1 試行 — 5時台は帯内で最も静穏だが深夜帯通算 cold>0 は 92 試行中 29 試行 (~31.5%) で帯別 ~29–33% の平坦パターンを維持、traffic 最低帯での発現継続は K-Z3 traffic 依存説への反証材料として継続。status 判定は rank に委ねる"

# Insert before the K-Z2 row line (line 104) — same as prior runs
script = f'''
import io

path = 'query-cosientist.md'
text = open(path, encoding='utf-8').read()
lines = text.split('\\n')

# find the K-Z2 hypothesis row line (starts with '| K-Z2 |')
idx = None
for i, l in enumerate(lines):
    if l.startswith('| K-Z2 |'):
        idx = i
        break
assert idx is not None, 'K-Z2 row not found'

evidence = {evidence!r}
lines.insert(idx, evidence)
open(path, 'w', encoding='utf-8').write('\\n'.join(lines))
print('inserted before line', idx + 1)
'''
open('kz3_run114_append.py', 'w').write(script)
print(run('python3 kz3_run114_append.py'))
print(run("grep -c 'run114' query-cosientist.md"))
