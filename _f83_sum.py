import re, statistics
runs = {}
control = []
for line in open('_f83_run207_out.txt'):
    m = re.match(r'(run207[A-C]|control) (\d+) ([\d.]+)', line.strip())
    if not m: continue
    key, code, t = m.group(1), m.group(2), float(m.group(3))
    (control if key=='control' else runs.setdefault(key,[])).append((code,t))
out = []
for k in sorted(runs):
    ts = sorted(t for c,t in runs[k] if c=='200')
    cold = [t for c,t in runs[k] if c=='200' and t>=0.8]
    errs = [c for c,t in runs[k] if c!='200']
    p50 = statistics.median(ts) if ts else None
    out.append(f"{k}: n={len(runs[k])} errs={len(errs)} cold(>=0.8s)={len(cold)} p50={p50*1000:.1f}ms max={max(ts)*1000:.1f}ms colds={[round(t,3) for t in cold]}")
ts = sorted(t for c,t in control if c=='200')
cold = [t for c,t in control if c=='200' and t>=0.8]
errs = [c for c,t in control if c!='200']
out.append(f"control: n={len(control)} errs={len(errs)} cold={len(cold)} p50={statistics.median(ts)*1000:.1f}ms max={max(ts)*1000:.1f}ms")
open('_f83_sum_out.txt','w').write('\n'.join(out)+'\n')
