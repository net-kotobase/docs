import re
src = open("cos_iter51_kq1_backenddirect.mjs").read()
src = src.replace('const API = "https://backend.kotobase.net";', 'const API = "https://kotobase.net";')
open("bench52_kq1_edge.mjs", "w").write(src)
print("written")
