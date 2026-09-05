#!/usr/bin/env python3
"""rank 第50回 (追記): 4fa6a0c の run155 evidence (17時台) を取り込んで log を修正する。"""
import io, subprocess, re

REPO = "/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs"
PATH = REPO + "/query-cosientist.md"

FIXED_ENTRY = """- 2026-09-05: rank 第50回。git pull --ff-only は detached HEAD 構成のため git fetch
  net-kotobase + log --all 確認に置換 — remote 先端は 4fa6a0c (falsify 第54回,
  K-Z3 17時台 run155A–C: cold 4/1/0 per 20 = 5/60 ~8.3%, search のみ 1s 超外れ値,
  landing control 静穏 p50 53ms) で rank 第49回 (a236a6b) 以降の新規 evidence はこの
  1 本のみ。取り込み判定: 17時台は帯初計測で 5/60 ~8.3% — 12時台 (~8.3%) / 13時台
  (~6.7%) / 14時台 (~8.3%) と同水準の低位帯で、16時台 (9/60 ~15%) が中位寄りだった
  のに対し隣接帯で低位に戻る。control 分離成立下で search のみ 1s 超外れ値は
  search 局在の追加裾だが、帯別追加 n の限界情報利得低下は第49回確定のまま。
  status 遷移なし (K-Q1 は deploy 整合待ちのまま計装計測不可, K-Z2/K-Z3 は観測継続,
  K-S1/K-S2 は evidence なし)、rank 順位変動なし (K-Q1 > K-Z2 > K-Z3 > K-S1 > K-S2)。
  NEXT: K-Q1 deploy 整合切分け (cosientist 担当: version 485fd2dc が PR #3 計装込み
  build か実査, 未反映なら再 deploy — 第49回 NEXT を維持。bench/falsify は deploy 整合
  確認まで帯 n 積み増しは非優先)。
"""

with io.open(PATH, encoding="utf-8") as f:
    content = f.read()

# 差し替え: 初回に追記した不正確な第50回エントリを正確版へ置換
start = content.find("- 2026-09-05: rank 第50回。git pull --ff-only —")
if start == -1:
    print("entry not found, no edit")
else:
    end = content.find("\n- 2026-09-05:", start + 1)
    if end == -1:
        end = len(content)
    content = content[:start] + FIXED_ENTRY.rstrip("\n") + "\n" + content[end:]
    with io.open(PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("entry replaced")
