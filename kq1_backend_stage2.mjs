// K-Q1 backend query path 計測 第2段 (rank 第38回 NEXT: K-Q2 harness 再使用 + TTFB/total 分解)
// SIWE (ephemeral EOA, --provision 相当) → Biscuit issuance → authenticated /xrpc/datomic.q
// を keepalive 1 socket + TTFB/total 記録で実測。secret 不含 (秘密鍵は ephemeral, 記録しない)。
import { randomBytes } from "node:crypto";
import { secp256k1 } from "@noble/curves/secp256k1.js";
import { keccak_256 } from "@noble/hashes/sha3.js";
import https from "node:https";

const AUTHN = "https://auth.kotobase.net";
const API = "https://kotobase.net";
const N = 30;
const WARMUP = 3;
const agent = new https.Agent({ keepAlive: true, maxSockets: 4 });

function hex(b) { return Buffer.from(b).toString("hex"); }
function eip191Digest(message) {
  const payload = Buffer.from(message, "utf8");
  const prefix = Buffer.from(`\x19Ethereum Signed Message:\n${payload.length}`, "utf8");
  return keccak_256(Buffer.concat([prefix, payload]));
}
const privateKey = randomBytes(32);
const publicKey = secp256k1.getPublicKey(privateKey, false);
const address = `0x${hex(keccak_256(publicKey.slice(1))).slice(-40)}`;
function signatureFor(message) {
  const recovered = secp256k1.sign(eip191Digest(message), privateKey, { prehash: false, lowS: true, format: "recovered" });
  const sig = new Uint8Array(65);
  sig.set(recovered.slice(1), 0);
  sig[64] = 27 + recovered[0];
  return `0x${hex(sig)}`;
}

function req(url, { method = "GET", headers = {}, body = null } = {}) {
  return new Promise((resolve, reject) => {
    const payload = body === null ? null : Buffer.from(JSON.stringify(body));
    const t0 = performance.now();
    const r = https.request(url, {
      method, agent, timeout: 20000,
      headers: {
        ...(payload ? { "content-type": "application/json", "content-length": payload.length } : {}),
        ...headers,
      },
    }, (res) => {
      const chunks = [];
      res.on("data", (c) => chunks.push(c));
      res.on("end", () => {
        const text = Buffer.concat(chunks).toString("utf8");
        resolve({
          status: res.statusCode, ttfb: performance.now() - t0,
          total: performance.now() - t0, text,
          setCookie: res.headers["set-cookie"]?.[0] || null,
        });
      });
    });
    r.on("timeout", () => r.destroy(new Error("timeout")));
    r.on("error", reject);
    r.end(payload);
  });
}

function jsonHeaders(extra = {}) {
  return { "content-type": "application/json", origin: AUTHN, ...extra };
}

function nearestRank(sorted, p) { return sorted[Math.max(0, Math.ceil(p * sorted.length) - 1)]; }
function stats(samples) {
  const s = samples.map(x => x.total).sort((a, b) => a - b);
  const tt = samples.map(x => x.ttfb).sort((a, b) => a - b);
  const codes = {};
  for (const x of samples) codes[x.status] = (codes[x.status] || 0) + 1;
  return { n: samples.length, codes, total_p50: nearestRank(s, 0.5), total_p95: nearestRank(s, 0.95), ttfb_p50: nearestRank(tt, 0.5), ttfb_p95: nearestRank(tt, 0.95), total_min: s[0], total_max: s[s.length - 1] };
}

const out = { date: new Date().toISOString(), client: "Tokyo (host)", runs: [] };
try {
  const opt = await req(`${AUTHN}/v1/siwe/options`, { method: "POST", headers: jsonHeaders(), body: { address, chain_id: "1", return_to: "https://kotobase.net/admin" } });
  if (opt.status !== 200) throw new Error(`siwe options ${opt.status} ${opt.text.slice(0, 200)}`);
  const msg = JSON.parse(opt.text).message;
  const ver = await req(`${AUTHN}/v1/siwe/verify`, { method: "POST", headers: jsonHeaders(), body: { nonce: JSON.parse(opt.text).nonce, signature: signatureFor(msg) } });
  if (ver.status !== 200) throw new Error(`siwe verify ${ver.status} ${ver.text.slice(0, 200)}`);
  const cookie = ver.setCookie.split(";", 1)[0];
  const runId = `biscuit-query-${Date.now()}`;
  const prov = await req(`${AUTHN}/v1/tenants`, { method: "POST", headers: jsonHeaders({ cookie }), body: { name: `Biscuit query benchmark ${runId}` } });
  if (prov.status !== 201) throw new Error(`provision ${prov.status} ${prov.text.slice(0, 200)}`);
  const tenant = JSON.parse(prov.text).tenant;
  const issue = await req(`${AUTHN}/v1/biscuit/token`, { method: "POST", headers: jsonHeaders({ cookie }), body: { tenantId: tenant.id, dbName: runId, permissions: ["data:read", "data:write"] } });
  if (issue.status !== 201) throw new Error(`issue ${issue.status} ${issue.text.slice(0, 200)}`);
  const issued = JSON.parse(issue.text);
  const authorization = issued.authorization;
  const graph = issued.graph;
  out.tenant_shape = { hasAuth: /^Biscuit /.test(authorization || ""), graphLen: (graph || "").length };

  const txEdn = `[{ :db/id "${runId}" :bench/run-id "${runId}" :bench/value "authenticated" }]`;
  const write = await req(`${API}/xrpc/ai.gftd.apps.kotobase.datomic.transact`, {
    method: "POST",
    headers: { authorization, "x-kotobase-tenant-did": tenant.did, "x-kotobase-db-name": runId },
    body: { db_name: runId, tx_edn: txEdn },
  });
  out.write = { status: write.status, total: Number(write.total.toFixed(2)) };
  if (write.status !== 200) throw new Error(`write ${write.status} ${write.text.slice(0, 200)}`);

  const queryEdn = `{:find [?e ?value] :where [[?e :bench/run-id "${runId}"] [?e :bench/value ?value]]}`;
  const body = { graph, db_name: runId, query_edn: queryEdn };
  const headers = { authorization, "x-kotobase-tenant-did": tenant.did, "x-kotobase-db-name": runId };
  const q = async () => req(`${API}/xrpc/ai.gftd.apps.kotobase.datomic.q`, { method: "POST", headers, body });
  const first = await q();
  if (first.status !== 200) throw new Error(`first query ${first.status} ${first.text.slice(0, 200)}`);
  out.firstQuery = { status: first.status, total: Number(first.total.toFixed(2)), containsMarker: first.text.includes("authenticated") };

  for (let i = 0; i < WARMUP; i++) await q();
  const samples = [];
  for (let i = 0; i < N; i++) samples.push(await q());
  out.runs.push({ name: "authenticated warm query (gateway /xrpc/datomic.q)", ...stats(samples) });

  // 同窓対比: gateway auth check (verify 1 hop 相当)
  const authPath = async () => req(`${API}/api/auth/me`, { headers: { authorization } });
  for (let i = 0; i < WARMUP; i++) await authPath();
  const a = [];
  for (let i = 0; i < N; i++) a.push(await authPath());
  out.runs.push({ name: "gateway auth check (/api/auth/me, Biscuit)", ...stats(a) });
} finally {
  privateKey.fill(0);
}
console.log(JSON.stringify(out, null, 1));
