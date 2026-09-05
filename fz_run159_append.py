import io

path = '/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md'
with io.open(path, 'r', encoding='utf-8') as f:
    text = f.read()

anchor = '| open | falsify 2026-09-05 (K-Z3 18\u6642\u53f0 n \u7a4d\u307f\u5897\u3057 run158A\u2013C'
assert text.count(anchor) == 1, f"anchor count = {text.count(anchor)}"

evidence = ('falsify 2026-09-05 (K-Z3 18\u6642\u53f0 control \u4ed8\u304d\u518d\u8a08\u6e2c run159A\u2013C, run158 not-separated \u306e\u8ffd\u52a0 n + \u518d\u8a08\u6e2c, '
            '\u540c\u6e2c\u5b9a\u6cd5 n=20 \u00d7 3 + landing control, \u5225\u63a5\u7d9a curl, Tokyo, 18:18:23\u201318:18:36 JST, \u5168 80/80 200, '
            'host load1 8.85 \u306f production HTTP \u5b9f\u6e2c\u306e\u305f\u3081 gate \u5916): run159A cold(>=0.5s) 0/20 p50 0.055s / '
            'run159B cold 1/20 (0.981s, 8\u756a\u76ee\u306e\u5358\u767a) p50 0.056s / run159C cold 0/20 p50 0.050s \u2014 '
            'landing control (kotobase.net/, \u540c\u6642\u523b, n=20, \u5168 200) \u306f cold 0/20 p50 0.055s (max 0.089s) \u3068\u9759\u7a33\u3067 '
            'control \u5206\u96e2\u6210\u7acb\u3002run158A\u2013C \u578b\u306e search/landing \u540c\u6642\u5168\u4f53\u9045\u5ef6\u7a93 (250\u2013500ms \u5e2f) \u306f 15 \u5206\u5f8c\u306e\u518d\u8a08\u6e2c\u3067\u5373\u6642\u975e\u518d\u73fe \u2014 '
            'search p50 \u306f 50\u201356ms \u5e2f\u306b\u5fa9\u5e30\u3057 cold 1/60 \u306f run100A/116A \u578b\u306e\u8584\u3044\u5358\u767a\u578b\u3002'
            '18\u6642\u53f0\u306e\u78ba\u5b9a\u5024\u306f\u672c tick \u306e 1/60 \u306e\u307f (run158 \u5206\u306f not-separated \u306e\u305f\u3081\u5e2f\u767a\u73fe\u7387\u63a1\u7528\u4e0d\u53ef) \u3067\u3001'
            '\u5168\u4f53\u9045\u5ef6\u7a93\u306f\u5c40\u6240\u7684\u306a\u77ed\u6642\u9593\u7a93\u306e\u53ef\u80fd\u6027\u304c\u9ad8\u307e\u308a\u5e2f\u767a\u73fe\u7387\u306e\u78ba\u5b9a\u306b\u306f\u8ffd\u52a0 n \u8981\u3002'
            'status \u5224\u5b9a\u306f rank \u306b\u59d4\u306d\u308b (rank \u5c02\u9580)\u3002 ')

text = text.replace(anchor, '| open | ' + evidence + 'falsify 2026-09-05 (K-Z3 18\u6642\u53f0 n \u7a4d\u307f\u5897\u3057 run158A\u2013C', 1)

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('appended OK')
