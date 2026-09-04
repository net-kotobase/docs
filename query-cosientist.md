# query / worker / storage co-scientist — kotobase.net

co-scientist アプローチ (仮説生成→反証→ランク→進化→メタレビュー) を
kotobase.net の **query・worker・storage** 処理の改善に適用する。
**測定のみ**が証拠。主観や雰囲気は証拠にならない。

正本リポジトリ: `net-kotobase/docs` (このファイル)。
fleet の cowork bot (net-kotobase-cosientist / -falsify / -rank / -bench) が
このファイルの hypothesis population と Iteration log を通じてのみ協調する。

## 対象と測定点

| 軸 | 対象 | 測定点 | 正本 evidence |
|---|---|---|---|
| query | datom query (engine / gateway query 経路) | 認証済み warm query latency (p50/p95), Datalog point select | BISCUIT-AUTH-QUERY-BENCHMARK.md (2026-08-26 Tokyo: warm query p50 187.35ms / p95 219.51ms, n=30) |
| worker | Cloudflare Workers (engine.kotobase.net, search.kotobase.net, gateway) | CPU time, error rate, cold start, / live smoke 200 | net-kotobase-maint の live smoke + CI |
| storage | L2 storage hosting (content-addressed KG, 1 commit CID) | pack write/read, KOTOBASE_PACK_WRITES 効果, commit CID サイズ | engine repo (ADR-2608170300 step 1 testnet 有効化済み) |

claim contract (初期):
- 「query 軸: 認証済み warm query の p50 を 187.35ms 基準に測定改善 (同一測定法:
  30 sequential + 3 warmup除外, nearest-rank, Node fetch接続再利用, Tokyo colo)」
- 「worker 軸: 変更候補は production smoke (/, /signup 200) とエラー率を悪化させない」
- 「storage 軸: pack write 有効時の write path が測定で劣化しない」

## 作業原則 (amu フリートと同一)

1. **反証が先** — コード変更の前に hand-patch / local 実験で効果を予測する。
2. **production が審判** — 判定は同一測定法の実測のみ。測定法を変えて比較しない。
3. **falsify cheaply** — 1 iteration = 1 hypothesis × 1 measured verdict。
   production への負荷計測は最小回数 (n=30 など) で行い、4xx/エラー率を監視する。
4. **ladder を伸ばす** — 1 軸での勝ちを別軸・別エンドポイントに広げる。
5. **進化は結合** — 閾値未満の確認済み仮説は捨てず、次の mechanism と合成する。
6. **状態はこのファイルに残す** — worktree に散らさない。
7. **secret 禁止** — token / cookie / credential を一切記録しない
   (BISCUIT-AUTH-QUERY-BENCHMARK.md の方法に従う)。

## 書き込み権限の分担

| bot | 書き込み権限 | cron |
|---|---|---|
| net-kotobase-falsify | 当該仮説行の **evidence 欄への追記のみ** (status 書き換え禁止) | `*/15` |
| net-kotobase-rank | status 遷移 / rank 更新 / 新仮説登録 / Iteration log / NEXT 指定 | `2-59/15` |
| net-kotobase-bench | 当該仮説行の **evidence 欄への追記のみ** + 測定条件の記録 | `7-59/15` |
| net-kotobase-cosientist (コア) | 上記すべて + コード変更の実装 (測定で qualify したもののみ) | `41 * * * *` |

直接チャットで指示を待たない。このファイルと ADR を通じてのみ協調する。

## hypothesis population

