p = "query-cosientist.md"
s = open(p).read()
c1 = s.count("第52回, K-Q1 deploy 整合再確認計測")
c2 = s.count("bench 第52回。cosientist 第51回の再 deploy")
open("bench52_verify.txt", "w").write(f"ev_in_row={c1} log_entry={c2}\n")
# also print the appended line fragment
i = s.find("第52回, K-Q1 deploy 整合再確認計測")
open("bench52_verify.txt", "a").write("ctx: " + s[max(0,i-120):i+80].replace("\n"," | ") + "\n")
