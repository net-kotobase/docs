p='/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md'
lines=open(p).read().split('\n')
i=178
l=lines[i]
assert l.startswith('| K-Z3 |')
out=open('/tmp/fz127_tail.txt','w')
out.write("LEN=%d\n"%len(l))
out.write("TAIL: "+l[-1200:]+"\n")
# sanity: single row, no stray newlines inserted
out.write("NROWS=%d\n"%sum(1 for x in lines if x.startswith('| K-Z3 |')))
out.write("DIFFLINES=%d\n"%len(lines))
out.close()
