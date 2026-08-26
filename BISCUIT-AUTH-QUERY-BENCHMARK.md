# Biscuit-authenticated query benchmark

Observed 2026-08-26 from Tokyo against the production `auth.kotobase.net` and `kotobase.net` services.

The verified vertical slice was:

1. create an ephemeral secp256k1 EOA;
2. sign the server-issued EIP-4361 message using EIP-191;
3. verify SIWE and create a tenant;
4. issue a 15-minute Biscuit v3 scoped to the tenant's canonical graph CID and `data:read`/`data:write`;
5. verify the Biscuit directly and through the public Gateway;
6. transact three datoms through the public Gateway;
7. query through the same authenticated route and verify the inserted marker.

All correctness gates passed: SIWE valid, Biscuit issued and verified, transaction HTTP 200, query HTTP 200, and marker read back.

| Production series | Success | min | p50 | p95 | p99 | max | mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Biscuit issuance | 30/30 | 32.62 ms | 39.49 ms | 116.65 ms | 169.76 ms | 169.76 ms | 56.75 ms |
| Biscuit verification | 30/30 | 14.38 ms | 18.65 ms | 96.65 ms | 100.19 ms | 100.19 ms | 26.31 ms |
| Authenticated warm query | 30/30 | 132.47 ms | 187.35 ms | 219.51 ms | 220.61 ms | 220.61 ms | 174.81 ms |

First observed timings were 214.22 ms for SIWE options, 425.27 ms for SIWE verification and session issuance, 1,574.86 ms for the authenticated write, and 332.46 ms for its immediate authenticated query read-back.

Method: 30 measured sequential requests per series after three excluded warmups; nearest-rank percentiles; Node fetch connection reuse; NRT Cloudflare colo; no forced cache clear. No key, cookie, token, signature, or tenant content was recorded.

Limitations: this is a single-client production edge-latency sample, not a throughput or capacity claim. The query is a small two-pattern Datalog point selection, not an LDBC traversal. Network and edge latency are included, and “first observed” is not claimed to be a controlled cold-cache measurement.

The private operational repository contains the reproducible harness and machine-readable evidence. The public result intentionally excludes ephemeral account and tenant identifiers as well as every credential.
