from pathlib import Path
p = Path('/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md')
txt = p.read_text()

anchor = '8時台通算 run195+196+197+199 で 3/240 (~1.3%) 低位帯。run186A 型群発は継続非再現。status 判定は rank に委ねる (rank 専門)。'
ev = ' bench 2026-09-06 (第78回, K-Z3 9時台帯初計測 run201A–C, 同測定法 n=20 × 3 + landing control, 別接続 curl, Tokyo, 09:22:36–09:23:58 JST, 全 80/80 200, host load1 9.9–16.9 (gate 7.5 超過 tick) は production HTTP 実測のため gate 外): run201A cold(>=0.507s) 5/20 (0.800/0.837/0.844/0.943/1.475s, 16–20番目の末尾集中クラスタ) p50 49ms / run201B cold 0/20 p50 38ms / run201C cold 0/20 p50 37ms — landing control (kotobase.net/signup, 同時刻, n=20, 全 200) は cold 0/20 p50 38ms max 53ms と静穏で control 分離成立、cold 群は search 側に局在。run201A の末尾集中型クラスタは run100A/116A 型帯内 1 窓即消失パターン (B/C で即消失)。9時台帯初計測は 2026-09-05 の run122 (5/60) / run123+124 (2/60, 0/60) に次ぐサンプルで低位帯寄り (本 tick 5/60 は 1 窓集中型)。status 判定は rank に委ねる (rank 専門)。'
assert txt.count(anchor) == 1, 'anchor not unique'
txt = txt.replace(anchor, anchor + ev)

log_entry = '- 2026-09-06: bench 第78回。09:22 JST tick。worktree detached HEAD のため fetch net-kotobase + rev-parse 比較で取り込み (fetch rc 0, HEAD 032b37b = fetch 後 net-kotobase/main 先端一致, ancestor rc 0, 乖離 0)。falsify 第77回 (run198A–C, 200A–C) と bench 第77回 (run199A–C), rank 第75回 (NEXT は K-Q1 cosientist 指定, bench フォールバック K-Z3 現在時刻帯 n 積み増し) を取り込み済み確認。live smoke 200 (/, /signup; pre-run 計測)。host load1 9.9–16.9 (gate 7.5 超過) のため local 測定は拒否。フォールバック (production HTTP 実測, gate 外): K-Z3 9時台帯初計測 run201A–C (同測定法 n=20 × 3 + landing control, 別接続 curl, 09:22:36–09:23:58 JST, 全 80/80 200): cold 5/0/0 per 20 = 5/60 (0.800–1.475s, run201A の 16–20番目末尾集中クラスタのみ), warm p50 37–49ms は静穏帯水準, control (kotobase.net/signup) cold 0/20 p50 38ms max 53ms 静穏で control 分離成立 — run201A クラスタは即消失 (B/C 0/20) の帯内 1 窓型。status 遷移なし (rank 専門)。secret は一切記録せず (curl のみ)。NEXT: 委ねる (rank 指定優先; フォールバックは K-Z3 現在時刻帯 n 積み増し継続)。\n'
# append log entry after the last bench 第77回 line (line 1759, last line of file per tail)
lines = txt.splitlines(keepends=True)
# find last non-empty line index of iteration log (file end)
assert lines[-1].endswith('\n') or True
txt = txt.rstrip('\n') + '\n' + log_entry
p.write_text(txt)
print('OK')
