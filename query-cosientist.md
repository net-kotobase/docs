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
| K-Q1 | query | warm query p50 187ms の内訳は edge/network ではなく Worker CPU + Biscuit verify が支配的 (Biscuit verify 単体は測定済み p50 18.65ms なので、残り ~170ms は query 実行 + edge)。engine の query 実行 path を hand-profilable な形で local 実行して内訳を実測する | open | bench 2026-09-03: 未測定 — host busy (load1 17.50 / 1min, 閾値 7.5 超過のため local profiling を実施せず終了)。次回 quiet-host 時に再試行 |
| K-Q2 | query | 同一測定法での再測 (2026-08-26 との比較) で p50 が再現するか — 測定の再現性を先に確立する (基準線の固定) | executed (再現せず) | rank 2026-09-03: falsify 実測 2 run (753.41/908.69ms, p95 884/1668) で基準線 187.35ms は不再現 → 判定確定。後続は K-Q1 (退行切り分け) へ |
| K-W1 | worker | live smoke 4xx 2% の内訳は path 固有 (bot traffic) であり、 Worker のバグではない — /api/funnel と status code 分布の実測で反証する | open | bench 2026-09-03: production GET 実測 (kotobase.net, n=30/path, 100ms 間隔, host load1 15.91 は production HTTP 実測のため gate 外): / /signup /api/funnel は全 30/30=200 (p50 32/28/77ms) — smoke 対象 path は健全。4xx は path 固有で決定的: /login 404 30/30, /api/status 404 30/30, /wp-login.php /.env /xmlrpc.php 404 30/30, /admin 401 30/30 — ランダム/断続的な Worker エラーではなく特定 path の恒常応答。bot 起源説と整合 (判定は rank に委ねる) |
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

| K-Z1 | worker | K-W2 の反証で実在が確認された isolate 単位の cold penalty (+0.8–1.8s, 発現率 ~35%) は、定期 self-ping (isolate warm-up) で発現率を測定可能な水準まで下げられる — warm-up 導入前後で /search?q= の cold 群出現率を同測定法で比較する | open | bench 2026-09-03: warm-up 前基準線 (search.kotobase.net /search?q=test, n=20, 別接続 curl, Tokyo, host load1 16.29 は production HTTP 実測のため gate 外): cold 群 (TTFB>500ms) 7/20, TTFB 1.41–2.22s / warm 群 13/20 45–83ms, 全 200。falsify 同日実測 (7/20, 0.85–1.8s) を再現 — warm-up 導入前の cold 群出現率 ~35% を確定 |

rank (期待 gain × 確率, 2026-09-03 第2回):
1. K-Q1 — K-Q2 の実測で +566〜721ms の退行が query path 側と帰属確定。
   退行の切り分けは現状最大の既知 gain (~170ms 課題を含む)。確率中〜高。
2. K-Z1 — 実測済み penalty (~35% に +0.8–1.8s)。gain 大だが query 退行を優先。
3. K-S1 — claim contract の storage 判定に必要。中。
4. K-W1 — 4xx 2% は影響小だが安価。
5. K-S2 — 1 CID 反復読み出し、条件付き改善。中。
( K-Q2 は executed — 再現性検証の役割を完了 )

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
