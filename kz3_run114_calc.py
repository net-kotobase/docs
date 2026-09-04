import re, subprocess

# Parse kz3_run114_out.txt
path = '/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/kz3_run114_out.txt'
sections = {}
cur = None
for line in open(path):
    line = line.strip()
    m = re.match(r'^=== (run114[A-C]|landing control)', line)
    if m:
        cur = m.group(1)
        sections[cur] = []
        continue
    m = re.match(r'^(\d{3}) ([\d.]+)$', line)
    if m and cur:
        sections[cur].append((int(m.group(1)), float(m.group(2))))

def stats(rows, thresh=0.5):
    codes = [c for c, t in rows]
    ok = [t for c, t in rows if c == 200]
    ok_sorted = sorted(ok)
    n = len(ok)
    p50 = ok_sorted[n // 2] if n else None
    cold = [t for t in ok if t >= thresh]
    return dict(n=len(rows), ok2xx=sum(1 for c in codes if 200 <= c < 300), cold=len(cold),
                cold_vals=sorted(cold), p50=round(p50, 3) if p50 else None)

lines = []
for k, rows in sections.items():
    lines.append(f'{k}: {stats(rows)}')

# 5時台 totals: run112A-C (cold 1/60) + run113? no run113 was 4時台 bench. run114 = this.
# 深夜帯通算 update: previous 89 trials 29 cold (~32.6%); add 3 trials (run114A-C), count cold>0 trials.
lines.append('')
lines.append(f'uptime now: {subprocess.run("uptime", shell=True, capture_output=True, text=True).stdout.strip()}')
lines.append(f'date now: {subprocess.run("date", shell=True, capture_output=True, text=True).stdout.strip()}')
open('/tmp/fz_run114_calc.txt', 'w').write('\n'.join(lines))
print('ok')
