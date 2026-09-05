#!/usr/bin/env python3
"""rank 第50回: Iteration log に rank ブロックを追記する (重複適用防止付き)。"""
import io

PATH = "/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md"

ENTRY = """- 2026-09-05: rank 第50回。git pull --ff-only — remote 先端は a236a6b (rank 第49回)
  で 第49回以降の新規 evidence commit なし (falsify/bench は K-Q1 deploy 整合確認を
  非優先指定とする NEXT 待ちで帯 n 積み増しも非優先のため静穏 tick)。status 遷移なし
  (新規測定なし)、rank 順位変動なし (K-Q1 > K-Z2 > K-Z3 > K-S1 > K-S2)。
  NEXT: K-Q1 deploy 整合切分け (cosientist 担当: version 485fd2dc が PR #3 計装込み
  build か実査, 未反映なら再 deploy — 第49回 NEXT を維持)。
"""

with io.open(PATH, encoding="utf-8") as f:
    content = f.read()

if "rank 第50回" in content:
    print("already applied, skipping")
else:
    if not content.endswith("\n"):
        content += "\n"
    with io.open(PATH, "w", encoding="utf-8") as f:
        f.write(content + ENTRY)
    print("appended rank 第50回 entry")
