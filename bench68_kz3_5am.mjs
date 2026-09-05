// bench68 — K-Z3 5時台 1セット目 (run185A-C)
// 同測定法: /search?q= n=20 × 3 run + landing control n=20, 別接続 curl, production 実測 (gate 外)
// secret 不含。
import { execSync } from "node:child_process";

function run(url) {
  const out = execSync(
    `curl -s -o /dev/null -w '%{http_code} %{time_starttransfer} %{time_total}' --max-time 15 '${url}'`,
    { encoding: "utf8", shell: "/bin/bash" },
  ).trim();
  const [code, ttfb, total] = out.split(" ").map(Number);
  return { code, ttfb, total };
}

const SEARCH = "https://search.kotobase.net/search?q=bench68kz3";
const LANDING = "https://kotobase.net/";

function summarize(runs, label) {
  const ok = runs.filter((r) => r.code === 200);
  const sorted = ok.map((r) => r.ttfb).sort((a, b) => a - b);
  const cold = ok.filter((r) => r.ttfb >= 0.5);
  const p50 = sorted.length ? sorted[Math.ceil(0.5 * sorted.length) - 1] : null;
  return {
    label, n: runs.length, ok200: ok.length,
    coldCount: cold.length,
    coldValues: cold.map((r) => Math.round(r.ttfb * 1000) + "ms"),
    p50ms: p50 != null ? Math.round(p50 * 1000) : null,
    minMs: sorted.length ? Math.round(sorted[0] * 1000) : null,
    maxMs: sorted.length ? Math.round(sorted[sorted.length - 1] * 1000) : null,
  };
}

const result = { purpose: "bench68 K-Z3 5時台 1セット目 (run185A-C)", observedAt: new Date().toISOString(), runs: [] };
for (let r = 0; r < 3; r += 1) {
  const runs = [];
  for (let i = 0; i < 20; i += 1) runs.push(run(SEARCH));
  result.runs.push(summarize(runs, `run${r + 1} search`));
}
const control = [];
for (let i = 0; i < 20; i += 1) control.push(run(LANDING));
result.control = summarize(control, "landing control");
console.log(JSON.stringify(result, null, 1));