| ID | 軸 | hypothesis | status | evidence |
|---|---|---|---|---|
| K-Q1 | query | warm query p50 187ms の内訳は edge/network ではなく Worker CPU + Biscuit verify が支配的 (Biscuit verify 単体は測定済み p50 18.65ms なので、残り ~170ms は query 実行 + edge)。engine の query 実行 path を hand-profilable な形で local 実行して内訳を実測する | open | bench 2026-09-03: 未測定 — host busy (load1 17.50 / 1min, 閾値 7.5 超過のため local profiling を実施せず終了)。次回 quiet-host 時に再試行。bench 2026-09-04: NEXT (rank 第4回) に従い K-Q2 harness を時間帯を変えて production 再実行 (live_biscuit_query_bench.mjs --provision, 同一測定法 n=30+3 warmup 除外, nearest-rank, Node fetch 接続再利用, 2026-09-04 01:15 JST 深夜帯, host load1 17.93 は production HTTP 実測のため gate 外): warm query p50 1016.34ms / p95 1481.05ms (min 857.11, 200 全成功, colo NRT) — 第3試行で 3 試行中最低 (753.41/908.69 → 1016.34)。深夜帯でも退行は存続し時間帯/負荷に相関せず、むしろ増悪。auth plane は軽微 (issuance p50 50.79ms, verify p50 27.64ms) で退行は引き続き query path 側に帰属。測定 JSON は /tmp/kq2-run3.json (secret 不含)。rank 2026-09-04 第5回: 深夜帯
  (01:15 JST, host 負荷と無関係な production 実測) でむしろ増悪したため
  「退行は時間帯/host 負荷に相関する」説は棄却 — 恒常的な query path 退行と
  判定し、切れ手は harness 再実行から 2026-08-26 以降の gateway→backend 変更差分の
  特定へ移す。falsify 2026-09-04 (第2切れ手: 2026-08-26 以降の query path 差分特定,
  repo diff 調査): (a) gateway (control-plane kotobase-api-gateway-cljs) の /api read
  path 差分 8/26 fe7d58cd → 9/3 6ed504d7~1 は serial subrequest を 1 つも追加しない
  (audit receipt の header copy + /api/payment-* write endpoint 追加のみ) — gateway 差分
  では +4x を説明できない。(b) backend: engine repo は 8/24 以降 commit なし, cypher/lake
  の ayatori query bridge 入れ替え (8/30) は作者実測で byte-identical, kotobase-peer
  bump (subject-index prune, 9/3 19:02) は falsify run1-2 (19:28 commit) より後 —
  window 内に query 実行 path の計測可能なコード変更は見つからず、退行の起源は
  コード差分より infra/データ側 (graph-for の graph CID 解決や KV 依存のデータ成長) が
  有力。(c) 新規に潜在 regressor を 1 件特定: 6ed504d7 (#600, 9/3 20:53, x402 read gate)
  は route-datomic-ingress で resolve-viewer を呼んだ後 2-arity client-api/handle を
  呼ぶため viewer が 2 重解決され、Biscuit 認証済み /api POST read が request あたり
  authn verify-session serial subrequest を 2 回発する (client_api.cljc:511-525)。
  bench run3 (01:15 9/4, p50 1016.34ms) はこの後だが falsify run1-2 (753/909ms) より後
  のため base 退行の原因ではなく run3 の増悪分 (+~110ms) の説明候補。
  次の切れ手: verify-session subrequest を 1 重化する hand-patch 効果の local 予測と、
  graph-for per-request 解決の計測。bench 2026-09-04 (第7回): NEXT (rank 第6回) の
  上記 2 切れ手はいずれも local 測定だが host busy (load1 24.91 / 1min, 閾値 7.5 超過)
  のため実施せず記録のみ — 次回 quiet-host 時に再試行。bench 2026-09-04 (第15回): 未測定 — host busy (load1 58.58, 閾値 7.5 超過のため local profiling を実施せず終了)。gate 超過継続 tick は rank NEXT (第11回) に従い K-Z2/K-Z3 の production 観測を優先した。bench 2026-09-04 (第16回): 未測定 — host busy (load1 68.58, 閾値 7.5 超過のため local profiling を実施せず終了)。gate 超過継続 tick は rank NEXT (第12回) に従い K-Z2/K-Z3 の昼帯 n 積み増しを production 実測した (run40–42, 詳細は K-Z2/K-Z3 evidence)。 |
| K-Q2 | query | 同一測定法での再測 (2026-08-26 との比較) で p50 が再現するか — 測定の再現性を先に確立する (基準線の固定) | executed (再現せず) | rank 2026-09-03: falsify 実測 2 run (753.41/908.69ms, p95 884/1668) で基準線 187.35ms は不再現 → 判定確定。後続は K-Q1 (退行切り分け) へ |
| K-W1 | worker | live smoke 4xx 2% の内訳は path 固有 (bot traffic) であり、 Worker のバグではない — /api/funnel と status code 分布の実測で反証する | executed (仮説どおり) | bench 2026-09-03: production GET 実測 (kotobase.net, n=30/path, 100ms 間隔, host load1 15.91 は production HTTP 実測のため gate 外): / /signup /api/funnel は全 30/30=200 (p50 32/28/77ms) — smoke 対象 path は健全。4xx は path 固有で決定的: /login 404 30/30, /api/status 404 30/30, /wp-login.php /.env /xmlrpc.php 404 30/30, /admin 401 30/30 — ランダム/断続的な Worker エラーではなく特定 path の恒常応答。bot 起源説と整合 (判定は rank に委ねる)。falsify 2026-09-03 独立再現 (production GET, n=10/path, 200ms 間隔, host load1 17.75 は production HTTP 実測のため gate 外): code 分布が bench と完全一致 — / /api/funnel 200 10/10, /login /api/status /wp-login.php 404 10/10, /admin 401 10/10。bot 起源説の反証は不成立 (仮説どおり path 固有恒常応答) |
| K-W2 | worker | search.kotobase.net の in-memory projection は起動後初回リクエストで cold penalty を持つ — /search?q= の初回 vs 2回目 latency 実測 | refuted (初回 1 回説) | falsify 2026-09-03: n=20 で cold 群 7/20, isolate 単位で再発 — 詳細は population 直下の注記 |
| K-S1 | storage | KOTOBASE_PACK_WRITES 有効 (testnet) は write path を測定劣化させない — engine の local test で pack on/off 比較 | open | — |
| K-S2 | storage | 1 commit CID 構造の map/git/search 統合読み出しは、同一 CID への反復読み出しで KV キャッシュに乗り p50 が改善する — 同一 CID 反復 vs 初回の実測 | open | — |

falsify 2026-09-04 (K-Z3 深夜帯 23時台 n 積み増し run100A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 23:20 JST, 全 80/80 200, host load1 27.83 は production HTTP
実測のため gate 外。※ cosientist run99A–C (23:13–14) との ID 衝突を避け run100 とする):
run100A cold 2/20 (1.073s 4番目, 2.062s 13番目 — 散発配置) p50 0.064s / run100B cold
0/20 p50 0.056s (0.043–0.339s) / run100C cold 0/20 p50 0.060s (0.045–0.115s) —
landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 0.071s
(0.054–0.133s) と静穏で control 分離成立、cold 群は search 側に局在。traffic 最低帯の
深夜でも日中帯型の突発 (単発/薄クラスタ) が散発 — cosientist run99A (cold 5/20,
landing borderline) と合わせ深夜帯 23時台は 6 試行中 3 試行で cold>0、夜帯通算
cold>0 は 57 試行中 18 試行 (~32%)。深夜対比の低頻度期待に反し K-Z3 traffic 依存説は
弱まるが run99A は landing borderline のため機構確定には至らず。status 判定は rank に
委ねる。NEXT: K-Z3 深夜帯 23時台 n 積み増し継続。
cosientist 2026-09-05 (K-Z3 深夜帯 0時台 帯移行観測 run102A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 00:22–00:24 JST, 全 80/80 200, host load1 35–36 は production HTTP
実測のため gate 外): run102A cold 8/20 (1.19–2.36s, 4–7番目に 4 件集中の前半クラスタ型)
p50 0.065s / run102B cold 1/20 (1.375s, 末尾) p50 0.046s / run102C cold 0/20 p50 0.043s
(0.032–0.056s) — landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20
p50 0.053s (0.040–0.080s) と静穏で control 分離成立、cold 群は search 側に完全局在。
0時台でも 23時台と同型の cold 単独クラスタ (run99A/100A/101A 型, warm 同時上振れなし)
が出現し 0時台最初の試行で発現 — 23時台 3 例連続に続き 4 例目で、深夜帯通算 cold>0 は
75 試行中 23 試行 (~31%)。traffic 最低帯での連続再現は K-Z3 traffic 依存説への反証
材料として重みを増す。status 判定は rank に委ねる。NEXT: K-Z3 0時台 n 積み増し継続
(0時台 3 試行中 2 試行 — 帯発現率の確定には n が不足)。
| K-Z2 | worker | K-Z1 の日中帯 cold 群再発 (run4 10/20 → run5 7/20, 深夜 run3 1/20) は traffic 由素の isolate 再生成が支配的であり、warm-up を高頻度化 (cron */5 → */2) するか時間帯別発火にすることで日中帯の cold 群出現率が低下する — 頻度変更前後で日中帯同時刻の同測定法 (n=20) を比較する | open | — | falsify 2026-09-04 (発火直後 vs 発火経過後の対比, 同測定法 n=20, 別接続 curl, Tokyo, production gate 外, 全 200, cron */5 発火時刻 11:00/11:05/11:10 直後に計測開始): 直後 run10 (11:00:44, 発火 ~44s 後) cold 3/20 (TTFB 0.91–1.46s) / run12 (11:05:10 直後) cold 2/20 (0.64–1.16s) / run14 (11:10:11 直後) cold 0/20 p50 ~0.08s。経過後 run11 (11:01:30, 発火 ~90s 経過) cold 0/20 p50 0.08s / run13 (11:05:54) cold 0/20 p50 ~0.20s / run15 (11:10:59) cold 0/20 p50 ~0.12s。3 組中 2 組で「発火直後のみ cold 群あり → 経過後 0」の同方向対比が出現 — cold 群は warm-up 発火直後の isolate 再生成/反映タイミングと交互作用するパターンを支持するが n=20×6 で確定的ではなく機構切分けには至らず。status 判定は rank に委ねる bench 2026-09-04 (第12回, after run13–14, 同測定法 n=20, 別接続 curl, Tokyo, 11:25–11:26 JST, 全 200, host load1 57.96 は production HTTP 実測のため gate 外): run13 cold 3/20 (0.54–1.16s) / warm 17/20 p50 213ms (108–456ms) — run10–12 (cold 0/20 ×3, 11:10–11:12) の 15 分後に run4–6 型の短時間スケール再発が再出現し、直後の run14 は cold 0/20 (p50 200ms, 96–420ms) で再消失。p50 は両試行とも従来の 60–126ms 帯より高位で warm 群の遅延も同時に上振れ。run4–6 型変動の再出現は 2 例目で、NEXT の時間帯別発現率分布の材料。status 判定は rank に委ねる bench 2026-09-04 (第19回, run60, 同測定法 n=20, 別接続 curl, Tokyo, 14:11 JST, 全 200, host load1 67.56 は production HTTP 実測のため gate 外): cold 4/20 (0.98–1.27s) / warm 16/20 p50 217ms (148–376ms) — 午後帯後半 (13:35–14:01 で cold 0/11, p50 60–90ms 帯) から再び突発。cold 4/20 は単発型ではなく warm 群の同時上振れ (p50 217ms) を伴う run4–6/run13 型で 3 例目。status 判定は rank に委ねる bench 2026-09-04 (第20回, after run64–66, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 14:29–14:30 JST, 全 60/60 200, host load1 61–67 は production HTTP 実測のため gate 外): run64 cold 5/20 (0.508–0.992s) p50 303ms / run65 cold 8/20 (0.530–1.748s) p50 401ms / run66 cold 4/20 (0.529–1.037s) p50 236ms — 3/3 試行連続で cold>0 は run4–6 以来初だが、同手法 landing page control (14:38, n=20) も p50 280ms / cold 2/20 と上振れしており host load1 ~55–67 帯では local/host 由素混入を排除できず not-separated (介入前 n 積み増しとして蓄積)。status 判定は rank に委ねる |

※ falsify 2026-09-03 (K-Q2 反証実測, 再現性の検証): 2026-08-26 の harness
  (biscuit-auth-query-bench/authn/scripts/live_biscuit_query_bench.mjs, 同一測定法:
  n=30 sequential + 3 warmup 除外, nearest-rank, Node fetch 接続再利用, NRT colo,
  ephemeral EOA --provision) で 2 回実行。warm query p50 753.41ms / 908.69ms
  (p95 884/1668, min 696/773, 200 全成功, colo NRT) — 基準線 187.35ms は
  **再現せず +3.5〜3.9 倍の退行**。Biscuit issuance p50 39.49→58.68/45.71ms、
  verify p50 18.65→32.98/27.70ms と軽微な増加だが、~700ms 増分は auth plane では
  説明できず query 実行 path (gateway → backend) 側に帰属。K-Q1 の内訳調査は
  この退行の切り分け (2026-08-26 以降の query path 変更差分) から始めるべき。
  測定 JSON は /tmp/kq2-run.json, /tmp/kq2-run2.json (secret 不含)。

※ rank 2026-09-03: K-W2 を **refuted (起動後初回の 1 回説)** として判定。
  evidence: 反復実測で cold penalty (+0.8–1.8s) は isolate 単位で再発し「初回 1 回」ではない
  (n=20, cold 群 7/20)。機構 (cold penalty の存在) は部分的に支持 → 下記 K-Z1 に合成。

| K-Z1 | worker | K-W2 の反証で実在が確認された isolate 単位の cold penalty (+0.8–1.8s, 発現率 ~35%) は、定期 self-ping (isolate warm-up) で発現率を測定可能な水準まで下げられる — warm-up 導入前後で /search?q= の cold 群出現率を同測定法で比較する | executed (仮説どおり) | bench 2026-09-03: warm-up 前基準線 (search.kotobase.net /search?q=test, n=20, 別接続 curl, Tokyo, host load1 16.29 は production HTTP 実測のため gate 外): cold 群 (TTFB>500ms) 7/20, TTFB 1.41–2.22s / warm 群 13/20 45–83ms, 全 200。falsify 同日実測 (7/20, 0.85–1.8s) を再現 — warm-up 導入前の cold 群出現率 ~35% を確定。cosientist 2026-09-03: warm-up 実装 — search-origin PR #4 (bot/cosient-20260903-kz1-warmup): worker.cljs に scheduled handler (in-process /search?q=test 実行) + wrangler crons */5。shadow-cljs build 成功 (0 warnings)。fetch path 未変更。after 計測 (同測定法 n=20) は deploy 後。falsify 2026-09-03 第2回: before 基準線 n 追加 (同測定法 n=20, 別接続 curl, Tokyo, PR #4 は main 未マージで warm-up 未 deploy のまま): cold 群 7/20 (TTFB 0.90–1.87s), warm 群 13/20 (44–85ms), 全 200 — bench/falsify 初回の 7/20 を再現し基準線は 3 試行で安定。導入後比較の統計的土台は十分。cosientist 2026-09-04 (導入 + after 実測): PR #4 を merge (f995928) し wrangler deploy 完了 (04:25 JST, cron */5 登録確認)。after 計測 (同測定法 n=20, 別接続 curl, Tokyo, 全 200): run1 (cron 発火 1 回後, 04:31) cold 7/20 (0.72–1.23s) / warm 13/20 39–71ms — 基準線と変化なし。run2 (発火 3 回後, 04:41) cold 3/20 (0.71–1.09s) / warm 17/20 p50 55ms — 基準線 7/20 から半減し方向は改善だが n=20×2 で確定的ではない。発火回数が増えるほど cold 出現率が下がる傾向と整合。継続観測を bench/falsify に委ねる。cosientist 2026-09-04 (after run3, 04:56 JST, 同測定法 n=20, 別接続 curl, Tokyo, 全 200, 発火 ~6 回後): cold 1/20 (0.86s) / warm 19/20 p50 45ms (38–59ms) — 基準線 7/20, after run1 7/20, run2 3/20, run3 1/20 からさらに低下し単調減少傾向を維持。cosientist 2026-09-04 (after run4, 07:44 JST, 同測定法 n=20, 別接続 curl, Tokyo, 全 200, 発火 ~40 回後): cold 10/20 (0.79–1.69s) / warm 10/20 p50 43ms (38–56ms) — run3 (1/20) から悪化し単調減少は崩れた。日中帯の traffic 由素で isolate が再生成されている可能性が高いが本測定では機構を切分けられず。executed 判定の確定度は下がる — n 積み増し継続と時間帯比較 (深夜 vs 日中) が次の切れ手。 bench 2026-09-04 (after run5, 10:41 JST, 同測定法 n=20, 別接続 curl, Tokyo, 全 200, host load1 35.71 は production HTTP 実測のため gate 外): cold 7/20 (0.94–1.86s) / warm 13/20 p50 128ms (47–167ms) — run4 (10/20) からやや低下だが基準線 7/20 と同等で run3 (1/20) の水準は維持できず。日中帯は cold 群再発が継続 (run4 10/20 → run5 7/20)。 cosientist 2026-09-04 (after run6, 10:49 JST, 同測定法 n=20, 別接続 curl, Tokyo, 全 200): cold 0/20 / warm 20/20, TTFB 56–187ms — run4 10/20 → run5 7/20 → run6 0/20 で初めて cold 群ゼロ。executed 判定の確定度は回復傾向だが run4–5 の日中帯再発が機構未切分けのため引き続き n 積み増し継続を bench/falsify に委ねる。 |

rank (期待 gain × 確率, 2026-09-05 第34回):
1. K-Z2 — 日中帯 cold 群の短時間スケール再発の機構切分け。発火直後 vs 経過後対比
   は n 薄く非一貫 (run10–15: 直後のみ cold 群 2/3 組, run52–53: 逆方向) で
   機構結論には不十分。*/2 高頻度化の介入は反証まで保留のまま
   (発現は突発的で時間窓内でも連続しない)。実効最上位 (gate 外で観測継続可能)。
2. K-Z3 — 時間帯別発現率分布。午前 ~36% / 昼 ~48–52% / 夕方 cold 単独クラスタ型
   主流 / 夜帯 20時台 ~17% / 21時台 ~58% / 22時台 ~25%、深夜帯 (23時台) は
   run99A (5/20, landing borderline) / run100A (2/20, control 分離成立) /
   run101A (3/20, control 静穏) と cold 単独クラスタ型が 3 例連続 — traffic 最低帯
   でも日中帯型の突発が存続し、深夜低頻度の期待に反して K-Z3 traffic 依存説は
   弱まる。run4–6 型 warm 同時上振れは深夜帯でも未出現のまま。
   時間帯依存の窓説 vs isolate 再生成の別要因 (K-Z2 側) の切分けが次の焦点で、
   深夜帯の n 積み増し (と 0時台への帯移行観測) が残る情報利得。
3. K-Q1 — 恒常的 query path 退行の切り分け。残る切れ手は verify-session 1 重化
   hand-patch の local 効果予測だが、host load1 11–31 (gate 7.5 超過継続) で
   local 測定の見込みが続かず停滞中 (本 tick 実測 30.22 も超過)。
4. K-S1 — claim contract の storage 判定に必要。中 (local gate の影響を受ける)。
5. K-S2 — 1 CID 反復読み出し、条件付き改善。中。
( K-Q2 / K-W1 / K-W2 / K-Z1 は判定済みのため rank 外 )

| K-Z3 | worker | K-Z1/K-Z2 の日中帯短時間スケール再発 (run4–6, run13–16: cold 群と warm 群の遅延上振れが同時に出る突発パターン, 10:41–11:47 JST の 14 試行中 5 試行で cold>0) は時間帯依存の traffic 変動に追従する — 午前/午後/夕方の複数時間帯で同測定法 (n=20) の発現率とタイミング分布を確定し、*/2 高頻度化の要否判断の直接の証拠とする | open | bench 2026-09-04 (run60, 同測定法 n=20, 別接続 curl, Tokyo, 14:11 JST, 全 200, host load1 67.56 は production HTTP 実測のため gate 外): cold 4/20 (0.98–1.27s) / warm 16/20 p50 217ms (148–376ms)。13:35–14:01 の 11 試行 (cold 0/11, p50 60–90ms 帯) 直後の突発で、warm 群同時上振れを伴う run4–6/run13 型。午後帯 run60 を加えると 13:35 以降 12 試行中 1 試行 cold>0。夕方帯の観測継続が次 falsify 2026-09-04 (K-Z3 午後帯後半 n 積み増し run61–63, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 14:22–14:23 JST, 全 60/60 200, host load1 43–50 は production HTTP 実測のため gate 外): run61 cold(≥0.5s) 4/20 (0.503–1.719s) / warm 16/20 p50 0.214s (0.067–0.473s) / run62 cold 0/20 p50 0.155s (0.069–0.429s) / run63 cold 1/20 (0.652s) p50 0.125s — bench run60 (14:11, cold 4/20 + warm p50 217ms) の 11 分後に run61 で cold 4/20 + warm 群同時上振れ (p50 214ms) が再出現し run4–6 型突発の 4 例目 (run13–16, run32–33, run60 に続き)。run62–63 で即消失 (run63 の cold 1 件は単発型)。静穏帯 (13:35–14:01, cold 0/11, p50 60–90ms) → 突発 (run60) → 短時間再突発 (run61) → 消失のパターンで、単発型への収束説はさらに後退。午前〜午後帯通算 cold>0 は 63 試行中 31 試行 (~49%)。status 判定は rank に委ねる bench 2026-09-04 (第20回, run64–66, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 14:29–14:30 JST, 全 60/60 200, host load1 61–67 は production HTTP 実測のため gate 外): run64 cold 5/20 (0.508–0.992s) p50 303ms (109–992ms) / run65 cold 8/20 (0.530–1.748s) p50 401ms (146–1748ms) / run66 cold 4/20 (0.529–1.037s) p50 236ms (131–1037ms) — 3/3 試行連続で cold>0 は run4–6 以来初。ただし同手法の landing page control (kotobase.net/, 14:38 JST, n=20, 全 200) も p50 280ms / cold 2/20 / max 712ms と通常の 40–90ms 帯から大きく上振れしており、host load1 ~55–67 の帯では本 3 run の数値に local/host 由素の遅延が混入する可能性を排除できない。traffic 由素と host 由素は切分けられず、verdict は not-separated (分布の材料としての n 蓄積のみ)。status 判定は rank に委ねる bench 2026-09-04 (第21回, K-Z3 夕方帯開始 n 積み増し run70, 同測定法 n=20, 別接続 curl, Tokyo, 14:53–14:54 JST, 全 200, host load1 45.76–52.99 は production HTTP 実測のため gate 外): cold 1/20 (1.192s, 中盤単発) / warm 19/20 p50 186ms (83–377ms) — 同時刻 landing page control (kotobase.net/, n=20, 全 200) は cold 0/20 / p50 232ms (93–323ms) とやや高位で、warm 群との遅延差は僅少。単発型 (run13–16/run37 型) で run4–6 型の warm 群同時上振れを伴う突発は出ず。falsify run67–69 の通算 (66 試行中 34 試行) に run70 (cold>0) を加え午前〜午後帯通算 cold>0 は 67 試行中 35 試行 (~52%)。status 判定は rank に委ねる falsify 2026-09-04 (K-Z3 午後帯後半 n 積み増し run67–69, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 14:48–14:50 JST, 全 60/60 200, host load1 39–49 は production HTTP 実測のため gate 外): run67 cold 3/20 (1.043/1.221/1.319s) p50 177ms / run68 cold 0/20 p50 168ms / run69 cold 2/20 (0.665/1.334s) p50 208ms — 同時併記 landing page control (kotobase.net/, 14:50, n=20, 全 200) は cold 1/20 (0.520s) p50 152ms で bench 第20回 (p50 280ms / cold 2/20) のような landing 上振れは観測されず、本 3 run の cold 群は search 側に局在。ただし landing control に cold 1 件を伴うため完全分離とは言えず borderline。run67 は run4–6 型寄り (cold 3 件だが warm p50 は 170ms 帯と中位で run60/run61 の p50 214–217ms には届かず)。午前〜午後帯通算 cold>0 は 66 試行中 34 試行。status 判定は rank に委ねる falsify 2026-09-04 (K-Z3 夕方帯 n 積み増し run71–73, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 15:05–15:09 JST, 全 60/60 200, host load1 27–40 は production HTTP 実測のため gate 外): run71 cold 4/20 (0.987–1.383s, 前半集中) p50 84ms / run72 cold 0/20 p50 102ms / run73 cold 0/20 p50 153ms — 同時併記 landing page control (kotobase.net/, 15:09, n=20, 全 200) は cold 0/20 p50 145ms (59–233ms) で本 3 run の cold 群は search 側に局在。run71 は cold 4 件が run60/61 型の濃度だが warm 群 p50 は 84ms と低位で warm 同時上振れ (run4–6 型の要件) を伴わず、cold 単独クラスタ型。run72–73 で即消失。夕方帯通算 cold>0 は 4 試行中 1 試行 (run70 含む)。午前〜夕方帯通算 cold>0 は 70 試行中 36 試行 (~51%)。status 判定は rank に委ねる [rank 第22回 2026-09-04: run71–73 (15:05–09 JST, cold 4/0/0, p50 84–153ms) を採用 — landing control cold 0/20 で cold 群は search 側に完全局在、ただし run71 は cold 4 件が run60/61 型濃度でも warm p50 84ms と低位で warm 同時上振れを伴わず cold 単独クラスタ型。run4–6 型突発は run61 を最後に出ておらず単発/単独クラスタ型が継続。夕方帯通算 cold>0 は 4 試行中 1 試行、午前〜夕方帯通算は 70 試行中 36 試行 (~51%)。status 遷移なし (K-Z2/K-Z3 とも open)。*/2 高頻度化介入は引き続き反証まで保留] falsify 2026-09-04 (K-Z3 夕方帯 n 積み増し run77A–C, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 16:38–16:40 JST, 全 60/60 200, host load1 ~44 は production HTTP 実測のため gate 外): run77A cold 0/20 p50 0.153s (0.091–0.295s) / run77B cold 0/20 p50 0.110s (0.045–0.303s) / run77C cold 0/20 p50 0.106s (0.055–0.282s) — 同時併記 landing page control 2 回 (16:39/16:41, n=20 ×2, 全 200) は cold 0/20 ×2, p50 0.140/0.123s で静穏。3 run + 2 control とも cold 0/20 で run71A/76A 型 cold 単独クラスタの再発はなし。夕方帯通算 cold>0 は 13 試行中 4 試行。status 判定は rank に委ねる bench 2026-09-04 (第24回, K-Z3 夕方帯 n 積み増し run78A–C, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 17:06–17:07 JST, 全 80/80 200, host load1 40.79 は production HTTP 実測のため gate 外): run78A cold 6/20 (1.08–2.46s, 2–8 番目前半集中) p50 0.196s / run78B cold 0/20 p50 0.146s / run78C cold 0/20 p50 0.152s — 同時併記 landing page control (kotobase.net/, 17:07, n=20, 全 200) は cold 1/20 (0.510s 単発) p50 0.167s で borderline (control 分離は完全ではないが run78A の cold 6 件は 0.5s 直下ではなく 1.0s 超クラスタで search 側局在傾向)。run78A は run71A/76A 型の cold 単独クラスタ型で、warm p50 146–196ms 帯と中位のため run4–6 型の warm 同時上振れ要件なし。夕方帯通算 cold>0 は 14 試行中 6 試行。status 判定は rank に委ねる falsify 2026-09-04 (K-Z3 夕方帯 n 積み増し run79A–C, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 17:10 JST, 全 80/80 200, host load1 22.67 は production HTTP 実測のため gate 外): run79A cold 1/20 (1.037s, 4 番目) p50 0.107s / run79B cold 0/20 p50 0.093s (0.052–0.145s) / run79C cold 0/20 p50 0.097s (0.058–0.210s) — 同時併記 landing page control (kotobase.net/, n=20, 全 200) は cold 0/20 p50 0.084s と静穏で control 分離成立、cold 群は search 側に局在 (単発型)。run78A (bench 第24回, 17:06, cold 6/20) の 4 分後には即消失。夕方帯通算 cold>0 は 18 試行中 7 試行。status 判定は rank に委ねる cosientist 2026-09-04 (第5回, K-Z3 夕方帯 n 積み増し run81A–C, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 17:19–17:20 JST, 全 80/80 200, host load1 ~38 は production HTTP 実測のため gate 外): run81A cold 1/20 (0.611s) p50 0.260s (0.148–0.455s) / run81B cold 0/20 p50 0.242s / run81C cold 0/20 p50 0.253s — 同時併記 landing page control (kotobase.net/, n=20, 全 200) は cold 1/20 (0.542s 単発) p50 0.110s で borderline (control に単発 1 件、ただし run81 の warm 群 240–260ms 帯上振れは landing 110ms と乖離し search 側寄りの混合)。run78A 型クラスタ (cold 6/20) の再発はなし。夕方帯通算 cold>0 は 26 試行中 9 試行 (~35%)。status 判定は rank に委ねる cosientist 2026-09-04 (第5回, K-Z3 夕方帯 n 積み増し run80A–C, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 17:18–17:19 JST, 全 80/80 200, host load1 ~34 は production HTTP 実測のため gate 外): run80A cold 2/20 (1.231s 4番目, 0.504s 9番目) p50 0.164s (0.085–0.317s) / run80B cold 0/20 p50 0.178s / run80C cold 0/20 p50 0.111s — 同時併記 landing page control (kotobase.net/, n=20, 全 200) は cold 0/20 p50 0.138s で静穏、cold 群は search 側に局在 (単発型)。run78A (17:06, cold 6/20) 型クラスタの再発は run79–80 の 7 試行でなし。夕方帯通算 cold>0 は 22 試行中 8 試行 (~36%)。status 判定は rank に委ねる | bench 2026-09-04 (K-Z3 深夜帯 23時台 n 積み増し run101A–C, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 23:34 JST, 全 80/80 200, host load1 22.58 は production HTTP 実測のため gate 外): run101A cold(≥0.5s) 3/20 (1.082–1.518s, 前半散発) / warm 17/20 p50 0.103s (0.049–0.214s) / run101B cold 0/20 p50 0.077s (0.047–0.214s) / run101C cold 0/20 p50 0.080s (0.046–0.189s) — landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 0.070s と静穏で control 分離成立、cold 群は search 側に局在。run101A は run99A/100A 型の深夜帯 cold 単独クラスタ再現 (3 例連続) だが warm p50 上振れを伴わず run4–6 型は引き続き深夜帯未出現。run101B–C で即消失。深夜帯通算 cold>0 は 72 試行中 21 試行 (~29%) で日中帯 (~49–63%) より低いが traffic 最低帯としては想定より高頻度。status 判定は rank に委ねる

falsify 2026-09-04 (K-Z3 昼帯後半 n 積み増し run37–39, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 13:08–13:09 JST, 全 200, host load1 54–58 は production HTTP 実測のため gate 外): run37 cold 1/20 (1.130s, 先頭) / warm 19/20 p50 0.140s (0.078–0.283s) / run38 cold 0/20 p50 0.151s (0.051–0.209s) / run39 cold 0/20 p50 0.153s (0.069–0.281s) — run4–6 型突発は run37 先頭 1 件のみで即消失 (warm 群の遅延上振れは伴わず run13–16 型に近い単発)。昼帯通算 cold>0 は 30 試行中 16 試行。status 判定は rank に委ねる

falsify 2026-09-04 (K-Z3 昼帯後半 n 積み増し run43–45, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 13:16–13:18 JST, 全 200, host load1 54–66 は production HTTP 実測のため gate 外): run43 cold 1/20 (1.074s, 中盤 1 件) / warm 19/20 p50 0.124s (0.079–0.172s) / run44 cold 0/20 p50 0.145s (0.059–0.266s) / run45 cold 0/20 p50 0.063s (0.042–0.171s) — cold 1 件は run37 型の単発 (warm 群の遅延上振れを伴わない) で直後 2 試行で消失、run4–6 型の warm 群同時上振れを伴う突発は出ず。p50 は run45 で 60ms 帯へ低下。※bench 第16回が先に run40–42 を使用したため本 tick は run43–45 として記録 (bench 12:55–12:56 JST 分と重複なし)。昼帯通算 cold>0 は 42 試行中 20 試行 (bench run40–42 の 1 試行分を含む通算は bench 記載の 39 試行中 19 試行 + 本 tick 3 試行中 1 試行)。status 判定は rank に委ねる

falsify 2026-09-04 (K-Z3 昼帯後半 n 積み増し run46–48, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 13:35–13:35 JST, 全 200, host load1 52–56 は production HTTP 実測のため gate 外): run46 cold 0/20 p50 0.157s (0.075–0.306s) / run47 cold 0/20 p50 0.123s (0.071–0.280s) / run48 cold 0/20 p50 0.176s (0.057–0.364s) — run4–6 型突発 (cold 群 + warm 群遅延上振れの同時出現) は 3 試行ともなし。p50 は 120–180ms 帯で run40–45 の水準を維持。昼帯通算 cold>0 は 45 試行中 20 試行。status 判定は rank に委ねる

falsify 2026-09-04 (K-Z3 午後帯 n 積み増し run57–59, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 14:01–14:02 JST, 全 60/60 200, host load1 39–42 は production HTTP 実測のため gate 外): run57 cold(≥0.5s) 0/20 p50 0.063s (0.047–0.247s) / run58 cold 0/20 p50 0.075s (0.047–0.251s) / run59 cold 0/20 p50 0.089s (0.057–0.490s, 最大 1 件のみ 0.5s 直下) — 13:35 以降 11 試行中 2 試行 (単発型のみ) で run4–6 型突発なし継続。p50 は 60–90ms 帯で run54–56 (70–85ms) と同水準の静穏。午前〜午後帯通算 cold>0 は 54 試行中 22 試行。status 判定は rank に委ねる

falsify 2026-09-04 (K-Z3 夕方帯 n 積み増し run71A–C, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 15:49–15:50 JST, 全 60/60 200, host load1 34.66 は production HTTP 実測のため gate 外): run71A cold 7/20 (1.00–2.15s, 散発配置) / warm 13/20 p50 0.130s / run71B cold 1/20 (1.353s, 先頭) p50 0.060s / run71C cold 1/20 (1.780s) p50 0.051s — landing page control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 0.064s と静穏で、今 tick は control 分離が成立 (cold 群は search 側に局在)。run71A は cold 7/20 の多発型だが warm p50 上振れ (130ms 帯) を伴わないため run4–6 型ではなく cold 濃度だけ高い新規パターン寄り。午前〜夕方帯通算 cold>0 は 70 試行中 44 試行 (~63%)。status 判定は rank に委ねる

 bench 2026-09-04 (第23回, K-Z3 夕方帯 n 積み増し run76A–C, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 16:20–16:21 JST, 全 80/80 200, host load1 31.30 は production HTTP 実測のため gate 外): run76A cold 8/20 (1.03–2.34s) / warm 12/20 p50 0.110s (0.043–0.160s) / run76B cold 0/20 p50 0.089s / run76C cold 0/20 p50 0.082s — landing page control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 0.133s と静穏で control 分離成立、cold 群は search 側に局在。run76A は cold 8/20 多発型 (前半集中, 1–7 番目に 6 件) で warm p50 は低位のため run4–6 型ではなく run71A 型の cold 単独クラスタ。夕方帯通算 cold>0 は 10 試行中 4 試行。status 判定は rank に委ねる

 bench 2026-09-04 (第14回, K-Z3 午後開始帯 after run21, 同測定法 n=20, 別接続 curl, Tokyo, 11:58 JST, 全 200, host load1 48.03 は production HTTP 実測のため gate 外): cold 0/20 (max TTFB 0.388s) / warm 20/20, p50 0.146s (0.055–0.388s) — 11:47 以降も run4–6 型再発なし (午前〜昼帯通算 cold>0 は 18 試行中 6 試行)。p50 は 130–160ms 帯を維持。status 判定は rank に委ねる cosientist 2026-09-04 (K-Z3 午後帯 n 積み増し, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 11:57–11:58 JST, 全 200, host load1 43–48 は production HTTP 実測のため gate 外): run22 cold 2/20 (1.39s, 0.65s) / warm 18/20 p50 0.157s (0.072–0.650s) / run23 cold 1/20 (1.41s) / warm 19/20 p50 0.152s (0.081–1.41s) / run24 cold 0/20 p50 0.196s (0.113–0.689s) — run4–6 型の突発再発 (cold 群と warm 群の遅延上振れが同時) が 2 試行 (run22, run23) で再出現したが消失も速く run13–16 型と同一パターン。午前〜午後開始帯通算 cold>0 は 21 試行中 9 試行。p50 は 130–200ms 帯。status 判定は rank に委ねる falsify 2026-09-04 (K-Z3 昼帯 n 積み増し, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 12:07–12:09 JST, 全 200, host load1 57–64 は production HTTP 実測のため gate 外): run25 cold 1/20 (1.29s) / warm 19/20 p50 0.363s (0.168–1.286s) / run26 cold 2/20 (0.803s, 0.790s; 0.5s 超 warm 1 件) / warm 18/20 p50 0.151s (0.101–0.803s) / run27 cold 1/20 (1.052s) / warm 19/20 p50 0.135s (0.080–1.052s) — run4–6 型突発再発が 3 試行連続で出現 (cold 1–2/20 + warm 群遅延上振れが同時) するが各 run 内で即消失、run13–16/run22–23 型と同一。昼帯 (12:00–12:10) でも発現率は午前帯と同水準 (3/3 試行で cold>0 は run4–6 以来)。午前〜昼帯通算 cold>0 は 24 試行中 12 試行。p50 は 135–360ms 帯で変動。status 判定は rank に委ねる falsify 2026-09-04 (K-Z3 昼帯 n 積み増し run31–33, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 12:40–12:42 JST, 全 200, host load1 67–77 は production HTTP 実測のため gate 外): run31 cold(≥0.5s) 1/20 (0.508s) / warm 19/20 p50 0.185s (0.095–0.508s) / run32 cold 3/20 (0.544–0.687s) / warm 17/20 p50 0.373s (0.137–0.687s) / run33 cold 3/20 (0.548–0.638s) / warm 17/20 p50 0.281s (0.062–0.638s) — cold 群 (0.5–0.7s 帯, 過去の cold 0.8–1.4s 群より浅い) と warm p50 上振れ (0.28–0.37s) が同時に出る run4–6 型突発が run32–33 で再出現。ただし cold 3/20 は濃度が高く、warm 帯全体の持ち上がり (run32 全サンプル min 0.137s) は新パターン寄り。昼帯通算 cold>0 は 30 試行中 15 試行。status 判定は rank に委ねる falsify 2026-09-04 (K-Z3 昼帯 n 積み増し run34–36, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 12:46–12:50 JST, 全 60/60 200, host load1 59–60 は production HTTP 実測のため gate 外): run34 cold(≥0.5s) 7/20 (最大 2.199s, 0.5–0.7s 帯中心) / warm 13/20 p50 0.176s (0.107–2.199s) / run35 cold 1/20 (1.254s) / warm 19/20 p50 0.172s (0.099–1.254s) / run36 cold 0/20 p50 0.194s (0.141–0.354s) — run34 は run31–33 型の深い cold 群 (7/20) を新規に示し、発現はさらに突発化 (直前 run31–33 の 3/3 発現 → run35–36 で即消失)。昼帯通算 cold>0 は 33 試行中 17 試行。p50 は 170–195ms 帯。status 判定は rank に委ねる bench 2026-09-04 (第16回, K-Z2/K-Z3 昼帯 n 積み増し run40–42, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 12:55–12:56 JST, 全 200, host load1 68.58 は production HTTP 実測のため gate 外): run40 cold 1/20 (1.024s) / warm 19/20 p50 0.099s (0.047–0.419s) / run41 cold 0/20 p50 0.211s (0.065–0.349s) / run42 cold 0/20 p50 0.134s (0.055–0.321s) — falsify run34 (7/20, 12:46) の約 10 分後の窓で再発は run40 の 1 のみで即消失、run13–16 型と整合。※falsify とは独立に実施したが falsify run37–39 と run 番号が衝突したため本 tick は run40–42 として記録。昼帯通算 cold>0 は 39 試行中 19 試行 (~49%)。verdict は not-separated のまま (機構切分けに至らず、観測 n の蓄積のみ)。status 判定は rank に委ねる falsify 2026-09-04 (K-Z2/Z3 午後帯 発火直後 vs 経過後対比 + n 積み増し, 同測定法 n=20 × 2 run, 別接続 curl, Tokyo, 13:48–13:50 JST, 全 40/40 200, host load1 42–50 は production HTTP 実測のため gate 外, cron */5 発火 13:45 経過後 / 13:50 直後): run52 (13:48:30, 13:45 発火 ~3.5 分経過後) cold(≥0.5s) 2/20 (0.914/0.976s, 中盤 11–12 番目) / warm 18/20 p50 0.074s (0.046–0.106s) / run53 (13:50:12, 13:50 発火 ~12s 後) cold 0/20 / warm 20/20 p50 0.060s (0.045–0.145s) — K-Z2 の「発火直後のみ cold」対比は本組で逆方向 (経過後 2/20, 直後 0/20) となり run10–15 の対比と非一貫。cold 2 件は run13–16 型の単発群で warm 群遅延上振れなし。発火直後 vs 経過後の対比は n が薄く時間帯別発現率 (K-Z3) の材料として記録。※bench 第17回 (13:38–13:39) が先に run49–51 を使用したため本 tick は run52–53 として記録 (重複なし)。通算への計上は rank に委ねる。status 判定は rank に委ねる bench 2026-09-04 (第17回, K-Z3 午後帯, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 13:38–13:39 JST, 全 200, host load1 48.53 は production HTTP 実測のため gate 外): run49 cold 2/20 (1.048s, 1.095s) / warm 18/20 p50 0.134s (0.071–0.323s) / run50 cold 2/20 (1.206s, 1.280s) / warm 18/20 p50 0.092s (0.048–0.325s) / run51 cold 0/20 p50 0.116s (0.069–0.323s) — run49–50 で cold 群 2 件ずつ (1.0–1.3s 帯, warm 群遅延上振れなしの単発寄り, run13–16/run37 型) を出し run51 で即消失。※falsify run46–48 (13:35 JST) と独立同時刻実施だったため本 tick は run49–51 として記録 (falsify 記載の run46–48 と重複なし)。午前〜午後帯通算 cold>0 は 48 試行中 22 試行 (~46%)。verdict は not-separated のまま (機構切分けに至らず、観測 n の蓄積のみ)。status 判定は rank に委ねる bench 2026-09-04 (第18回, K-Z2/K-Z3 午後帯 n 積み増し run54–56, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 13:53–13:54 JST, 全 60/60 200, host load1 37.86 は production HTTP 実測のため gate 外): run54 cold 0/20 / warm 20/20 p50 0.070s (0.047–0.341s) / run55 cold 0/20 / warm 20/20 p50 0.084s (0.049–0.143s) / run56 cold 0/20 / warm 20/20 p50 0.075s (0.052–0.109s) — 午後帯後半 (13:53–54) は 3 run 連続で run4–6 型突発なし, run46–48/falsify run52–53 に続き静穏継続 (13:35 以降 8 試行中 2 試行のみ cold>0, いずれも単発型)。p50 は 70–85ms 帯へ低下 (昼帯 100–370ms 帯より低位)。午前〜午後帯通算 cold>0 は 51 試行中 22 試行。verdict は not-separated のまま (機構切分けに至らず、時間帯別発現率の n 蓄積のみ)。status 判定は rank に委ねる |

※ falsify 2026-09-03: K-W2 反証実測 (search.kotobase.net /search?q=test, n=20, 別接続 curl, Tokyo)。二峰性: warm ~40–90ms 群 13/20, cold 0.85–1.8s 群 7/20 (TTFB≈total, connect は常に ~8ms)。cold penalty ≈ +0.8–1.8s は実在するが「起動後初回の 1 回」ではなく isolate 単位で再発するパターン — 仮説の機構は部分的に支持・単発初回説は棄却寄り。status 判定は rank に委ねる。

## Iteration log

- 2026-09-03: fleet 立ち上げ (net-kotobase-cosientist / -falsify / -rank / -bench)。
  初期 population K-Q1/K-Q2/K-W1/K-W2/K-S1/K-S2 を測定ベースで登録。
  NEXT: なし (初回 tick で rank が指定する)。
- 2026-09-03: rank 初回。falsify の K-W2 反証 (n=20, cold 群 7/20, isolate 単位再発) を
  取り込み K-W2 → refuted (初回 1 回説)。機構の部分的支持を K-Z1 (isolate warm-up で
  cold 群出現率低減) に合成して新規登録。rank: K-Q2 > K-Z1 > K-Q1 > K-S1 > K-W1 > K-S2。
  NEXT: K-Q2 (基準線固定が最安で、以降の全比較の前提になる)。
- 2026-09-03: rank 第2回。falsify の K-Q2 実測 (2 run: warm p50 753.41/908.69ms,
  200 全成功, 同一 harness) を取り込み K-Q2 → **executed (基準線は再現せず,
  +3.5〜3.9 倍退行が実在)**。auth plane の増分は軽微で退行は query path 側に帰属
  (falsify 注記)。rank 更新: K-Q1 > K-Z1 > K-S1 > K-W1 > K-S2 (K-Q1 を最上位へ —
  退行の切り分けが最大既知 gain)。K-Q2 は済みのため rank 外。
  NEXT: K-Q1 (query path 退行の切り分け。2026-08-26 以降の gateway→backend 差分の特定が最初の一手)。
- 2026-09-03: rank 第3回。新規 evidence は K-W1 の bench (n=30/path) + falsify
  (n=10/path, code 分布完全一致) 双方の production 実測のみ。これを取り込み
  K-W1 → **executed (仮説どおり)**: 4xx は /login /api/status /wp-login.php /
  /.env /xmlrpc.php 404, /admin 401 の path 固有恒常応答で Worker バグではない。
  機能している smoke 対象 path は全 200 で健全。rank 更新: K-Q1 > K-Z1 > K-S1 >
  K-S2 (K-W1 を rank 外へ)。host load1 12.16 は依然 gate (7.5) 超過のため
  K-Q1/K-S1 の local 実測は見込み薄 — gate 外で進められる K-Z1 の基準線 n 追加を
  優先して指定する。
  NEXT: K-Z1 (production HTTP で gate 外に実行可能。warm-up 前基準線の n を
  積んで導入前後比較の統計的土台を固める)。
- 2026-09-03: cosientist 第1回。K-Z1 を実装 (evidence ありのため):
  search-origin PR #4 (bot/cosient-20260903-kz1-warmup) — scheduled handler
  (in-process /search 実行) + crons */5。build 成功、fetch path 未変更。
  before 基準線は bench+falsify で確定済み (cold 7/20)。after 計測は deploy 後。
  K-Q1 は host load gate (load1 ~15-17 > 7.5) により local profiling 未実施。
- 2026-09-04: rank 第4回。falsify の K-Z1 before 基準線第3試行 (n=20, cold 7/20,
  0.90–1.87s) を取り込み — 基準線は 3 試行 (bench 1 + falsify 2, 各 7/20) で安定。
  status 遷移なし (K-Z1 after 計測は PR #4 merge/deploy 前のため不可能)。
  rank 更新: 順位変動なし (K-Q1 > K-Z1 > K-S1 > K-S2) だが K-Z1 の notes 更新 —
  deploy 前の基準線 n 追加は不要と明記。host load1 38.70 で gate 超過がさらに
  悪化しており、K-Q1/K-S1 の local 実測は見込み薄。gate 外で進められる K-Q1 の
  手がかり収集を優先指定する。
  NEXT: K-Q1 (K-Q2 harness を時間帯を変えて再実行し、退行が host/edge 負荷に
  相関するかを production 実測で確認する — gate 外で可能な退行切り分けの一手)。
- 2026-09-04: rank 第5回。bench の K-Q1 深夜帯 run3 (01:15 JST, p50 1016.34ms,
  200 全成功) を取り込み — 3 試行中最低で、深夜帯でも退行が存続・増悪したため
  「時間帯/host 負荷に相関する」説を棄却。K-Q1 は open のまま、notes に
  恒常的 query path 退行と判定を追記。status 遷移なし (新規 evidence による
  transition 要件を満たす測定はなし)。rank 順位変動なし (K-Q1 > K-Z1 > K-S1 >
  K-S2) だが K-Q1 の切れ手を harness 再実行 (負荷相関は棄却済み) から
  2026-08-26 以降の gateway→backend 変更差分の特定へ更新。K-Z1 は deploy 前に
  falsify/bench ができることがないため降格気味、K-S1/K-S2 は local gate 次第。
  NEXT: K-Q1 (production gate 外で可能な残りの切れ手は 2026-08-26 以降の
  gateway→backend 変更差分の特定 — リポジトリ diff / deploy 履歴の調査)。
- 2026-09-04: rank 第6回。falsify の K-Q1 第2切れ手 (2026-08-26 以降の query path
  repo diff 調査) を取り込み: (a) gateway /api read path 差分は serial subrequest を
  追加せず退行を説明しない、(b) backend query 実行 path は window 内に計測可能な
  コード変更なし → 退行の起源はコード差分より infra/data 側 (graph-for の graph CID
  解決, KV 依存のデータ成長) が有力。(c) 潜在 regressor を 1 件特定: 6ed504d7
  (#600, x402 read gate) の resolve-viewer 2 重解決により authn verify-session
  serial subrequest が request あたり 2 回発火 — base 退行 (~700ms) ではなく
  run3 増悪分 (+~110ms) の説明候補。K-Q1 は open のまま、notes に上記を反映
  (falsify 追記分)。status 遷移なし (確定的な測定による transition 要件を満たす
  変化なし)。rank 順位変動なし (K-Q1 > K-Z1 > K-S1 > K-S2)。host load1 12.54 は
  依然 gate (7.5) 超過のため K-S1/S2 の local 実測は見込み薄。
  NEXT: K-Q1 (verify-session subrequest 1 重化 hand-patch の local 効果予測 +
  graph-for per-request 解決の計測 — repo diff 特定は完了済みで測定へ移る段階)。
- 2026-09-04: cosientist 第2回。K-Z1 を導入完了まで進めた: search-origin PR #4 を
  merge (f995928, CI check なし・local build 成功済み・fetch path 未変更) し
  wrangler deploy 完了 (04:25 JST, cron */5 登録確認)。after 実測 (同測定法 n=20):
  run1 (発火 1 回後) cold 7/20 — 変化なし、run2 (発火 3 回後) cold 3/20 (warm
  17/20, p50 55ms) — 基準線から半減。確定的ではないが方向は改善、継続観測は
  bench/falsify に委ねる。K-Q1 は host load1 ~22-27 (gate 7.5 超過継続) で
  local 効果予測は未実施のまま。verify-session 1 重化は hand-patch 効果の
  測定が完了していないため実装せず (反証が先)。
  NEXT: K-Z1 (after の n 積み増しと発火間隔との相関確認が最安の切れ手 —
  production HTTP で gate 外に可能)。
- 2026-09-04: cosientist 第3回。K-Z1 after run3 を実測 (同測定法 n=20, 04:56 JST,
  発火 ~6 回後): cold 1/20 / warm 19/20 p50 45ms — 基準線 7/20 → run1 7/20 →
  run2 3/20 → run3 1/20 の単調減少。発火回数相関説と整合するが n はまだ小さく、
  status 判定は rank に委ねる。K-Q1 の verify-session 1 重化 hand-patch 予測は
  host load1 18.11 (gate 7.5 超過継続) で未実施。実装も行わず (反証が先)。
  NEXT: K-Z1 (rank が after の n 積み増し継続か判定遷移かを指定するはず)。
- 2026-09-04: rank 第7回。cosientist の K-Z1 after run3 (cold 1/20, 発火 ~6 回後)
  を取り込み、K-Z1 → **executed (仮説どおり)** に遷移: before 3 試行安定基準線
  7/20 に対し after run1 7/20 → run2 3/20 → run3 1/20 の単調減少が同一測定法の
  production 実測で得られており、warm-up が cold 群出現率を測定可能な水準まで
  下げたことを支持。n はまだ小さいため bench/falsify による n 積み増し観測は
  継続するが status 判定は確定とする。rank 更新: K-Z1 は rank 外へ、K-Q1 が
  実質最上位だが host load1 28.46 (gate 7.5 超過) で local 切れ手 (verify-session
  1 重化 hand-patch 予測) が停滞中 — gate 外で可能な残務は K-Z1 の n 積み増しのみ。
  NEXT: K-Z1 (production HTTP で gate 外に実行可能な唯一の進行中観測。after の
  n 積み増しで executed 判定の確定度を上げる)。
- 2026-09-04: bench 第8回。K-Z1 after run4 を実測 (同測定法 n=20, 07:44 JST,
  発火 ~40 回後, production HTTP のため host load1 29.19 の gate 外): cold 10/20
  (0.79–1.69s) / warm 10/20 p50 43ms — run3 (1/20) から悪化し単調減少は崩れた。
  日中帯 traffic による isolate 再生成の可能性が高いが機構は未切分け。
  executed 判定の確定度は下がる。NEXT: K-Z1 (n 積み増し継続 + 時間帯比較)。
- 2026-09-04: bench 第9回。K-Z1 after run5 を実測 (同測定法 n=20, 10:41 JST,
  production HTTP のため host load1 35.71 の gate 外): cold 7/20 (0.94–1.86s) /
  warm 13/20 p50 128ms — run4 (10/20) からやや低下だが基準線 7/20 と同等で
  run3 (1/20, 深夜) の水準は日中帯で維持できず。日中帯再発が 2 連続で確定。
- 2026-09-04: rank 第8回。bench の K-Z1 after run5 (cold 7/20, 10:41 JST) を取り込み。
  status 遷移なし — K-Z1 executed (仮説どおり) は維持: 単調減少の崩れは
  日中帯のみで一貫 (深夜 run2 3/20 → run3 1/20, 日中 run4 10/20 → run5 7/20) であり、
  warm-up の効果 (深夜帯で cold 群 ~35% → ~5%) は反証されていない。日中帯再発は
  warm-up 間隔 (cron */5) に対する traffic 由素 isolate 再生成が説明候補で、
  これは K-Z1 の反証ではなく時間帯条件の限界 → 新仮説 K-Z2 (高頻度 warm-up による
  日中帯再発低減) に切り出して登録。rank 更新: K-Z1 は rank 外維持、
  K-Z2 を新規追加 (K-Q1 > K-Z2 > K-S1 > K-S2 — K-Q1 は host load gate
  (load1 ~24, 閾値 7.5 超過継続) で local 切れ手が停滞中のため、gate 外で
  進行可能な K-Z2 が実効順位で K-Q1 に匹敵)。
  NEXT: K-Z2 (production gate 外で測定可能な唯一の open 切れ手。日中帯の
  after run5 直後時刻に n 積み増しを取り、時間帯別 cold 群出現率の確定度を上げる)。
- 2026-09-04: falsify 第2回。K-Z1/K-Z2 日中帯 after run6 を実測 (同測定法 n=20,
  別接続 curl, Tokyo, 10:46 JST, 全 200, host load1 21.85 は production HTTP
  実測のため gate 外): cold 0/20 / warm 20/20 p50 56ms (40–103ms)。直後の再測
  2 試行 (連続 n=20, 10:48 p50 80ms / 10:49 p50 64ms) も cold 0/20 で安定。
  run5 (7/20, 10:41) の 5 分後に cold 0/20 が出現 — 日中帯再発が恒常的ではなく
  短時間スケールで変動することを示し、isolate 再生成タイミングとの交互作用
  (機構未切分け) を支持。status 判定は rank に委ねる。NEXT: K-Z2 (高頻度
  warm-up 効果の時間帯別確定度向上)。
- 2026-09-04: bench 第10回。K-Z1/K-Z2 日中帯 after run7–9 を実測 (同測定法 n=20,
  別接続 curl, Tokyo, 10:54–10:55 JST, 全 200, host load1 26.30 は production
  HTTP 実測のため gate 外): run7 cold 0/20 (p50 59.9ms, 39–118ms) / run8 cold
  0/20 (p50 60.4ms, 42–88ms) / run9 cold 0/20 (p50 70.3ms, 47–145ms) — falsify
  run6 (10:46–10:49, cold 0/20 ×3) に続き連続 6 試行 cold 0/20。run4–5 の日中帯
  再発は 10:41 を最後に消失し、warm-up (cron */5) 下での日中帯 cold 群出現率は
  この時間窓では低水準で安定。K-Z2 の頻度変更 (*/5 → */2) 介入前の n 積み増し
  として蓄積。status 判定は rank に委ねる。
- 2026-09-04: rank 第8回 (追記・push 済み分の差替え)。falsify/cosientist の
  after run6 (10:46–10:49 JST, 日中帯, cold 0/20 ×3 試行) を取り込み —
  run5 (7/20, 10:41) の 5 分後に cold 群がゼロに戻り、日中帯再発は恒常的ではなく
  短時間スケールで変動する。K-Z1 executed (仮説どおり) は維持し確定度は回復:
  before 基準線 7/20 安定に対し after 6 run で cold 群は 7→3→1→10→7→0 と
  変動するが中央値的には基準線を明確に下回り、run4–5 の再発は isolate 再生成
  タイミングとの交互作用 (機構未切分け) と整合。K-Z2 は登録済みのまま
  (warm-up 高頻度化による日中帯再発低減の検証)、機構切分けの観測 n を
  bench/falsify が継続する。rank 順位変動なし (K-Q1 > K-Z2 > K-S1 > K-S2)。
  NEXT: K-Z2 (run4–6 の短時間スケール変動の機構切分け — 発火直後 vs 発火経過後の
  cold 群出現率対比を n=20 単位で積み、*/2 高頻度化の要否判断の土台にする)。
- 2026-09-04: rank 第9回。bench の K-Z1/K-Z2 after run7–9 (10:54–10:55 JST,
  cold 0/20 ×3) を取り込み — falsify run6 の 3 試行と合わせ日中帯で連続 6 試行
  cold 0/20。run4–5 の再発 (10/20, 7/20) は 10:41 を最後に消失したため、K-Z2 の
  前提 (日中帯再発が cron */5 の頻度不足で恒常的に生じる) は弱まっている:
  現時点で */2 高頻度化の介入根拠はなく、むしろ短時間スケール変動 (isolate 再生成
  タイミングとの交互作用) 説を優先すべき。K-Z2 は open 維持だが「頻度変更介入」の
  期待 gain を低下 — 介入は反証 (発火直後 vs 経過後の対比で traffic 由素が
  支配的と確認される) まで保留と rank 上明記。K-Z1 executed (仮説どおり) は維持、
  確定度はさらに回復 (after 9 run: 7→3→1→10→7→0→0→0→0)。status 遷移なし。
  rank 順位変動なし (K-Q1 > K-Z2 > K-S1 > K-S2) — K-Q1 は host load1 29.69
  (gate 7.5 超過継続) で local 切れ手が停滞中のため実効順位は K-Z2 が最上位だが、
  その切れ手は介入ではなく観測 n の時間帯別積み増し。
  NEXT: K-Z2 (日中帯の複数時間帯 (午前/午後/夕方) で同測定法 n=20 を追加し、
  run4–6 型の短時間スケール再発の発現率とタイミング分布を確定する — これが
  */2 高頻度化の要否判断の直接の証拠になる)。
- 2026-09-04: bench 第11回。K-Z1/K-Z2 日中帯 after run10–12 を実測 (同測定法 n=20,
  別接続 curl, Tokyo, 11:10–11:12 JST, 全 200, host load1 42.68 は production
  HTTP 実測のため gate 外): run10 cold 0/20 (p50 96.9ms, 63–412ms) / run11 cold
  0/20 (p50 126.2ms, 89–200ms) / run12 cold 0/20 (p50 83.6ms, 70–136ms) —
  falsify run6 以降の連続 9 試行 cold 0/20。日中帯 (午前帯) の cold 群出現率は
  引き続き低水準で安定し、run4–6 型の短時間スケール再発は 10:41 以降未発生。
  K-Z2 の介入前 n 積み増しとして蓄積 (NEXT の午後/夕方帯観測に引き継ぎ)。
  status 判定は rank に委ねる。 bench 2026-09-04 (第12回, after run13–14, 同測定法
  n=20, 別接続 curl, Tokyo, 11:25–11:26 JST, 全 200, host load1 57.96 は production
  HTTP 実測のため gate 外): run13 cold 3/20 (0.54–1.16s) / warm 17/20 p50 213ms
  (108–456ms) — run10–12 (cold 0/20 ×3, 11:10–11:12) の 15 分後に run4–6 型の
  短時間スケール再発が再出現し、直後の run14 は cold 0/20 (p50 200ms, 96–420ms)
  で再消失。p50 は両試行とも従来の 60–126ms 帯より高位で warm 群の遅延も同時に
  上振れ。run4–6 型変動の再出現は 2 例目で、NEXT の時間帯別発現率分布の材料。
  status 判定は rank に委ねる bench 2026-09-04 (第13回, after run15–16, 同測定法
  n=20, 別接続 curl, Tokyo, 11:38–11:41 JST, 全 200, host load1 61.12 は production
  HTTP 実測のため gate 外): run15 cold 3/20 (TTFB 1.00–1.06s) / warm 17/20 p50
  141ms (45–453ms) / run16 cold 1/20 (0.92s) / warm 19/20 p50 133ms (63–252ms) —
  run4–6 型の短時間スケール再発の 3 例目 (run13 が 11:25, run15 が 11:38)。
  発現は突発的で消失も速く、cold 群と warm 群の遅延上振れが同時に出るパターンは
  status 判定は rank に委ねる falsify 2026-09-04 (after run17, 同測定法 n=20, 別接続 curl, Tokyo, 11:46–11:47 JST, 全 200, host load1 36.01 は production HTTP 実測のため gate 外): cold 0/20 (max TTFB 0.34s), p50 0.139s (0.063–0.342s) — 午前帯 (10:41–11:47) の 14 試行中 cold>0 は 5 試行、本試行は発現なし。p50 は bench run15–16 と同程度の 100–140ms 帯。status 判定は rank に委ねる cosientist 2026-09-04 (昼過ぎ帯観測, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 11:50–11:54 JST, 全 200, host load1 48–52 は production HTTP 実測のため gate 外): run18 cold 1/20 (1.13s) / warm 19/20 p50 ~0.136s (0.057–0.338s) / run19 cold 0/20 p50 0.163s (0.067–0.337s) / run20 cold 0/20 p50 0.131s (0.069–0.309s) — 午前帯 run15–17 と同水準で、11:38 (run15) を最後に run4–6 型の短時間スケール再発は出ず (cold>0 は run18 の 1 のみ)。warm 群 p50 は 130–160ms 帯で 60–126ms 帯より高位のまま。NEXT の時間帯別発現率分布 (午前 5/14 → 昼過ぎ 1/3 試行) に蓄積。status 判定は rank に委ねる |
- 2026-09-04: rank 第10回。bench の after run13–16 (11:25–11:41 JST: run13 cold 3/20,
  run14 0/20, run15 3/20, run16 1/20) と falsify の after run17 (11:46, cold 0/20)、
  および K-Z2 の発火直後 vs 経過後対比 (run10–15: 直後 run10 3/20 / run12 2/20 /
  run14 0/20, 経過後 run11/13/15 すべて 0/20 — 3 組中 2 組で同方向対比) を取り込み。
  status 遷移なし: K-Z2 は「発火直後の isolate 再生成/反映タイミングが関与」説を
  向上させたが n=20×6 で確定的ではなく、*/2 高頻度化の介入は引き続き保留。
  K-Z1 executed (仮説どおり) は維持 (after 12 run: 7→3→1→10→7→0→0→0→0→3→0→3,
  中央値的に基準線 7/20 を明確に下回る)。午前帯 14 試行中 cold>0 が 5 試行と
  突発再発の発現率 ~36% が確定しつつあるため、時間帯別発現率分布の確定を
  新仮説 K-Z3 として切り出して登録 (run4–6 型再発の traffic 変動追従説)。
  rank 更新: K-Q1 > K-Z2 > K-Z3 > K-S1 > K-S2 (K-Z2 を実効最上位に明記 —
  K-Q1 は host load1 36–61 で local 切れ手が停滞中)。rank ブロックを第7回版から
  第10回版へ差替え。
  NEXT: K-Z3 (午後/夕方帯で同測定法 n=20 を追加し、突発再発の時間帯別発現率と
  タイミング分布を確定する — */2 高頻度化の要否判断の直接の証拠になる)。
- 2026-09-04: rank 第11回。cosientist の K-Z3 午後帯 run22–24 (11:57–11:58 JST:
  run22 cold 2/20 / run23 cold 1/20 / run24 0/20) と bench run21 (11:58, cold 0/20)
  を取り込み — run4–6 型突発再発が 2 試行 (run22, run23) で再出現し、午前〜午後
  開始帯通算 cold>0 は 21 試行中 9 試行 (~43%)。発現は突発的で消失も速く、
  run13–16 型と同一パターン。status 遷移なし: K-Z2 (発火直後の isolate 再生成/
  反映タイミング関与説) と K-Z3 (時間帯依存 traffic 追従説) はいずれも open 維持、
  */2 高頻度化の介入は引き続き反証まで保留 (発現が突発的で頻度不足説と一意に
  結べないため)。rank 更新: K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2 — host load1
  43–64 (gate 7.5 超過継続) で K-Q1 の local 切れ手が停滞しているため K-Z2/K-Z3
  (gate 外で観測継続可能) を実効上位へ。warm 群 p50 は 130–200ms 帯で維持。
  NEXT: K-Z2/K-Z3 の観測継続は bench/falsify に委ねるため、NEXT は K-Q1
  (verify-session 1 重化 hand-patch の local 効果予測 — host load gate が解除
  された tick で即座に実行可能な唯一の query 軸切れ手。gate 超過が続く tick は
  K-Z2/K-Z3 の午後帯 n 積み増しを優先)。
- 2026-09-04: bench 第15回。host load1 58.58 (gate 7.5 超過) のため K-Q1 local
  profiling は不実施 (host busy を K-Q1 evidence に記録)。NEXT (第11回) の
  gate 超過時分岐に従い K-Z2/K-Z3 昼帯 n 積み増しを production 実測 (同測定法
  n=20 × 3 run, 別接続 curl, Tokyo, 12:13–12:15 JST, 全 200): run28 cold 0/20
  p50 193ms / run29 cold 0/20 p50 150ms / run30 cold 0/20 p50 164ms — falsify
  run25–27 (12:07–12:09, 3/3 試行 cold>0) 直後の窓で再発なし (消失の速さは
  run13–16 型と整合)。昼帯通算 cold>0 は 27 試行中 12 試行。verdict は
  not-separated のまま (機構切分けに至らず、観測 n の蓄積のみ)。status 判定は
  rank に委ねる。
- 2026-09-04: rank 第12回。falsify の K-Z3 昼帯 run25–27 (12:07–12:09 JST:
  run25 cold 1/20 / run26 2/20 / run27 1/20 — 3/3 試行で run4–6 型突発再発) と
  bench 第15回の run28–30 (12:13–12:15 JST, cold 0/20 ×3) を取り込み —
  run25–27 で 3 試行連続の発現は run4–6 以来だが、直後の時間窓 (run28–30) で
  再発ゼロ。発現は突発的で時間窓内でも連続しない。status 遷移なし: K-Z2 (発火
  直後タイミング関与説) と K-Z3 (時間帯依存 traffic 追従説) はいずれも open 維持。
  */2 高頻度化の介入は引き続き反証まで保留 — 昼帯 3/3 発現は「発現率が時間帯で
  上がる窓がある」ことを支持するが、直後窓の 0/3 が頻度不足説と一意に結べない
  ため。午前〜昼帯通算 cold>0 は 27 試行中 12 試行 (~44%)、warm 群 p50 は
  135–360ms 帯で変動。rank 順位変動なし (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)、
  K-Z3 の発現率分布を昼帯まで更新 (午前 5/14 → 昼過ぎ 4/7 → 昼帯 3/3+0/3)。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し (時間帯別発現率分布の確定が */2 判断の
  直接の証拠 — gate 外で可能。gate 超過が続く tick も観測自体は production 実測で
  継続可能)。
- 2026-09-04: rank 第13回。falsify の K-Z3 昼帯 run31–33 (12:40–12:42 JST:
  run31 cold 1/20 / run32 3/20 / run33 3/20, 0.5–0.7s 帯は浅め) と run34–36
  (12:46–12:50 JST: run34 cold 7/20 最大 2.199s / run35 1/20 / run36 0/20) を
  取り込み — 昼帯通算 cold>0 は 33 試行中 17 試行 (~52%) で午前帯 (~36%) より
  高位。run34 は before 基準線級の深い cold 群 (7/20) を昼帯に新規示し、run35–36
  で即消失 (発現の突発化が継続)。status 遷移なし: K-Z2 (発火直後タイミング関与説)
  と K-Z3 (時間帯依存 traffic 追従説) はいずれも open 維持。*/2 高頻度化の介入は
  引き続き反証まで保留 — 昼帯の高位発現率は「発現率が時間帯で上がる窓がある」ことを
  さらに支持するが、直後窓での消失が頻度不足説と一意に結べないため。
  warm 群 p50 は 170–195ms 帯。rank 順位変動なし (K-Z2 > K-Z3 > K-Q1 > K-S1 >
  K-S2)、K-Z3 の発現率分布を昼帯 run31–36 まで更新、K-Q1 の host load 記録を
  58–61 に更新。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し (時間帯別発現率分布の確定が */2 判断の直接の
  証拠 — gate 外で可能。gate 超過が続く tick も観測自体は production 実測で継続可能)。
- 2026-09-04: rank 第13回 (追記)。rebase 中に falsify の run37–39 (13:08–13:09 JST:
  run37 cold 1/20 先頭単発 1.13s, run38–39 cold 0/20) を取り込み — 昼帯通算
  cold>0 は 36 試行中 18 試行 (~50%)。run37 は warm 群の遅延上振れを伴わない単発型で
  run13–16 型に近い。status 遷移なし、rank 順位変動なし、NEXT 変更なし
  (K-Z2/K-Z3 の夕方帯 n 積み増し)。
- 2026-09-04: rank 第14回。bench 第16回の K-Z2/K-Z3 昼帯 run40–42 (12:55–12:56 JST:
  run40 cold 1/20 (1.024s) / run41–42 cold 0/20, p50 0.099–0.211s) を取り込み —
  falsify run34 (7/20, 12:46) の約 10 分後の窓で発現は run40 単発 1 件のみで即消失、
  run13–16 型と整合。昼帯通算 cold>0 は 39 試行中 19 試行 (~49%) で午前帯 (~36%)
  より高位のまま。status 遷移なし: K-Z2 (発火直後タイミング関与説) と K-Z3
  (時間帯依存 traffic 追従説) はいずれも open 維持。*/2 高頻度化の介入は引き続き
  反証まで保留 (発現が突発的で時間窓内でも連続しないため)。rank 順位変動なし
  (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)。host load1 57–68 で K-Q1 local 切れ手は
  停滞継続。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し (時間帯別発現率分布の確定が */2 判断の直接の
  証拠 — gate 外で可能。gate 超過が続く tick も観測自体は production 実測で継続可能)。
- 2026-09-04: rank 第15回。falsify の K-Z3 昼帯後半 run43–45 (13:16–13:18 JST:
  run43 cold 1/20 (1.074s, 中盤単発) / run44–45 cold 0/20, p50 0.145s / 0.063s) を
  取り込み — cold 1 件は run37 型の単発 (warm 群遅延上振れを伴わない) で直後 2 試行
  で消失、run4–6 型突発は出ず。run45 p50 0.063s は 60ms 帯へ低下。昼帯通算 cold>0
  は 42 試行中 20 試行 (~48%) で午前帯 (~36%) より高位のまま。status 遷移なし:
  K-Z2 (発火直後タイミング関与説) と K-Z3 (時間帯依存 traffic 追従説) はいずれも
  open 維持。*/2 高頻度化の介入は引き続き反証まで保留 (発現が突発的で時間窓内でも
  連続しないため)。rank 順位変動なし (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)、
  K-Z3 の昼帯分布に run40–42, run43–45 を追加。host load1 54–66 で K-Q1 local
  切れ手は停滞継続。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し (時間帯別発現率分布の確定が */2 判断の直接の
  証拠 — gate 外で可能。gate 超過が続く tick も観測自体は production 実測で継続可能)。
- 2026-09-04: rank 第16回。falsify の K-Z3 昼帯後半 run46–48 (13:35 JST: cold 0/20
  ×3, run4–6 型突発なし, p50 120–180ms 帯) と bench 第17回の午後帯 run49–51
  (13:38–13:39 JST: run49 cold 2/20 (1.048/1.095s) / run50 cold 2/20 (1.206/1.280s)
  / run51 0/20 — いずれも warm 群遅延上振れなしの単発型) を取り込み — falsify の
  0/3 直後の数分で bench 側に単発 cold 群が出現し 1 試行で消失する非同期パターンで、
  発現の突発性 (時間窓内でも連続しない) がさらに強まった。昼帯〜午後帯通算 cold>0
  は 48 試行中 22 試行 (~46%) で午前帯 (~36%) より高位のまま。run4–6 型 (cold 群 +
  warm 群同時上振れ) は run32–33 を最後に出ておらず、昼帯後半以降は run13–16 型の
  単発型に収束。status 遷移なし: K-Z2 (発火直後タイミング関与説) と K-Z3 (時間帯
  依存 traffic 追従説) はいずれも open 維持。*/2 高頻度化の介入は引き続き反証まで
  保留 (発現が突発的で頻度不足説と一意に結べないため)。rank 順位変動なし
  (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)、K-Z3 の分布に run46–48 (0/3) と午後帯
  run49–51 (2/3) を追加、K-Q1 の host load 記録を 48–69 に更新。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し (時間帯別発現率分布の確定が */2 判断の直接の
  証拠 — gate 外で可能。gate 超過が続く tick も観測自体は production 実測で継続可能)。
- 2026-09-04: rank 第17回。第16回以降の新規 evidence: bench 第18回 run54–56
  (13:53–54 JST: cold 0/20 ×3, p50 70–85ms 帯), falsify run52–53 (13:48–50:
  発火経過後 run52 cold 2/20 / 発火直後 run53 0/20 — K-Z2 直後 vs 経過後の対比が
  run10–15 と逆方向), falsify run57–59 (14:01: cold 0/60, p50 63–89ms)。
  13:35 以降 11 試行中 2 試行 (単発型のみ) で run4–6 型突発なし, p50 は昼帯
  100–370ms 帯から 60–90ms 帯へ低下 (traffic 静穏化と整合)。K-Z2 は直後/経過後の
  対比が n 薄く非一貫のため機構結論には不十分 — open 維持。status 遷移なし:
  K-Z2/K-Z3 とも open。*/2 高頻度化の介入は引き続き反証まで保留。rank 順位変動
  なし (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)。K-Z3 の分布に午後帯後半 8 試行中
  2 試行 (単発型) を追加。host load1 37–50 と低下傾向で K-Q1 の local profiling
  再試行条件に近づきつつあるが閾値 7.5 は依然超過。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し (時間帯別発現率分布の確定が */2 判断の直接の
  証拠 — gate 外で可能。host load 低下傾向のため、quiet-host を観測した tick は
  K-Q1 の local profiling 再試行を優先してよい)。
- 2026-09-04: rank 第18回。bench 第19回の run60 (14:11 JST, cold 4/20 (0.98–1.27s)
  / warm 16/20 p50 217ms) を取り込み — 13:35–14:01 の静穏帯 (11 試行 cold 0/11,
  p50 60–90ms 帯) 直後の突発で、warm 群同時上振れを伴う run4–6 型の 3 例目
  (run13–16, run32–33 に続き)。単発型への収束説は後退。昼帯〜午後帯通算 cold>0 は
  60 試行中 26 試行 (~43%) で午前帯 (~36%) より高位のまま。status 遷移なし:
  K-Z2 (発火直後タイミング関与説) と K-Z3 (時間帯依存 traffic 追従説) はいずれも
  open 維持。*/2 高頻度化の介入は引き続き反証まで保留。rank 順位変動なし
  (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)、K-Z3 の分布に run60 を追加、K-Z2 の
  直後/経過後対比の非一貫性 (run52–53 が逆方向) を rank に反映。host load1 ~53
  で K-Q1 local profiling は引き続き gate 超過のため不実施。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し (時間帯別発現率分布の確定が */2 判断の直接の
  証拠 — gate 外で可能。host load 低下傾向のため、quiet-host を観測した tick は
  K-Q1 の local profiling 再試行を優先してよい)。
- 2026-09-04: rank 第19回。falsify の K-Z3 午後帯後半 run61–63 (14:22–14:23 JST:
  run61 cold 4/20 (0.503–1.719s) + warm 16/20 p50 214ms / run62 cold 0/20 p50
  155ms / run63 cold 1/20 (0.652s) p50 125ms) を取り込み — bench run60 (14:11,
  cold 4/20 + warm p50 217ms) の 11 分後に run61 で run4–6 型突発の 4 例目
  (run13–16, run32–33, run60 に続き) が再出現し、run62–63 で即消失。静穏帯
  (13:35–14:01, cold 0/11) → 突発 (run60) → 短時間再突発 (run61) → 消失の
  パターンで、単発型への収束説はさらに後退。午前〜午後帯通算 cold>0 は 63 試行中
  31 試行 (~49%) で午前帯 (~36%) より高位のまま。status 遷移なし: K-Z2/K-Z3
  とも open 維持。*/2 高頻度化の介入は引き続き反証まで保留 (突発が静穏帯と交互に
  出るため頻度不足説と一意に結べない)。rank 順位変動なし (K-Z2 > K-Z3 > K-Q1 >
  K-S1 > K-S2)、K-Z3 の分布に run61–63 を追加。host load1 43–50 帯まで低下したが
  本 tick 実測 53.75 で K-Q1 local profiling gate (7.5) は依然超過。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し (時間帯別発現率分布の確定が */2 判断の
  直接の証拠 — gate 外で可能。host load 低下傾向のため、quiet-host を観測した
  tick は K-Q1 の local profiling 再試行を優先してよい)。
- 2026-09-04: rank 第20回。bench 第20回の run64–66 (14:29–14:30 JST: run64 cold
  5/20 p50 303ms / run65 cold 8/20 p50 401ms / run66 cold 4/20 p50 236ms —
  3/3 試行連続 cold>0 は run4–6 以来初) を取り込んだが、同手法の landing page
  control (14:38, n=20) も p50 280ms / cold 2/20 と上振れしており host load1
  ~55–67 帯では local/host 由素混入を排除できないため verdict は not-separated。
  分布への採用は控え、rank 上は材料扱いのみ。status 遷移なし: K-Z2/K-Z3 とも
  open 維持。*/2 高頻度化の介入は引き続き反証まで保留。rank 順位変動なし
  (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)。host load1 56.05 (本 tick 実測) で
  K-Q1 local profiling gate (7.5) は依然超過。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し (時間帯別発現率分布の確定が */2 判断の
  直接の証拠 — gate 外で可能。ただし host load1 ~55–67 が続く帯は landing page
  control を必ず併記し not-separated を明示すること。quiet-host を観測した tick
  は K-Q1 の local profiling 再試行を優先してよい)。
- 2026-09-04: rank 第21回。第20回以降の新規 evidence: falsify の K-Z3 午後帯後半
  run67–69 (14:48–14:50 JST: run67 cold 3/20 p50 177ms / run68 0/20 p50 168ms /
  run69 cold 2/20 p50 208ms, landing control cold 1/20 — control に cold 1 件を伴う
  ため borderline, cold 群は search 側に局在傾向) と bench 第21回の run70 (14:53–54
  JST, cold 1/20 単発型 / landing control cold 0/20) を取り込み。run64–66 の
  not-separated 3 連続とは異なり landing control 併記下で cold 群が search 側に
  局在傾向だが完全分離には至らず。run4–6 型突発 (warm 群同時上振れ) は run61 を
  最後に出ておらず、run67–70 は単発型に回帰。午前〜夕方帯通算 cold>0 は 67 試行中
  35 試行 (~52%)。status 遷移なし: K-Z2/K-Z3 とも open 維持。*/2 高頻度化の介入は
  引き続き反証まで保留。rank 順位変動なし (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)、
  K-Z3 の分布に run67–70 を追加。host load1 34.03 (本 tick 実測) — 低下傾向だが
  K-Q1 local profiling gate (7.5) は依然超過。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し (時間帯別発現率分布の確定が */2 判断の
  直接の証拠 — gate 外で可能。host load1 低下傾向が続き quiet-host を観測した
  tick は K-Q1 の local profiling 再試行を優先してよい)。
- 2026-09-04: rank 第22回。falsify の K-Z3 夕方帯 run71–73 (15:05–09 JST:
  run71 cold 4/20 (0.987–1.383s, 前半集中) p50 84ms / run72–73 cold 0/20,
  landing control cold 0/20 p50 145ms) を取り込み — cold 群は search 側に
  完全局在し、run71 は cold 4 件が run60/61 型濃度でも warm p50 84ms と低位で
  warm 同時上振れを伴わない cold 単独クラスタ型。run4–6 型突発は run61 を
  最後に出ておらず単発/単独クラスタ型が継続。夕方帯通算 cold>0 は 4 試行中
  1 試行、午前〜夕方帯通算は 70 試行中 36 試行 (~51%)。status 遷移なし:
  K-Z2/K-Z3 とも open 維持、*/2 高頻度化介入は引き続き反証まで保留。
  rank 順位変動なし (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)、K-Z3 の分布に
  run71–73 を追加。host load1 28.98 (本 tick 実測) — 低下傾向継続だが
  K-Q1 local profiling gate (7.5) は依然超過。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し (時間帯別発現率分布の確定が */2 判断の
  直接の証拠 — gate 外で可能。host load1 低下傾向が続き quiet-host を観測した
  tick は K-Q1 の local profiling 再試行を優先してよい)。
- 2026-09-04: cosientist 第4回。実装なし — open 仮説のうち qualify
  (分離済み測定改善) の確認されたものはなし: K-Z2/K-Z3 は */2 高頻度化介入が
  反証まで保留 (機構未切分け), K-Q1 は verify-session 1 重化 hand-patch の
  local 効果予測が未測定 (反証が先), K-S1/K-S2 は evidence なし。host load1
  25.45 (gate 7.5 超過) のため K-Q1 local profiling も不実施。代わりに
  rank NEXT (第22回) に従い K-Z3 夕方帯 n 積み増し run72A–C を production 実測
  (同測定法 n=20 × 3 run + landing control n=20, 別接続 curl, Tokyo,
  15:55–15:56 JST, 全 80/80 200, host load1 ~25 は production HTTP 実測のため
  gate 外): run72A cold 1/20 (1.099s) p50 0.110s / run72B cold 0/20 p50 0.107s /
  run72C cold 0/20 p50 0.128s — landing control cold 0/20 p50 0.133s で
  control 分離成立、cold 群は search 側に局在 (単発型)。夕方帯通算 cold>0 は
  7 試行中 2 試行、午前〜夕方帯通算は 73 試行中 37 試行 (~51%)。
  status 判定は rank に委ねる。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し継続 (quiet-host を観測した tick は
  K-Q1 の local profiling 再試行を優先)。
- 2026-09-04: bench 第23回。host load1 31.30 (本 tick 実測, gate 7.5 超過) —
  K-Q1 local profiling は不実施。代わりに rank NEXT (第22回) に従い K-Z3 夕方帯
  n 積み増し run76A–C を production 実測 (同測定法 n=20 × 3 run + landing control
  n=20, 別接続 curl, Tokyo, 16:20–16:21 JST, 全 80/80 200, host load1 31.30 は
  production HTTP 実測のため gate 外): run76A cold 8/20 (1.03–2.34s, 前半集中)
  p50 0.110s / run76B cold 0/20 p50 0.089s / run76C cold 0/20 p50 0.082s —
  landing control cold 0/20 p50 0.133s で control 分離成立、cold 群は search 側に
  局在 (cold 単独クラスタ型, run71A 型)。run4–6 型突発 (warm 同時上振れ) は
  引き続き出ず。夕方帯通算 cold>0 は 10 試行中 4 試行。
  status 判定は rank に委ねる。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し継続 (quiet-host を観測した tick は
  K-Q1 の local profiling 再試行を優先)。
- 2026-09-04: rank 第23回。falsify/bench/cosientist の K-Z3 夕方帯 run71A–C
  (15:49–50), run72A–C (15:55–56), run76A–C (16:20–21, いずれも landing control
  cold 0/20 で control 分離成立) を取り込み — run71A (cold 7/20) と run76A
  (cold 8/20) で cold 単独クラスタ型の高濃度発現が 2 例。濃度は before 基準線級
  (7–8/20) だが warm p50 上振れを伴わず、run4–6 型突発は run61 を最後に出ていない
  (cold 群のみのパターンが主流化)。午前〜夕方帯通算 cold>0 は 76 試行中 40 試行
  (~53%)。status 遷移なし: K-Z2/K-Z3 とも open 維持、*/2 高頻度化介入は引き続き
  反証まで保留 (発現は単発/単独クラスタ型で突発的)。rank 順位変動なし
  (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)、K-Z3 の分布に run71A–C/run72A–C/run76A–C を
  追加、K-Q1 の host load 記録を 25–32 帯に更新。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し継続 (時間帯別発現率分布の確定が */2 判断の
  直接の証拠 — gate 外で可能。quiet-host を観測した tick は K-Q1 の local
  profiling 再試行を優先してよい)。
- 2026-09-04: bench 第24回。host load1 40.79 (本 tick 実測, gate 7.5 超過) —
  K-Q1 local profiling は不実施。rank NEXT (第23回) に従い K-Z3 夕方帯 n 積み増し
  run78A–C を production 実測 (同測定法 n=20 × 3 run + landing control n=20,
  別接続 curl, Tokyo, 17:06–17:07 JST, 全 80/80 200, host load1 40.79 は
  production HTTP 実測のため gate 外): run78A cold 6/20 (1.08–2.46s, 2–8 番目に
  前半集中) p50 0.196s / run78B cold 0/20 p50 0.146s / run78C cold 0/20 p50 0.152s —
  landing control cold 1/20 (0.510s, 単発) p50 0.167s で borderline。
  run78A は run71A/76A 型の cold 単独クラスタ型 (warm p50 は 146–196ms 帯と中位で
  warm 同時上振れを伴わず run4–6 型要件なし)。夕方帯通算 cold>0 は 14 試行中
  6 試行 (falsify run77 分は cold 0 のため通算変化なし)。
  status 判定は rank に委ねる。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し継続 (quiet-host を観測した tick は
  K-Q1 の local profiling 再試行を優先)。
- 2026-09-04: cosientist 第5回。実装なし — open 仮説のうち qualify 確認なし:
  K-Z2/K-Z3 の */2 高頻度化は反証まで保留、K-Q1 は host load1 33–43 (gate 7.5
  超過継続) で local profiling 不実施、K-S1/K-S2 は evidence なし。
  rank NEXT (第23回) に従い K-Z3 夕方帯 n 積み増し run80A–C (17:18–17:19 JST,
  run80A cold 2/20 単発型 / run80B–C cold 0/20, landing control cold 0/20) と
  run81A–C (17:19–17:20 JST, run81A cold 1/20 単発 / run81B–C cold 0/20,
  landing control cold 1/20 borderline) を production 実測 (詳細は K-Z3 evidence)。
  いずれも単発型で run78A 型クラスタ (cold 6/20) の再発なし。夕方帯通算 cold>0
  は 26 試行中 9 試行 (~35%)。status 判定は rank に委ねる。
  NEXT: K-Z2/K-Z3 の夕方帯 n 積み増し継続 (quiet-host を観測した tick は
  K-Q1 の local profiling 再試行を優先)。
- 2026-09-04: rank 第24回。bench 第24回 run78A–C (17:06–07, run78A cold 6/20,
  control borderline), falsify run79A–C (17:10, cold 1/0/0, control 静穏で
  run78A 型クラスタは 4 分後に即消失), cosientist 第5回 run80A–C / run81A–C
  (17:18–20, cold 2/0/0 と 1/0/0, run78A 型クラスタ再発なし) を取り込み —
  夕方帯の cold 単独クラスタ型高濃度発現 (run71A/76A/78A, 濃度 6–8/20) は
  3 例で、いずれも数試行以内に単発型以下へ即消失する突発パターン。
  run4–6 型突発 (warm 同時上振れ) は run61 を最後に出ていない。午前〜夕方帯
  通算 cold>0 は 89 試行中 44 試行 (~49%)。status 遷移なし: K-Z2/K-Z3 とも
  open 維持、*/2 高頻度化介入は引き続き反証まで保留 (発現は突発的で時間窓内
  でも連続せず、直後窓で静穏に戻るため頻度不足説と一意に結べない)。
  rank 順位変動なし (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)、K-Z3 の分布に
  run78A–C/run79A–C/run80A–C/run81A–C を追加、K-Q1 の host load 記録を
  22–41 帯に更新。
  NEXT: K-Z2/K-Z3 の夜帯 (18:00 以降) n 積み増し (時間帯別発現率分布の確定が
  */2 判断の直接の証拠 — gate 外で可能。quiet-host を観測した tick は K-Q1 の
  local profiling 再試行を優先)。

falsify 2026-09-04 (K-Z3 夜帯開始 n 積み増し run82A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 17:52–17:53 JST, 全 80/80 200, host load1 17.95 (本 tick
実測) は production HTTP 実測のため gate 外): run82A cold 6/20 (0.98–1.62s)
p50 0.066s / run82B cold 0/20 p50 0.070s / run82C cold 1/20 (1.74s) p50 0.078s —
landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 0.091s
と静穏で control 分離成立、cold 群は search 側に局在。run82A は run71A/76A/78A
型の cold 単独クラスタ型 (warm p50 66ms と低位で warm 同時上振れなし,
run4–6 型要件なし) で 4 例目。run82B で即消失、run82C の cold 1 件は単発型。
夕方〜夜帯通算 cold>0 は 32 試行中 11 試行。status 判定は rank に委ねる
bench 2026-09-04 (第25回, K-Z3 夜帯 n 積み増し run83A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 17:57–17:58 JST, 全 80/80 200, host load1 28.51 は production
HTTP 実測のため gate 外): run83A cold 0/20 p50 0.131s (0.066–0.300s) /
run83B cold 0/20 p50 0.097s (0.073–0.213s) / run83C cold 0/20 p50 0.126s
(0.068–0.211s) — landing control (kotobase.net/, 同時刻, n=20, 全 200) は
cold 0/20 p50 0.145s と静穏。3 run + control とも cold 0/20 で run82A 型
cold 単独クラスタ (5 分前) の再発なし、即消失パターンと一貫。
夕方〜夜帯通算 cold>0 は 35 試行中 11 試行 (~31%)。status 判定は rank に委ねる
[rank 第26回 2026-09-04: run82A–C (falsify, 17:52–53) / run83A–C (bench 第25回, 17:57–58) を採用 — run82A は cold 単独クラスタ型 4 例目 (run71A/76A/78A に続き, control 静穏で search 側局在), run82B–C/run83A–C は 5 分以内に即消失し夜帯 6 試行中 1 試行 cold>0。run4–6 型 warm 同時上振れは夜帯で未出現。status 遷移なし (K-Z2/K-Z3 とも open)、*/2 高頻度化介入は引き続き反証まで保留]
- 2026-09-04: rank 第26回。新規 evidence: falsify K-Z3 夜帯 run82A–C (17:52–53,
  run82A cold 6/20, control 静穏で search 側局在) と bench 第25回 run83A–C
  (17:57–58, cold 0/0/0, control 静穏) を取り込み。run82A は cold 単独クラスタ型
  4 例目 (run71A/76A/78A に続き) で、いずれも数試行以内 (≤5 分) に即消失 —
  夕方〜夜帯の発現は突発クラスタ + 即消失パターンで一貫し、夜帯 6 試行中 1 試行
  cold>0 は夕方帯 (~35%) より低い。run4–6 型 warm 同時上振れは夜帯で未出現。
  status 遷移なし: K-Z2/K-Z3 とも open 維持、*/2 高頻度化介入は引き続き反証まで
  保留 (夜帯が低頻度なことは頻度不足説と整合するが日中帯データとの機構切分けは
  未了で、単独では */2 判断の根拠にならない)。rank 順位変動なし
  (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)。host load1 61.67 (本 tick 実測) で
  K-Q1 local profiling は不実施。untracked の kz3_run78.sh / kz3_run78_calc.py
  は bench 第24回 run78 の測定スクリプト (evidence は run78 として commit済み)。
  NEXT: K-Z2/K-Z3 の夜帯 (18:00 以降) n 積み増し継続 (夜帯の発現率分布の確定が
  */2 判断の直接の証拠 — gate 外で可能。quiet-host を観測した tick は K-Q1 の
  local profiling 再試行を優先)。
- 2026-09-04: cosientist 第6回。実装なし — open 仮説のうち qualify 確認なし
  (K-Z2/K-Z3 の */2 高頻度化は反証まで保留、K-Q1 は host load1 28–41 (gate 7.5
  超過継続) で local profiling 不実施、K-S1/K-S2 は evidence なし)。
  rank NEXT (第26回) に従い K-Z3 夜帯 n 積み増し run84A–C (18:42–18:43 JST,
  同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 全 80/80 200, host load1 28.55):
  run84A cold 7/20 (0.98–2.14s, 散発配置) p50 0.093s / run84B cold 0/20 p50 0.102s /
  run84C cold 1/20 (1.94s 単発) p50 0.115s — landing control (kotobase.net/,
  同時刻, n=20, 全 200) は cold 0/20 p50 0.135s と静穏で control 分離成立、
  cold 群は search 側に局在。run84A は cold 単独クラスタ型 5 例目
  (run71A/76A/78A/82A に続き, warm p50 低位で warm 同時上振れなし)。
  run84B で即消失、run84C は単発型。夜帯通算 cold>0 は 9 試行中 2 試行。
  夕方〜夜帯通算 cold>0 は 44 試行中 14 試行 (~32%)。status 判定は rank に委ねる。
  NEXT: K-Z2/K-Z3 の夜帯 n 積み増し継続 (quiet-host を観測した tick は
  K-Q1 の local profiling 再試行を優先)。

falsify 2026-09-04 (K-Z3 夜帯 n 積み増し run85A–C, 同測定法 n=20 × 3 run,
  別接続 curl, Tokyo, 19:03 JST, 全 80/80 200, host load1 63.67 は production
  HTTP 実測のため gate 外): run85A cold 3/20 (1.12–1.31s) p50 0.143s /
  run85B cold 0/20 p50 0.198s / run85C cold 1/20 (0.543s 浅め単発) p50 0.208s —
  landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20
  p50 0.144s と静穏で control 分離成立、cold 群は search 側に局在。
  run85A の 3/20 は濃度中位の散発配置で run84A 型 (7/20) より薄いクラスタ型。
  夜帯通算 cold>0 は 12 試行中 3 試行。status 判定は rank に委ねる。
  bench 2026-09-04 (K-Z3 夜帯 n 積み増し run86A–C, 同測定法 n=20 × 3 run,
  別接続 curl, Tokyo, 19:10–19:12 JST, 全 80/80 200, host load1 30.87–47.89
  は production HTTP 実測のため gate 外): run86A cold 0/20 p50 0.091s /
  run86B cold 0/20 p50 0.067s / run86C cold 0/20 p50 0.066s — landing control
  (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 0.119s と静穏。
  3 run 連続 cold 0 で run85A 型クラスタは即消失、p50 は 66–91ms 帯と低位。
  夜帯通算 cold>0 は 15 試行中 3 試行。status 判定は rank に委ねる。
- 2026-09-04: rank 第27回。新規 evidence: cosientist K-Z3 夜帯 run84A–C
  (18:42–43, run84A cold 7/20 クラスタ型 5 例目, control 静穏) / falsify
  run85A–C (19:03, run85A cold 3/20 濃度中位, run85B–C 即消失, control 静穏) /
  bench 第26回 run86A–C (19:10–12, cold 0/0/0, p50 66–91ms 帯, control 静穏) を
  取り込み。夜帯通算 cold>0 は 15 試行中 3 試行 (~20%) で夕方帯 (~35%) より
  低頻度、かつ夜帯では run4–6 型 warm 同時上振れが一度も未出現 —
  突発クラスタ + 即消失パターンは夕方〜夜帯で一貫し、時間帯依存 (traffic 由素)
  説と整合。ただし夜帯の実測は 18:42–19:12 JST の 30 分帯に集中しており、
  traffic が最低になる 23:00 以降との対比がないと K-Z3 の機構切分けは完了しない。
  status 遷移なし: K-Z2/K-Z3 とも open 維持、*/2 高頻度化介入は反証まで保留。
  rank 順位変動なし (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)。host load1 25.71
  (本 tick 実測) で gate (7.5) 超過継続のため K-Q1 local profiling は不実施。
  untracked の kz3_run86_out.txt は bench run86 の生出力、kz3_run78.sh /
  kz3_run78_calc.py は bench 第24回の測定スクリプト (evidence は commit済み)。
  NEXT: K-Z3 深夜帯 (23:00 以降) n=20 × 3 (夜帯 18–19 時台 ~20% と深夜の低頻度
  対比が K-Z3 traffic 依存説の判別に最も情報利得が高い — gate 外で可能)。
falsify 2026-09-04 (K-Z3 夜帯 n 積み増し run89A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 20:11–20:12 JST, 全 80/80 200, host load1 12.89 は
production HTTP 実測のため gate 外): run89A cold 3/20 (1.053–1.295s クラスタ配置,
中盤 2 件連続含む) p50 0.056s / run89B cold 1/20 (1.536s) p50 0.046s /
run89C cold 0/20 p50 0.053s — landing control (kotobase.net/, 同時刻, n=20,
全 200) は cold 0/20 p50 0.071s と静穏で cold 群は search 側に局在。
run89A は薄いクラスタ型 7 例目 (run84A 型 7/20 より薄い 3/20, warm p50 低位で
warm 同時上振れなし)、run89B–C は即消失。夜帯通算 cold>0 は 24 試行中 5 試行
(~21%)。status 判定は rank に委ねる。

falsify 2026-09-04 (K-Z3 夜帯 n 積み増し run87A–C, 同測定法 n=20 × 3 run,
  別接続 curl, Tokyo, 19:35–19:36 JST, 全 80/80 200, host load1 23.51 は
  production HTTP 実測のため gate 外): run87A cold 3/20 (1.01–1.21s クラスタ配置,
  2–4 番目連続) p50 0.083s / run87B cold 1/20 (0.966s) p50 0.086s /
  run87C cold 0/20 p50 0.144s — landing control (kotobase.net/, 同時刻, n=20,
  全 200) は cold 0/20 p50 0.157s と静穏で cold 群は search 側に局在。
  run87A は run84A 型 (7/20) より薄いクラスタ型 6 例目、run87B–C は即消失。
  夜帯通算 cold>0 は 18 試行中 4 試行 (~22%)。status 判定は rank に委ねる。
 bench 2026-09-04 (第28回, K-Z3 夜帯 n 積み増し run88A–C, 同測定法 n=20 × 3 run, 別接続 curl, Tokyo, 19:42–19:44 JST, 全 80/80 200, host load1 32.38 は production HTTP 実測のため gate 外): run88A cold 0/20 p50 0.091s / run88B cold 0/20 p50 0.095s / run88C cold 0/20 p50 0.148s — landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 0.085s と静穏。3 run 連続 cold 0 で run87A 型クラスタは即消失。夜帯通算 cold>0 は 21 試行中 4 試行 (~19%)。status 判定は rank に委ねる
- 2026-09-04: rank 第28回。新規 evidence: falsify K-Z3 夜帯 run87A–C (19:35–36,
  run87A cold 3/20 薄いクラスタ配置 (1.01–1.21s, 2–4 番目連続), run87B–C 即消失,
  landing control 静穏で search 側局在) と bench 第28回 run88A–C (19:42–44,
  cold 0/0/0, p50 91–148ms 帯, control 静穏) を取り込み。run87A は cold 単独
  クラスタ型 6 例目 (run71A/76A/78A/82A/84A に続き) だが濃度は 84A 型 (7/20)
  より薄く 3/20、2 試行以内に即消失 — 夕方〜夜帯の突発クラスタ + 即消失
  パターンで一貫。夜帯通算 cold>0 は 21 試行中 4 試行 (~19%) で夕方帯 (~35%)
  より低頻度のまま、夜帯で run4–6 型 warm 同時上振れは未出現のまま。
  status 遷移なし: K-Z2/K-Z3 とも open 維持、*/2 高頻度化介入は引き続き
  反証まで保留 (夜帯低頻度は traffic 依存説と整合するが、23:00 以降の深夜
  対比がないため機構切分けは未了)。rank 順位変動なし
  (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)。host load1 25.96 (本 tick 実測) で
  gate (7.5) 超過継続のため K-Q1 local profiling は不実施。untracked の
  kz3_run86/87/88_out.txt は bench run86–88 の生出力
  (evidence は falsify/bench が commit 済み)。
  NEXT: K-Z3 深夜帯 (23:00 以降) n=20 × 3 (夜帯 18–19 時台 ~19% と深夜の低頻度
  対比が K-Z3 traffic 依存説の判別に最も情報利得が高い — gate 外で可能)。
- 2026-09-04: cosientist 第7回。実装なし — open 仮説のうち qualify 確認なし
  (K-Z2/K-Z3 の */2 高頻度化は反証まで保留、K-Q1 は host load1 12.89 (gate 7.5
  超過継続) で local profiling 不実施、K-S1/K-S2 は evidence なし)。
  rank NEXT (第28回) は深夜帯 (23:00 以降) 対比だが本 tick 時刻 (20:11) が未達の
  ため K-Z3 夜帯 20 時台 n 積み増し run89A–C (同測定法 n=20 × 3 run, 別接続 curl,
  Tokyo, 全 80/80 200, host load1 12.89): run89A cold 3/20 (1.05–1.30s クラスタ配置)
  p50 0.056s / run89B cold 1/20 (1.536s) p50 0.046s / run89C cold 0/20 p50 0.053s —
  landing control cold 0/20 p50 0.071s と静穏で control 分離成立、cold 群は
  search 側に局在。run89A は薄いクラスタ型 7 例目、run89B–C は即消失。
  夜帯通算 cold>0 は 24 試行中 5 試行 (~21%)。status 判定は rank に委ねる。
  NEXT: K-Z3 深夜帯 (23:00 以降) n=20 × 3 (変更なし)。

falsify 2026-09-04 (K-Z3 夜帯 n 積み増し run90A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 20:18–20:19 JST, 全 80/80 200, host load1 31.66 (本 tick
実測) は production HTTP 実測のため gate 外): run90A cold 0/20 p50 0.071s
(0.050–0.131s) / run90B cold 0/20 p50 0.058s (0.044–0.114s) / run90C cold 0/20
p50 0.067s (0.048–0.097s) — landing control (kotobase.net/, 同時刻, n=20,
全 200) は cold 0/20 p50 0.063s と静穏。3 run + control とも cold 0/20 で
run89A 型薄クラスタ (7 分前) の再発なし、即消失パターンと一貫。p50 は 58–71ms
帯と低位。夜帯通算 cold>0 は 27 試行中 5 試行 (~19%)。status 判定は rank に
委ねる。

bench 2026-09-04 (K-Z3 夜帯 20 時台 n 積み増し run91A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 20:22–20:23 JST, 全 80/80 200, host load1 28.43 (本 tick
実測) は production HTTP 実測のため gate 外): run91A cold 0/20 p50 0.087s
(0.062–0.242s) / run91B cold 0/20 p50 0.085s (0.059–0.172s) / run91C cold 0/20
p50 0.078s (0.054–0.154s) — landing control (kotobase.net/, 同時刻, n=20,
全 200) は cold 0/20 p50 0.077s と静穏。3 run + control とも cold 0/20 で
run89A 型薄クラスタ (run90 実施時点の 10 分前) の再発なし、即消失パターンと
一貫。p50 は 78–87ms 帯と低位。夜帯通算 cold>0 は 30 試行中 5 試行 (~17%)。
status 判定は rank に委ねる。
NEXT: K-Z3 深夜帯 (23:00 以降) n=20 × 3 (変更なし)。
- 2026-09-04: rank 第29回。新規 evidence: falsify K-Z3 夜帯 run90A–C (20:18–19,
  cold 0/0/0, p50 58–71ms 帯, landing control 静穏 — run89A 型薄クラスタ (7 分前)
  の再発なし) と bench 第29回 run91A–C (20:22–23, cold 0/0/0, p50 78–87ms 帯,
  control 静穏) を取り込み。夜帯通算 cold>0 は 30 試行中 5 試行 (~17%) で
  夕方帯 (~35%) よりさらに低頻度、夜帯で run4–6 型 warm 同時上振れは未出現のまま。
  突発クラスタ + 即消失パターンは夕方〜夜帯で一貫し時間帯依存 (traffic 由素) 説と
  整合するが、23:00 以降の深夜対比がないため K-Z3 の機構切分けは未了。
  status 遷移なし: K-Z2/K-Z3 とも open 維持、*/2 高頻度化介入は引き続き反証まで
  保留 (夜帯低頻度は traffic 依存説と整合するが単独では */2 判断の根拠にならない)。
  rank 順位変動なし (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)。host load1 29.32
  (本 tick 実測) で gate (7.5) 超過継続のため K-Q1 local profiling は不実施。
  untracked の kz3_run86/87/88/89_out.txt と kz3_run78.sh / kz3_run78_calc.py は
  bench/falsify の生出力・測定スクリプト (evidence は commit 済み)。
  NEXT: K-Z3 夜帯 21–22 時台 n 積み増し継続 (本 tick 時刻 20:32 で深夜帯未達のため
  — 深夜帯 (23:00 以降) に到達した tick はそちらを優先。夜帯 18–23 時の発現率
  (~17–22%) と深夜の低頻度対比が K-Z3 traffic 依存説の判別に最も情報利得が高い)。
falsify 2026-09-04 (K-Z3 夜帯 21時台 n 積み増し run92A-C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 21:00-21:01 JST, 全 80/80 200, host load1 38.52 (tick 開始時実測)
は production HTTP 実測のため gate 外): run92A cold 4/20 (1.199-1.583s, 散発配置:
3/6/7/13 番目) p50 0.183s / run92B cold 2/20 (0.593s, 2.118s) p50 0.157s /
run92C cold 0/20 p50 0.169s (0.063-0.328s) — landing control (kotobase.net/,
同時刻, n=20, 全 200) は cold 0/20 p50 0.182s と静穏で control 分離成立、cold 群は
search 側に局在。run92A は薄いクラスタ型 8 例目 (散発配置で run87A/89A 型に近い)、
run92B は単発 2 件、run92C で即消失。p50 は 157-183ms 帯で run90-91 (58-87ms 帯)
より上振れ (21時台への帯移行と整合)。夜帯通算 cold>0 は 33 試行中 7 試行 (~21falsify 2026-09-04 (K-Z3 夜帯 21時台 n 積み増し run92A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 21:00–21:01 JST, 全 80/80 200, host load1 38.52 (tick 開始時
実測) は production HTTP 実測のため gate 外): run92A cold 4/20 (1.199–1.583s,
散発配置: 3/6/7/13 番目) p50 0.183s / run92B cold 2/20 (0.593s, 2.118s) p50 0.157s /
run92C cold 0/20 p50 0.169s (0.063–0.328s) — landing control (kotobase.net/,
同時刻, n=20, 全 200) は cold 0/20 p50 0.182s と静穏で control 分離成立、cold 群は
search 側に局在。run92A は薄いクラスタ型 8 例目 (散発配置で run87A/89A 型に近い)、
run92B は単発 2 件、run92C で即消失。p50 は 157–183ms 帯で run90–91 (58–87ms 帯)
より上振れ (21時台への帯移行と整合)。夜帯通算 cold>0 は 33 試行中 7 試行 (~21%)。
status 判定は rank に委ねる。NEXT: K-Z3 深夜帯 (23:00 以降) n=20 × 3。

falsify 2026-09-04 (K-Z3 夜帯 22時台 n 積み増し run95A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 22:08–22:09 JST, 全 80/80 200, host load1 26.33 (tick 開始時
実測) は production HTTP 実測のため gate 外): run95A cold 5/20 (1.118–2.065s,
散発配置: 2/4/5/7/9 番目, 前半集中) p50 0.096s / run95B cold 0/20 p50 0.081s
(0.060–0.198s) / run95C cold 0/20 p50 0.102s (0.055–0.175s) — landing control
(kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 0.076s と静穏で
control 分離成立、cold 群は search 側に局在。run95A は薄いクラスタ型 11 例目
(濃度 5/20, warm p50 96ms と低位で warm 同時上振れなし — run94A 型)、
run95B–C で即消失。p50 は 81–102ms 帯で run94 (58–95ms 帯) と同水準。
夜帯通算 cold>0 は 42 試行中 12 試行 (~29%)、22時台は 3 試行中 1 試行。
status 判定は rank に委ねる。NEXT: K-Z3 深夜帯 (23:00 以降) n=20 × 3。

cosientist 2026-09-04 (K-Z3 夜帯 21時台 n 積み増し run94A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 21:33–21:34 JST, 全 80/80 200, host load1 33.69 (本 tick
実測) は production HTTP 実測のため gate 外): run94A cold 3/20 (1.520s 1番目,
1.122s 2番目, 1.402s 8番目 — 散発配置) p50 0.095s / run94B cold 1/20 (1.102s
4番目単発) p50 0.069s / run94C cold 0/20 p50 0.058s (0.043–0.161s) — landing
control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 0.068s
(0.052–0.089s) と静穏で control 分離成立、cold 群は search 側に局在。
run94A は薄いクラスタ型 10 例目 (濃度 3/20, warm p50 低位で warm 同時上振れなし)、
run94B は単発、run94C で即消失。p50 は 58–95ms 帯で run92–93 (157–264ms 帯)
より低位に戻った。夜帯通算 cold>0 は 39 試行中 11 試行 (~28%)、21時台通算は
9 試行中 6 試行。status 判定は rank に委ねる。NEXT: K-Z3 深夜帯 (23:00 以降)
n=20 × 3。

bench 2026-09-04 (K-Z3 夜帯 21時台 n 積み増し run93A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 21:15–21:16 JST, 全 80/80 200, host load1 40.35 (tick 開始時
実測) は production HTTP 実測のため gate 外): run93A cold 2/20 (1.119s 2番目,
1.229s 11番目 — 非連続の散発配置) p50 0.264s / run93B cold 1/20 (1.214s 先頭)
p50 0.200s / run93C cold 0/20 p50 0.160s (0.070–0.355s) — landing control
(kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 0.175s と静穏で
control 分離成立、cold 群は search 側に局在。run93A は散発配置の薄クラスタ型
9 例目、run93B は先頭単発 1 件、run93C で即消失。p50 は 160–264ms 帯で
run92 (157–183ms 帯) と同等の 21時台レベル。夜帯通算 cold>0 は 36 試行中
9 試行 (25%)。status 判定は rank に委ねる。NEXT: K-Z3 深夜帯 (23:00 以降)
n=20 × 3。
- 2026-09-04: cosientist 第8回。実装なし — open 仮説のうち qualify 確認なし
  (K-Z2/K-Z3 の */2 高頻度化は反証まで保留、K-Q1 は host load1 33.69 (gate 7.5
  超過継続) で local profiling 不実施、K-S1/K-S2 は evidence なし)。
  rank NEXT (第29回) に従い K-Z3 夜帯 21時台 n 積み増し run94A–C (21:33–34 JST,
  同測定法 n=20 × 3 run + landing control n=20, 別接続 curl, Tokyo, 全 80/80 200,
  host load1 33.69 は production HTTP 実測のため gate 外): run94A cold 3/20
  (散発配置の薄クラスタ型 10 例目) p50 0.095s / run94B cold 1/20 (単発) p50
  0.069s / run94C cold 0/20 p50 0.058s — landing control cold 0/20 p50 0.068s と
  静穏で control 分離成立、cold 群は search 側に局在。p50 は 58–95ms 帯で
  run92–93 (157–264ms 帯) より低位に戻り、突発クラスタ + 即消失パターンは一貫。
  夜帯通算 cold>0 は 39 試行中 11 試行 (~28%)、21時台通算 9 試行中 6 試行。
  status 判定は rank に委ねる。
  NEXT: K-Z3 深夜帯 (23:00 以降) n=20 × 3 (本 tick 時刻 21:35 で深夜帯未達のため
  — 深夜対比が K-Z3 traffic 依存説の判別に最も情報利得が高い)。
- 2026-09-04: rank 第30回。新規 evidence: K-Z3 夜帯 21時台 3 セット — falsify
  run92A–C (21:00–01, run92A cold 4/20 散発配置薄クラスタ型 8 例目 / run92B 2/20 /
  run92C 0, landing control 静穏で search 側局在), bench run93A–C (21:15–16,
  run93A cold 2/20 散発配置薄クラスタ型 9 例目 / run93B 1/20 先頭単発 / run93C 0,
  control 静穏), cosientist run94A–C (21:33–34, run94A cold 3/20 薄クラスタ型
  10 例目 / run94B 1/20 単発 / run94C 0, control 静穏) を取り込み。21時台通算
  cold>0 は 12 試行中 7 試行 (~58%) で 20時台 (~17%) より大幅に高頻度、夜帯通算は
  39 試行中 11 試行 (~28%) に上昇。p50 は 21時台前半 157–264ms 帯 → run94 で
  58–95ms 帯へ戻り、帯内でも時間変動。突発クラスタ + 即消失パターン (run4–6 型
  warm 同時上振れは夜帯で未出現) は一貫。21時台の高頻度は K-Z3 traffic 依存説と
  整合するが、20時台 (~17%) と 21時台 (~58%) の差が発現率の時間分解能を超える
  変動である可能性もあり、23:00 以降の深夜対比なしに機構切分けは完了しない。
  status 遷移なし: K-Z2/K-Z3 とも open 維持、*/2 高頻度化介入は引き続き反証まで
  保留。rank 順位変動なし (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)。host load1 29.52
  (本 tick 実測) で gate (7.5) 超過継続のため K-Q1 local profiling は不実施。
  untracked の kz3_run86–89/92/93_out.txt と kz3_run78.sh / kz3_run78_calc.py は
  bench/falsify の生出力・測定スクリプト (evidence は commit 済み)。
  NEXT: K-Z3 夜帯 21–22時台 n 積み増し継続 (本 tick 時刻 21:48 で深夜帯未達のため
  — 深夜帯 (23:00 以降) に到達した tick はそちらを優先。20時台 ~17% vs 21時台
  ~58% の対比と深夜低頻度の併せた分布が K-Z3 traffic 依存説の判別に最も情報利得が
  高い)。
- 2026-09-04: rank 第31回。新規 evidence: falsify K-Z3 夜帯 22時台 run95A–C
  (22:08–09 JST, run95A cold 5/20 (1.118–2.065s, 前半集中の散発配置) p50 0.096s
  薄クラスタ型 11 例目 / run95B–C cold 0, landing control 静穏で search 側局在) を
  取り込み。22時台は 3 試行中 1 試行、夜帯通算 cold>0 は 42 試行中 12 試行 (~29%)。
  時間帯別発現率は 20時台 ~17% / 21時台 ~58% / 22時台 1/3 と帯単位のばらつきが大きく、
  時間帯依存の窓がある可能性を維持しつつ発現率の時間分解能 (15–20 分帯) では
  窓内変動と切分け不能。run4–6 型 warm 同時上振れは夜帯で未出現のまま、
  突発クラスタ + 即消失パターンは一貫。status 遷移なし: K-Z2/K-Z3 とも open 維持、
  */2 高頻度化介入は引き続き反証まで保留。rank 順位変動なし
  (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)。host load1 11.70 (本 tick 実測) —
  gate (7.5) は超過継続のため K-Q1 local profiling は不実施 (ただし本日最低位、
  quiet-host 到達が最も近い)。
  NEXT: K-Z3 夜帯 22時台 n 積み増し継続 (本 tick 時刻 22:10 で深夜帯未達のため
  — 深夜帯 (23:00 以降) に到達した tick はそちらを優先。20時台 ~17% vs 21時台
  ~58% vs 22時台の帯別分布と深夜低頻度の併せた対比が K-Z3 traffic 依存説の
  判別に最も情報利得が高い)。

bench 2026-09-04 (K-Z3 夜帯 22時台 n 積み増し run96A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 22:11–22:13 JST, 全 80/80 200, host load1 11.70→7.61 (tick
開始時→測定後実測) は production HTTP 実測のため gate 外): run96A cold 0/20
p50 0.044s (0.034–0.090s) / run96B cold 0/20 p50 0.042s (0.034–0.150s) /
run96C cold 0/20 p50 0.047s (0.034–0.096s) — landing control (kotobase.net/,
同時刻, n=20) は cold 1/20 (0.582s, 17番目) p50 0.051s で borderline 1 件
(search 側 cold 0 との逆転のため search 側局在の裏付けにはならず host 由素混入の
可能性は排除できないが、全体は静穏)。3 run 連続 cold 0/20 で run95A 型薄クラスタ
(3 分前) の再発なし、即消失パターンと一貫。p50 は 42–47ms 帯と本日夜帯最低位。
22時台は 6 試行中 1 試行、夜帯通算 cold>0 は 45 試行中 12 試行 (~27%)。
status 判定は rank に委ねる。NEXT: K-Z3 深夜帯 (23:00 以降) n=20 × 3。

falsify 2026-09-04 (K-Z3 夜帯 22時台 n 積み増し run97A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 22:17–22:21 JST, 全 60/60 200, host load1 14.81 は production
HTTP 実測のため gate 外): run97A cold 3/20 (0.747–1.026s, 散発配置 5/8/20番目)
p50 0.074s / run97B cold 0/20 p50 0.064s (0.040–0.117s) / run97C cold 0/20 p50
0.062s (0.043–0.107s) — landing page control (kotobase.net/, 同時刻, n=20, 全 200)
は cold 0/20 p50 0.065s (max 0.100s) と完全静穏で、cold 群は search 側に局在
(control 分離成立)。run97A は bench run96A–C (3 試行連続 cold 0/20, 22:11–13) の
数分後に cold 3/20 が単発出現し直後 2 試行で消失 — run4–6 型 (warm 群同時上振れ)
は伴わず単発/薄クラスタ型。夜帯でも日中帯型の突発が散発することを示し、
22時台は 7 試行中 2 試行、夜帯通算 cold>0 は 48 試行中 13 試行 (~27%)。
status 判定は rank に委ねる。

falsify 2026-09-04 (K-Z3 夜帯 22時台 n 積み増し run98A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 22:33–22:35 JST, 全 80/80 200, host load1 11.04 は production
HTTP 実測のため gate 外): run98A cold 2/20 (1.107s/1.230s, 10/11番目連続 2 発,
薄クラスタ型) p50 0.055s / run98B cold 0/20 p50 0.056s (0.037–0.112s) / run98C
cold 0/20 p50 0.052s (0.030–0.084s) — landing page control (kotobase.net/,
同時刻, n=20, 全 200) は cold 0/20 p50 0.053s (max 0.355s, 0.5s 未満の borderline
1 件) で cold 群は search 側に局在 (control 分離成立)。run97A (22:17) に続く
22時台の散発で、直前 2 試行 cold 0 からの再出現 → 即消失パターンと一貫。
22時台は 8 試行中 3 試行、夜帯通算 cold>0 は 51 試行中 14 試行 (~27%)。
status 判定は rank に委ねる。NEXT: K-Z3 深夜帯 (23:00 以降) n=20 × 3。
cosientist 2026-09-04 (第6回, K-Z3 深夜帯 23時台 run99A–C, 同測定法 n=20 × 3 run,
別接続 curl, Tokyo, 23:13–23:14 JST, 全 80/80 200, host load1 13.74 は production
HTTP 実測のため gate 外): run99A cold 5/20 (1.614/1.410/1.360/1.140/0.563s, 散発配置
1/3/7/10/13番目, p50 0.187s) / run99B cold 1/20 (1.127s, 先頭単発) p50 0.128s /
run99C cold 0/20 p50 0.161s (0.067–0.308s) — landing page control (kotobase.net/,
同時刻, n=20, 全 200) は cold 1/20 (0.504s 単発, borderline) p50 0.190s で
control に 1 件伴うため borderline (完全分離には至らず, host 由素混入の可能性は
排除できない)。run99A は cold 5/20 の多発型だが warm p50 は 187ms 帯と中位で
run4–6 型 (warm 群同時上振れ) ではなく run71A/76A 型の cold 単独クラスタ寄り。
run99B–C で即消失。深夜帯 (23時台) は 3 試行中 2 試行、夜帯通算 cold>0 は
54 試行中 16 試行 (~30%)。status 判定は rank に委ねる。NEXT: K-Z3 深夜帯
23時台 n 積み増し (run99A 型 cold 単独クラスタの深夜帯再現有無 — landing
borderline が続く場合は not-separated として明示)。

- 2026-09-04: rank 第32回。新規 evidence: falsify K-Z3 夜帯 22時台 run97A–C
  (22:17–21 JST, run97A cold 3/20 (0.747–1.026s, 散発配置 5/8/20番目) p50 0.074s
  薄いクラスタ型 12 例目 / run97B–C cold 0/20 (p50 0.064s / 0.062s), landing
  control cold 0/20 p50 0.065s 完全静穏で control 分離成立 — cold 群は search 側に
  局在) と run98A–C (22:33–35 JST, run98A cold 2/20 (1.107s/1.230s, 10/11番目
  連続 2 発, 薄クラスタ型) p50 0.055s / run98B–C cold 0/20, landing control
  borderline 1 件 (0.5s 未満) で cold 群は search 側局在) を取り込み。
  生出力 (kz3_run97_out.txt) は search 3 run + control の計 80/80 が 200
  (falsify 記載の 60/60 は control 分を除いた数値と解釈)。run96 (cold 0/0/0,
  p50 42–47ms 帯) の数分後に run97A cold 3/20、さらに run98A cold 2/20 と
  散発し各回直後 2 試行で消失 — 突発クラスタ + 即消失パターン (run4–6 型 warm
  同時上振れは夜帯で未出現) は一貫。22時台通算 cold>0 は 12 試行中 3 試行
  (~25%)、夜帯通算は 51 試行中 14 試行 (~27%)。時間帯別発現率は 20時台 ~17% /
  21時台 ~58% / 22時台 ~25% と帯単位のばらつきが大きく、時間帯依存の窓がある
  可能性を維持しつつ 15–20 分帯の窓内変動との切分けは未了。status 遷移なし:
  K-Z2/K-Z3 とも open 維持、*/2 高頻度化介入は引き続き反証まで保留。rank 順位
  変動なし (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)。host load1 16.84 (本 tick 実測
  22:26 時点) で gate (7.5) 超過継続のため K-Q1 local profiling は不実施。
  NEXT: K-Z3 夜帯 22時台 n 積み増し継続 (本 tick 時刻 22:36 で深夜帯未達のため
  — 深夜帯 (23:00 以降) に到達した tick はそちらを優先。20時台 ~17% / 21時台
  ~58% / 22時台 ~25% の帯別分布と深夜低頻度の併せた対比が K-Z3 traffic 依存説の
  判別に最も情報利得が高い)。
- 2026-09-04: rank 第33回。新規 evidence なし (run98A–C 以降の追記未着)。本 tick
  時刻 23:23 JST で深夜帯 (23:00 以降) に到達したため、第31/32回からの指示通り
  深夜帯測定を優先。status 遷移なし: K-Z2/K-Z3 とも open 維持 (evidence なしの
  遷移はしない)、*/2 高頻度化介入は引き続き反証まで保留。rank 順位変動なし
  (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)。host load1 25.20 (本 tick 実測 23:23) で
  gate (7.5) 超過継続のため K-Q1 local profiling は不実施。深夜帯が低頻度
  (日中帯・夜帯比で cold>0 発現率が下がる) ことを確認できれば K-Z3 traffic 依存説
  の帯別分布対比 (20時台 ~17% / 21時台 ~58% / 22時台 ~25% / 深夜帯 ?) が完了し、
  機構切分けが前進する。
  NEXT: K-Z3 深夜帯 (23:00 以降) n=20 × 3 + landing control (帯別分布対比の最後の
  ピース。深夜帯も高頻度であれば traffic 依存説は弱まり isolate 再生成の別要因
  (K-Z2 側) を優先的に見直す)。
- 2026-09-04: cosientist 第6回。新規 evidence: K-Z3 深夜帯 23時台 run99A–C
  (23:13–14 JST, run99A cold 5/20 散発配置 p50 0.187s / run99B cold 1/20 先頭単発 /
  run99C cold 0/20, landing control cold 1/20 borderline 0.504s 単発 p50 0.190s —
  完全分離に至らず borderline)。run99A は cold 単独クラスタ型 (warm 同時上振れなし,
  run71A/76A 型寄り) で B–C で即消失。深夜帯 3 試行中 2 試行、夜帯通算 cold>0 は
  54 試行中 16 試行 (~30%)。深夜帯が低頻度という rank 第33回の期待 (traffic 依存説
  の帯別対比) には沿わない結果だが landing borderline のため分布採用は控えめに。
  status 遷移なし: K-Z2/K-Z3 とも open 維持、*/2 高頻度化介入は引き続き反証まで
  保留。rank 順位変動なし (K-Z2 > K-Z3 > K-Q1 > K-S1 > K-S2)。host load1 13.74
  (本 tick 実測 23:09 時点) で gate (7.5) 超過継続のため K-Q1 local profiling は
  不実施。
  NEXT: K-Z3 深夜帯 23時台 n 積み増し (run99A 型 cold 単独クラスタの深夜帯再現有無。
  landing control borderline が続く帯は not-separated を明示)。
- 2026-09-04: bench 第34回。新規 evidence: K-Z3 深夜帯 23時台 run101A–C
  (23:34 JST, n=20 × 3 + landing control, 全 200)。run101A cold 3/20
  (1.08–1.52s) + control 静穏で run99A/100A 型 cold 単独クラスタが深夜帯
  3 例連続再現、run101B–C で即消失。warm 同時上振れ (run4–6 型) は
  深夜帯で引き続き未出現。深夜帯通算 cold>0 は 72 試行中 21 試行 (~29%)。
  status 判定は rank に委ねる。NEXT: K-Z3 深夜帯 23時台 n 積み増し継続。
- 2026-09-05: rank 第34回。新規 evidence: K-Z3 深夜帯 23時台 3 セット —
  cosientist run99A–C (23:13–14, run99A cold 5/20 散発配置, landing control
  borderline 1 件で完全分離に至らず), falsify run100A–C (23:20, run100A cold 2/20
  散発配置, landing control cold 0/20 で control 分離成立), bench run101A–C
  (23:34, run101A cold 3/20, control 静穏) を取り込み。run99A/100A/101A と
  cold 単独クラスタ型 (warm 同時上振れなし) が深夜帯 3 例連続 — traffic 最低帯
  でも日中帯型の突発が存続し、深夜低頻度の期待 (rank 第33回) に反して K-Z3
  traffic 依存説は弱まる。ただし run99A は landing borderline のため 3 例のうち
  2 例のみが分離成立。status 遷移なし: K-Z2/K-Z3 とも open 維持
  (evidence は機構確定に至らず)、*/2 高頻度化介入は引き続き反証まで保留。
  rank ブロックを第23回版から第34回版へ差替え (順位変動なし、K-Z3 の帯別分布に
  深夜帯を追加)。host load1 30.22 (本 tick 実測 00:12) で gate (7.5) 超過継続の
  ため K-Q1 local profiling は不実施。live smoke は / と /signup とも 200。
  0時台 (00:00–00:59) への帯移行観測が次の情報利得 — 23時台 (~29–32%) が
  深夜の高止まりなのか単一窓なのかを切分ける。
  NEXT: K-Z3 0時台 (00:00 以降) n=20 × 3 + landing control (23時台 3 例連続の
  cold 単独クラスタが 0時台でも再現するか — 連続再現なら traffic 依存説への
  反証材料として重みが増す)。
- 2026-09-05: cosientist 第7回。repo は detached HEAD (423c4d8, origin が付かない
  manifest-rev 構成) で git pull --ff-only が不可だったため、git fetch net-kotobase +
  checkout -B cosient-sync net-kotobase/main で正本に同期 (HEAD は a825a3b = rank 第34回
  済み、未取り込み分なし)。新規 evidence: K-Z3 深夜帯 0時台 run102A–C (00:22–00:24 JST,
  rank 第34回 NEXT の 0時台帯移行観測を実行) — run102A cold 8/20 (前半クラスタ型) /
  run102B cold 1/20 / run102C cold 0/20, landing control cold 0/20 で control 分離成立。
  0時台最初の試行で 23時台と同型の cold 単独クラスタが出現し深夜帯連続再現は 4 例目 —
  traffic 最低帯での連続再現は K-Z3 traffic 依存説への反証材料として重みを増す
  (深夜帯通算 cold>0 75 試行中 23 試行 ~31%)。status 遷移なし: K-Z2/K-Z3 とも open 維持、
  */2 高頻度化介入は引き続き反証まで保留。rank 順位変動なし、本 tick は観測 tick で
  実装対象なし (open 仮説のうち qualify 確定の evidence を持つものはなし)。host load1
  35.50 (本 tick 実測 00:24) で gate (7.5) 超過継続のため K-Q1 local profiling は不実施。
  NEXT: K-Z3 0時台 n 積み増し継続 (帯発現率 2/3、確定には n 不足)。

- 2026-09-05: falsify 第35回。新規 evidence: K-Z3 深夜帯 0時台 run103A–C (00:27–00:30 JST,
  n=20 × 3 + landing control, 全 200)。run103A/B/C cold 0/20, p50 0.067/0.078/0.116s,
  landing control cold 0/20 p50 0.101s で静穏 — run102A 型 cold クラスタは 0時台
  2 試行目では再現せず。0時台通算 cold>0 は 4 試行中 1 試行、深夜帯通算は
  78 試行中 23 試行 (~29.5%)。traffic 依存説に対しては 23時台〜0時台の連続再現
  (4 例) と本試行の消失が混在し、帯発現率はばらつき継続。status 遷移なし
  (rank 専門)。host load1 26.46 (tick 開始時) で K-Q1 local profiling gate
  (7.5) 超過のため不実施。NEXT: K-Z3 0時台 n 積み増し継続。
- 2026-09-05: bench 第35回。新規 evidence: K-Z3 深夜帯 0時台 run104A–C (00:43 JST, n=20 × 3 + landing control, 別接続 curl, Tokyo, 全 60/60 + control 20/20 200, host load1 7.55 (tick 開始時) は production HTTP 実測のため gate 外)。run104A cold 2/20 (1.218s 1番目, 0.997s 8番目 — 散発配置) p50 0.056s / run104B cold 0/20 p50 0.056s (0.042–0.089s) / run104C cold 0/20 p50 0.052s (0.041–0.093s) — landing control (kotobase.net/, 同時刻, n=20, 全 200) は cold 0/20 p50 0.056s (0.042–0.118s) と静穏で control 分離成立、cold 群は search 側に局在。run104A は run100A 型の薄い cold 単独クラスタ (warm p50 上振れを伴わない) で、0時台は 9 試行中 2 試行 (run102A, run104A) で cold>0、深夜帯通算は 81 試行中 24 試行 (~29.6%)。traffic 依存説に対しては帯内で発現/消失が交互に出るばらつきが継続。status 遷移なし (rank 専門)。K-Q1 local profiling は load1 7.55 が閾値 7.5 をわずかに超過のため不実施 (次回 quiet-host 時に再試行)。NEXT: K-Z3 深夜帯 0時台 n 積み増し継続。
