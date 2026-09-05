import { randomBytes } from "node:crypto";
import { secp256k1 } from "@noble/curves/secp256k1.js";
import { keccak_256 } from "@noble/hashes/sha3.js";

const AUTHN = "https://auth.kotobase.net";
const API = "https://kotobase.net";
const RETURN_TO = "https://kotobase.net/admin";

function hex(b) { return Buffer.from(b).toString("hex"); }
function eip191Digest(message) {
  const payload = Buffer.from(message, "utf8");
  const prefix = Buffer.from(`\x19Ethereum Signed Message:\n${payload.length}`, "utf8");
  return keccak_256(Buffer.concat([prefix, payload]));
}
function jsonHeaders(extra = {}) {
  return { "content-type": "application/json", origin: AUTHN, ...extra };
}
function signatureFor(message, privateKey) {
  const recovered = secp256k1.sign(eip191Digest(message), privateKey, {
    prehash: false, lowS: true, format: "recovered",
  });
  const signature = new Uint8Array(65);
  signature.set(recovered.slice(1), 0);
  signature[64] = 27 + recovered[0];
  return `0x${hex(signature)}`;
}
async function timedFetch(url, init = {}) {
  const started = performance.now();
  const response = await fetch(url, init);
  const text = await response.text();
  const durationMs = performance.now() - started;
  let data;
  try { data = JSON.parse(text); } catch { data = { raw: text.slice(0, 512) }; }
  return { response, data, durationMs,
    colo: response.headers.get("cf-ray")?.split("-").at(-1) || null };
}
function requireStatus(label, result, expected) {
  if (result.response.status !== expected) {
    throw new Error(`${label}: HTTP ${result.response.status} ${JSON.stringify(result.data)}`);
  }
  return result;
}
function cookieFrom(response) {
  const value = response.headers.getSetCookie?.()[0] || response.headers.get("set-cookie");
  if (!value) throw new Error("SIWE verification did not issue a session cookie");
  return value.split(";", 1)[0];
}
function nearestRank(sorted, percentile) {
  return sorted[Math.max(0, Math.ceil(percentile * sorted.length) - 1)];
}
function rounded(value) { return Number(value.toFixed(2)); }

const privateKey = randomBytes(32);
const publicKey = secp256k1.getPublicKey(privateKey, false);
const address = `0x${hex(keccak_256(publicKey.slice(1))).slice(-40)}`;
const runId = `biscuit-query-${Date.now()}`;

try {
  const options = requireStatus("SIWE options",
    await timedFetch(`${AUTHN}/v1/siwe/options`, {
      method: "POST", headers: jsonHeaders(),
      body: JSON.stringify({ address, chain_id: "1", return_to: RETURN_TO }),
    }), 200);
  const signature = signatureFor(options.data.message, privateKey);
  const verification = requireStatus("SIWE verification",
    await timedFetch(`${AUTHN}/v1/siwe/verify`, {
      method: "POST", headers: jsonHeaders(),
      body: JSON.stringify({ nonce: options.data.nonce, signature }),
    }), 200);
  if (verification.data.valid !== true) throw new Error("SIWE did not validate");
  const cookie = cookieFrom(verification.response);

  const created = requireStatus("tenant provision",
    await timedFetch(`${AUTHN}/v1/tenants`, {
      method: "POST", headers: jsonHeaders({ cookie }),
      body: JSON.stringify({ name: `Biscuit query benchmark ${runId}` }),
    }), 201);
  const tenantId = created.data.tenant?.id;
  const tenantDid = created.data.tenant?.did;

  const issued = requireStatus("Biscuit issuance",
    await timedFetch(`${AUTHN}/v1/biscuit/token`, {
      method: "POST", headers: jsonHeaders({ cookie }),
      body: JSON.stringify({ tenantId, dbName: runId, permissions: ["data:read", "data:write"] }),
    }), 201);
  const authorization = issued.data.authorization;
  const graph = issued.data.graph;

  const xrpcHeaders = { "content-type": "application/json", authorization,
    "x-kotobase-tenant-did": tenantDid, "x-kotobase-db-name": runId };

  const queryEdn = `{:find [?e ?value] :where [[?e :bench/run-id "${runId}"] [?e :bench/value ?value]]}`;
  const WARMUP = 3;
  const SAMPLES = 30;
  const latencies = [];
  const kvStatsSeen = [];
  let writeStatus = null;
  let writeUnauthorized = false;

  const txEdn = `[{ :db/id "${runId}" :bench/run-id "${runId}" :bench/value "authenticated" }]`;
  const write = await timedFetch(`${API}/xrpc/ai.gftd.apps.kotobase.datomic.transact`, {
    method: "POST", headers: xrpcHeaders,
    body: JSON.stringify({ db_name: runId, tx_edn: txEdn }),
  });
  writeStatus = write.response.status;
  writeUnauthorized = write.response.status === 401;

  for (let index = 0; index < WARMUP + SAMPLES; index += 1) {
    const q = await timedFetch(`${API}/xrpc/ai.gftd.apps.kotobase.datomic.q`, {
      method: "POST", headers: xrpcHeaders,
      body: JSON.stringify({ graph, db_name: runId, query_edn: queryEdn }),
    });
    if (q.response.status !== 200) {
      throw new Error(`query ${index}: HTTP ${q.response.status} ${JSON.stringify(q.data)}`);
    }
    if (index >= WARMUP) {
      latencies.push(q.durationMs);
      kvStatsSeen.push(q.response.headers.get("x-kotobase-kv-stats"));
    }
  }

  const sorted = [...latencies].sort((a, b) => a - b);
  const output = {
    schema: "kotobase.benchmark.biscuit-auth-query.v1.bench49",
    observedAt: new Date().toISOString(),
    environment: {
      authnUrl: AUTHN, apiUrl: API,
      runtime: `Node ${process.versions.node}`,
      clientRegion: "Tokyo, Japan",
    },
    workload: {
      authentication: "EIP-4361 SIWE with a real secp256k1 EIP-191 signature",
      samplesPerSeries: SAMPLES,
      excludedWarmupsPerSeries: WARMUP,
      database: runId,
      transactStatus: writeStatus,
      transactUnauthorized: writeUnauthorized,
      note: "transact 401 (Unauthorized) は bench 第49回 tick から継続して観測。query path 自体は 200 で成立。write 系 datom 未投入のため query は常時空結果 (rows: []) — warm query latency 測定としては実質 empty-result path となる点に注意。",
    },
    latencyMs: {
      min: rounded(sorted[0]),
      p50: rounded(nearestRank(sorted, 0.5)),
      p95: rounded(nearestRank(sorted, 0.95)),
      p99: rounded(nearestRank(sorted, 0.99)),
      max: rounded(sorted[sorted.length - 1]),
      mean: rounded(sorted.reduce((s, v) => s + v, 0) / sorted.length),
    },
    xKotobaseKvStatsHeaderObserved: kvStatsSeen.filter((v) => v !== null).length,
    xKotobaseKvStatsHeaderValues: [...new Set(kvStatsSeen.filter((v) => v !== null))],
    deployed: kvStatsSeen.some((v) => v !== null && v !== undefined),
    method: {
      percentile: "nearest-rank over successful measured requests",
      concurrency: 1,
      connectionPolicy: "Node fetch connection reuse; no forced cache clear",
      secretsRecorded: false,
    },
  };
  process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
} finally {
  privateKey.fill(0);
}
