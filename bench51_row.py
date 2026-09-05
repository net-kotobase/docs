import re
s = open("query-cosientist.md").read()
i = s.find("K-Z3 | worker |")
print(i)
print(repr(s[i:i+200]))
# find end of K-Z3 row
j = s.find("\n", i)
seg = s[i:j]
print("ROWLEN", len(seg))
print(repr(seg[-300:]))
