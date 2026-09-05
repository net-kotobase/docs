path = "/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md"
with open(path) as f:
    text = f.read()

anchor = " bench 2026-09-04 (run60, 同測定法 n=20, 別接続 curl, Tokyo, 14:11 JST"
assert text.count(anchor) == 1, "anchor not unique"

new_ev = (" falsify 2026-09-05 (K-Z3 9時台 n 積み増し run123A–C, 同測定法 n=20 × 3 + landing control, "
          "別接続 curl, Tokyo, 09:48–09:49 JST, 全 60/60 + control 20/20 200, host load1 22.5 は production "
          "HTTP 実測のため gate 外): run123A cold(>=0.5s) 2/20 (0.831s/0.972s, p50 53ms, p90 180ms) / "
          "run123B cold 0/20 (p50 41ms, max 65ms) / run123C cold 0/20 (p50 40ms, max 75ms) — 計 2/60 発現。"
          "landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 41ms max 58ms と静穏で "
          "control 分離成立。9時台は run122A–C (5/60) に続き 2 セット連続で cold 突発 (9時台通算 7/120) — "
          "8時台 0/180 との対比で traffic 上昇に転じる 9時台で発現率が上がるという K-Z3 traffic 依存説を支持 "
          "(run122 と同方向の 2 例目で n 蓄積中)。status 判定は rank に委ねる (rank 専門)。")

text = text.replace(anchor, new_ev + anchor, 1)
with open(path, "w") as f:
    f.write(text)
print("appended")
