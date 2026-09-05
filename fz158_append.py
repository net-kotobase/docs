import io

path = "query-cosientist.md"
with io.open(path, encoding="utf-8") as f:
    text = f.read()

anchor = "falsify 2026-09-05 (K-Z3 8時台 n 積み増し run121A–C"
idx = text.index(anchor)
entry = ("falsify 2026-09-05 (K-Z3 18時台 n 積み増し run158A–C, 同測定法 n=20 × 3 + landing control, "
         "別接続 curl, Tokyo, 18:01–18:03 JST, 全 80/80 200, host load1 13.34 は production HTTP 実測のため gate 外): "
         "run158A cold(>=0.5s) 1/20 p50 0.265s / run158B cold 1/20 p50 0.301s / run158C cold 5/20 p50 0.286s (max 0.636s) — "
         "landing control (kotobase.net/, 18:02, n=20) は cold 11/20 p50 0.515s と search と同時に全体的に上振れし、"
         "18:03 の再プローブでも landing cold 7/20 p50 0.409s / search cold 1/20 p50 0.291s と両方 250–500ms 帯 — "
         "search/landing 同時上振れのため control 分離不成立 (not-separated)。cold 計数 7/60 は帯発現率として採用不可で、"
         "18時台は夜帯としては異例の全体的遅延窓 (traffic ピーク直後の可能性) — 追加 n と control 付き再計測を rank 判断に委ねる。 "
         "status 判定は rank に委ねる (rank 専門)。 ")
text = text[:idx] + entry + text[idx:]
with io.open(path, "w", encoding="utf-8") as f:
    f.write(text)
print("inserted at", idx)
