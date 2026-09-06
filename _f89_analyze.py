import re
lines=open('/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/_f89_run215_out.txt').read().splitlines()
runs={'A':[],'B':[],'C':[]}
ctrl=[]
for ln in lines[1:]:
    m=re.match(r'run215([ABC]) 200 ([\d.]+)',ln)
    if m: runs[m.group(1)].append(float(m.group(2))); continue
    m=re.match(r'control 200 ([\d.]+)',ln)
    if m: ctrl.append(float(m.group(1)))
def st(x):
    s=sorted(x); n=len(s)
    p50=s[n//2] if n%2 else (s[n//2-1]+s[n//2])/2
    return f"n={n} p50={p50*1000:.0f}ms max={max(s)*1000:.0f}ms cold(>0.7s)={sum(1 for v in s if v>0.7)}"
for k,v in runs.items(): print(f"run215{k}",st(v))
print("search_total",st([v for r in runs.values() for v in r]))
print("control",st(ctrl))
print("control >0.3s:",[round(v*1000) for v in ctrl if v>0.3])