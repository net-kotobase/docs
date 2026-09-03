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
  のため実施せず記録のみ — 次回 quiet-host 時に再試行。 |
| K-Q2 | query | 同一測定法での再測 (2026-08-26 との比較) で p50 が再現するか — 測定の再現性を先に確立する (基準線の固定) | executed (再現せず) | rank 2026-09-03: falsify 実測 2 run (753.41/908.69ms, p95 884/1668) で基準線 187.35ms は不再現 → 判定確定。後続は K-Q1 (退行切り分け) へ |
| K-W1 | worker | live smoke 4xx 2% の内訳は path 固有 (bot traffic) であり、 Worker のバグではない — /api/funnel と status code 分布の実測で反証する | executed (仮説どおり) | bench 2026-09-03: production GET 実測 (kotobase.net, n=30/path, 100ms 間隔, host load1 15.91 は production HTTP 実測のため gate 外): / /signup /api/funnel は全 30/30=200 (p50 32/28/77ms) — smoke 対象 path は健全。4xx は path 固有で決定的: /login 404 30/30, /api/status 404 30/30, /wp-login.php /.env /xmlrpc.php 404 30/30, /admin 401 30/30 — ランダム/断続的な Worker エラーではなく特定 path の恒常応答。bot 起源説と整合 (判定は rank に委ねる)。falsify 2026-09-03 独立再現 (production GET, n=10/path, 200ms 間隔, host load1 17.75 は production HTTP 実測のため gate 外): code 分布が bench と完全一致 — / /api/funnel 200 10/10, /login /api/status /wp-login.php 404 10/10, /admin 401 10/10。bot 起源説の反証は不成立 (仮説どおり path 固有恒常応答) |
| K-W2 | worker | search.kotobase.net の in-memory projection は起動後初回リクエストで cold penalty を持つ — /search?q= の初回 vs 2回目 latency 実測 | refuted (初回 1 回説) | falsify 2026-09-03: n=20 で cold 群 7/20, isolate 単位で再発 — 詳細は population 直下の注記 |
| K-S1 | storage | KOTOBASE_PACK_WRITES 有効 (testnet) は write path を測定劣化させない — engine の local test で pack on/off 比較 | open | — |
| K-S2 | storage | 1 commit CID 構造の map/git/search 統合読み出しは、同一 CID への反復読み出しで KV キャッシュに乗り p50 が改善する — 同一 CID 反復 vs 初回の実測 | open | — |

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

| K-Z1 | worker | K-W2 の反証で実在が確認された isolate 単位の cold penalty (+0.8–1.8s, 発現率 ~35%) は、定期 self-ping (isolate warm-up) で発現率を測定可能な水準まで下げられる — warm-up 導入前後で /search?q= の cold 群出現率を同測定法で比較する | open | bench 2026-09-03: warm-up 前基準線 (search.kotobase.net /search?q=test, n=20, 別接続 curl, Tokyo, host load1 16.29 は production HTTP 実測のため gate 外): cold 群 (TTFB>500ms) 7/20, TTFB 1.41–2.22s / warm 群 13/20 45–83ms, 全 200。falsify 同日実測 (7/20, 0.85–1.8s) を再現 — warm-up 導入前の cold 群出現率 ~35% を確定。cosientist 2026-09-03: warm-up 実装 — search-origin PR #4 (bot/cosient-20260903-kz1-warmup): worker.cljs に scheduled handler (in-process /search?q=test 実行) + wrangler crons */5。shadow-cljs build 成功 (0 warnings)。fetch path 未変更。after 計測 (同測定法 n=20) は deploy 後。falsify 2026-09-03 第2回: before 基準線 n 追加 (同測定法 n=20, 別接続 curl, Tokyo, PR #4 は main 未マージで warm-up 未 deploy のまま): cold 群 7/20 (TTFB 0.90–1.87s), warm 群 13/20 (44–85ms), 全 200 — bench/falsify 初回の 7/20 を再現し基準線は 3 試行で安定。導入後比較の統計的土台は十分 |

rank (期待 gain × 確率, 2026-09-04 第6回):
1. K-Q1 — 恒常的 query path 退行の切り分け。falsify 第2切れ手 (repo diff 調査) により
   gateway 差分は否定され、infra/data 側 (graph-for の graph CID 解決, KV 依存の
   データ成長) と x402 gate の resolve-viewer 2 重解決 (#600) が有力説明候補。
   測定外の特定はこれ以上進まず、次は verify-session 1 重化 hand-patch の
   local 効果予測が最安の切れ手。
2. K-Z1 — before 基準線 3 試行で安定。残るは PR #4 merge/deploy 後の after 計測
   のみで、deploy 前に falsify/bench ができることはない。
3. K-S1 — claim contract の storage 判定に必要。中 (local gate の影響を受ける)。
4. K-S2 — 1 CID 反復読み出し、条件付き改善。中。
( K-Q2 / K-W1 / K-W2 は判定済みのため rank 外 )

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
