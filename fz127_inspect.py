import re
p='/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md'
lines=open(p).read().split('\n')
out=open('/tmp/fz127_inspect.txt','w')
# find K-Z3 row and K-S1 row boundaries
for i,l in enumerate(lines):
    if l.startswith('| K-Z3 |'):
        out.write(f"KZ3ROW {i+1} len={len(l)}\n")
        out.write("HEAD: "+l[:300]+"\n")
        out.write("TAIL: "+l[-600:]+"\n")
    if l.startswith('| K-S1 |'):
        out.write(f"KS1ROW {i+1} len={len(l)}\n")
out.close()
print("done")
