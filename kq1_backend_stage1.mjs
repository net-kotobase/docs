// K-Q1 backend query path 計測 第1段 (rank 第38回 NEXT)
// (1) datomic.kotobase.net (gateway 経由 /api/q) — 認証不要のため 401 を想定:
//     計測対象は resolve-viewer までの gateway authn 前段 latency (エラー応答 path)
//     → これは warm query 計測には使えない。代わりに:
// (2) engine.kotobase.net は DNS 不通のため backend 直叩き不可。
// (3) したがって第1段として gateway 単独の分解計測: /api/q POST (401 応答) の
//     TTFB vs total、および / (200, 静的) との対比。secret 不含 (credential なし)。
// 同一測定法: 30 sequential + 3 warmup 除外, nearest-rank, 接続再利用 (Node fetch keepalive)。
import https from "node:https";

const ORIGIN = "https://datomic.kotobase.net";
const agent = new https.Agent({ keepAlive: true, maxSockets: 1 });
const N = 30;
const WARMUP = 3;

function post(path, body, headers = {}) {
  return new Promise((resolve, reject) => {
    const payload = Buffer.from(JSON.stringify(body));
    const t0 = performance.now();
    const req = https.request(ORIGIN + path, {
      method: "POST",
      agent,
      headers: { "content-type": "application/json", "content-length": payload.length, ...headers },
      timeout: 15000,
    }, (res) => {
      let ttfb = performance.now() - t0;
      const chunks = [];
      res.on("data", (c) => chunks.push(c));
      res.on("end", () => {
        const total = performance.now() - t0;
        resolve({ status: res.statusCode, ttfb, total, bytes: Buffer.concat(chunks).length });
      });
    });
    req.on("timeout", () => { req.destroy(new Error("timeout")); });
    req.on("error", reject);
    req.end(payload);
  });
}

function get(path) {
  return new Promise((resolve, reject) => {
    const t0 = performance.now();
    const req = https.request(ORIGIN + path, { method: "GET", agent, timeout: 15000 }, (res) => {
      const ttfb = performance.now() - t0;
      const chunks = [];
      res.on("data", (c) => chunks.push(c));
      res.on("end", () => {
        resolve({ status: res.statusCode, ttfb, total: performance.now() - t0, bytes: Buffer.concat(chunks).length });
      });
    });
    req.on("timeout", () => { req.destroy(new Error("timeout")); });
    req.on("error", reject);
    req.end();
  });
}

function nearestRank(sorted, p) {
  const idx = Math.max(0, Math.ceil(p * sorted.length) - 1);
  return sorted[idx];
}

function stats(name, samples) {
  const s = samples.map(x => x.total).sort((a, b) => a - b);
  const tt = samples.map(x => x.ttfb).sort((a, b) => a - b);
  const codes = {};
  for (const x of samples) codes[x.status] = (codes[x.status] || 0) + 1;
  return {
    name, n: samples.length, codes,
    total_p50: nearestRank(s, 0.5), total_p95: nearestRank(s, 0.95),
    ttfb_p50: nearestRank(tt, 0.5), ttfb_p95: nearestRank(tt, 0.95),
    total_min: s[0], total_max: s[s.length - 1],
  };
}

const out = { date: new Date().toISOString(), origin: ORIGIN, runs: [] };

// warmup + 30 sequential: POST /api/q (no auth → expect 401; measures gateway authn pre-stage)
for (let i = 0; i < WARMUP; i++) await post("/api/q", { query: "[:find ?e :where [?e _ _]]" });
const q = [];
for (let i = 0; i < N; i++) q.push(await post("/api/q", { query: "[:find ?e :where [?e _ _]]" }));
out.runs.push(stats("POST /api/q (no-auth, 401 path)", q));

// warmup + 30: GET / (static info endpoint, 200) — gateway base overhead
for (let i = 0; i < WARMUP; i++) await get("/");
const g = [];
for (let i = 0; i < N; i++) g.push(await get("/"));
out.runs.push(stats("GET / (200 static)", g));

// sample body of 401 to confirm path reached resolve-viewer (no secret)
const probe = q[0];
out.probe_status = probe.status;
out.probe_bytes = probe.bytes;

console.log(JSON.stringify(out, null, 1));
