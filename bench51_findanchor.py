import re
s = open("query-cosientist.md").read()
for m in re.finditer(r"。{1,2} \|", s):
    print(m.start(), repr(s[m.start()-40:m.start()+4]))
