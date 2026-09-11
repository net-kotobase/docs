# kotobase.net Supply Chain

This document defines the current supply-chain baseline for the Worker control
plane. It is a release gate, not a complete third-party risk program.

## Toolchain

- Node is pinned by `.nvmrc` to `24`.
- `kotobase-api-gateway/package.json` requires `engines.node: >=24 <27`.
- `kotobase-api-gateway/package.json` pins `packageManager: pnpm@10.24.0`.
- Repository metadata checks are Babashka-based and run with `bb`.
- Murakumo Mac mini fleet images should use Node 24, pnpm 10.24.0, and
  Babashka `bb` 1.12.x.

## Dependency Policy

- `kotobase-api-gateway/pnpm-lock.yaml` is committed and must remain lockfile version `9.0`.
- Package integrity hashes must remain present in the lockfile.
- Worker dependencies must use npm registry ranges or exact versions only.
- Git, GitHub, URL, `file:`, `link:`, and workspace dependency sources are not
  allowed in `kotobase-api-gateway/package.json`.
- Wrangler and `@cloudflare/workers-types` are exact-pinned because they control
  deploy behavior and Worker runtime types.

## Automated Checks

Run before release:

```sh
scripts/murakumo-worker-check.cljc release-strict
```

For local debugging, the same checks are available from `kotobase-api-gateway/` as individual
`pnpm` scripts.

`pnpm supply:check` verifies package privacy, `UNLICENSED` package metadata,
Node/pnpm pins, exact Cloudflare toolchain pins, lockfile integrity metadata,
dependency source policy, the full package script manifest, explicit deploy/build scripts, Worker environment contract,
the Murakumo verification entrypoint, governance-doc and authoritative
ClojureScript workflow path coverage,
release-target drift between Wrangler config, public smoke, and release evidence,
Dependabot grouping, GitHub mirror coverage, and GitHub workflow
permissions/concurrency/timeout boundaries. GitHub Actions are advisory mirrors, not release authorities:
heavy verification runs on Murakumo through
`scripts/murakumo-worker-check.cljc release-strict` and
`scripts/murakumo-worker-check.cljc deploy-ready`. The Worker workflow rebuilds
the deployable ClojureScript, rejects generated-artifact drift, and mirrors
metadata/script syntax checks; the broader release authority remains Murakumo.
Worker, metadata, and
public-smoke workflows stay read-only; CodeQL is the only workflow allowed to write
`security-events`. Root `LICENSE`, `CHANGELOG.md`, repository-format files,
GitHub governance metadata, `.gitignore`, and `.nvmrc` changes are included in
the Worker and metadata workflow path filters so licensing-boundary,
release-history, repository-format, review-template, artifact-ignore, and
Node-toolchain changes run the gates.

The scheduled public-smoke workflow runs every 30 minutes and must call
`pnpm smoke:public` with `KOTOBASE_PUBLIC_SMOKE_REQUIRE_EDGE_HEADERS=1`; the
metadata gate rejects drift from that strict smoke posture.
For workflows that define both `push.paths` and `pull_request.paths`, the
metadata gate requires the two path-filter lists to stay identical.
GitHub workflow jobs run on `ubuntu-24.04`; `ubuntu-latest` is not used for
release gates. Workflow job IDs are fixed (`check`, `smoke`, and `analyze`) so
audit references stay stable. Workflow step names and order are also fixed by
the metadata gate.
Workflow `uses:` actions are allowlisted by exact major/minor tag so checkout,
Node setup, pnpm setup for public smoke, Babashka setup, and CodeQL action drift
is caught before release. Checkout steps must set `fetch-depth: 1`. Checkout steps must set `persist-credentials: false`. Checkout steps must set `submodules: false`.
The same metadata gate fixes setup inputs: Node 24, pnpm 10.24.0 with
`run_install: false` for public smoke, `kotobase-api-gateway/pnpm-lock.yaml` cache dependency
path for public smoke, and Babashka `bb` 1.12.218. Workflows with `run:` steps must use
`defaults.run.shell: bash`; Worker and public-smoke run steps must execute from
`kotobase-api-gateway/`. Workflow and job-level `env` are forbidden; step-level `env` is
allowlisted to the public-smoke strict edge-header flag. Workflows must not
expose `GITHUB_TOKEN`, `GH_TOKEN`, or `github.token`. The sole `secrets.*`
exception is the main-only `edge.yml` production-environment deploy step:
exactly `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`, after Sigstore
provenance/SBOM verification. Metadata CI rejects either secret anywhere else
or any additional secret reference.
Workflows must not use `pull_request_target`, `workflow_run`, or
`repository_dispatch` triggers.

`pnpm sbom` prints a local SBOM-lite JSON dependency inventory derived from
`kotobase-api-gateway/package.json` and `kotobase-api-gateway/pnpm-lock.yaml`. `pnpm sbom -- --check`
validates that direct dependencies, lockfile version, integrity metadata, fixed
root/source/project key order, ISO UTC generation timestamps that round-trip
exactly, stable unique
direct-dependency ordering, direct dependency key order/scopes/specifiers, stable
unique component order, component key order, component package URLs, fixed
explanatory notes, and sha512 lockfile integrity values are represented without
reading operator secrets. Direct dependency specifiers in SBOM-lite output must
be printable single-line registry version ranges. `pnpm sbom -- --check`
recursively rejects unsafe SBOM fields such as `Authorization`, cookie headers,
operator secret var names, bearer/CACAO/JWT-like values, and
private-CID-like values. Only the exact `notes` array is exempt from
secret-like value scanning so fixed explanatory notes can mention the no-secret
boundary.

`pnpm license:check` verifies direct Worker dependency licenses against
`docs/DEPENDENCY-LICENSES.md`. New direct dependencies with GPL, AGPL, LGPL,
SSPL, BUSL, proprietary, unknown, or missing licenses require owner review and
an ADR before release. The Worker mirror only syntax-checks
`kbb scripts/license-check.cljk --syntax-check`; the full license gate runs on
Murakumo.

`pnpm contract:check` verifies that the documented public HTTP route contract,
user-facing guide, and agent docs stay aligned with `kotobase-api-gateway/src/app.cljc`.
Root metadata checks reject stale `app.cljc:<line>` references in docs and release
metadata; public route and control-plane decisions should cite route names or
function names instead of source line numbers.

Worker test harnesses are also part of the supply-chain boundary. Metadata
checks currently allow exactly `kotobase-api-gateway/test/archive_response_boundary_test.cljc`,
`kotobase-api-gateway/test/auth_fallback_test.cljc`,
`kotobase-api-gateway/test/b2_list_boundary_test.cljc`,
`kotobase-api-gateway/test/cacao_time_test.cljc`, `kotobase-api-gateway/test/did_document_test.cljc`,
`kotobase-api-gateway/test/error_boundary_test.cljc`, `kotobase-api-gateway/test/json_boundary_test.cljc`,
`kotobase-api-gateway/test/realtime_control_test.cljc`, `kotobase-api-gateway/test/realtime_test.cljc`,
`kotobase-api-gateway/test/size_hint_test.cljc`,
`kotobase-api-gateway/test/xrpc_input_boundary_test.cljc`, and the
Babashka-owned `kotobase-api-gateway/test/pin_test.cljc` Worker pin harness, and release evidence requires
every `kotobase-api-gateway/test/*.cljc` file to appear in the SHA-256 source manifest. Worker
test `.mjs` files are forbidden rather than accepted as manifestable test
harnesses. The metadata self-test
`KOTOBASE_METADATA_SELF_TEST_WORKER_TEST_ALLOWLIST=1` injects an extra test
harness and must fail closed. The metadata self-test
`KOTOBASE_METADATA_SELF_TEST_STALE_WORKER_TEST_EVIDENCE=1` injects the old
`21 pin/realtime tests` evidence wording and must fail so `deps.toml` cannot
silently lag behind the current archive response boundary, auth fallback, B2 list boundary, CACAO time, DID document, error boundary, JSON body boundary,
realtime control, realtime, size hint, XRPC input boundary, and pin harness suite.
The release evidence self-tests inject an unmanifested
Worker test `.cljc` file and a forbidden Worker test `.mjs` file; the former must
fail with `evidence Worker test missing from source manifest` and the latter
must fail before manifesting. Root Babashka entrypoints under `scripts/*.cljc`
are also enumerated dynamically; the
`KOTOBASE_RELEASE_EVIDENCE_SELF_TEST_UNMANIFESTED_ROOT_BB=1` self-test injects
a synthetic root script and must fail with
`evidence root Babashka script missing from source manifest`. Duplicate source
manifest and required-doc entries are self-tested with
`KOTOBASE_RELEASE_EVIDENCE_SELF_TEST_DUPLICATE_SOURCE_PATH=1` and
`KOTOBASE_RELEASE_EVIDENCE_SELF_TEST_DUPLICATE_REQUIRED_DOC=1`, and must fail
before evidence can be accepted.

`pnpm examples:check` verifies that public curl/IPFS examples use safe
placeholders, refer only to documented routes, and stay aligned with agent docs
and public-smoke no-write boundaries. The Worker mirror only syntax-checks
`kbb scripts/examples-check.cljk --syntax-check`; the full examples gate runs on
Murakumo.

`pnpm site:check` verifies that the embedded landing page, `llms.txt`,
`llms-full.txt`, DID document branch, public smoke, and user-facing docs stay
aligned on the canonical `kotobase.net` identity, `did:web:kotobase.net`, and
the legacy `kotobase.gftd.ai` alias. The Worker mirror only syntax-checks
`kbb scripts/site-check.cljk --syntax-check`; the full site gate runs on Murakumo.

`pnpm api-compat:check` verifies that API versioning, deprecation,
breaking-change, legacy alias, migration-note, examples, public smoke, PR
review, and release evidence rules stay aligned. The Worker mirror only checks
`kbb scripts/api-compat-check.cljk --syntax-check`; the full API compatibility gate runs
on Murakumo through `pnpm check:quick` and `pnpm check:release`.

`pnpm submodule:check` verifies the `kotoba/` submodule URL and gitlink
provenance, tolerates uninitialized checkouts, and reports initialized checkout
HEAD/dirty counts in release evidence. `pnpm submodule:check --require-clean`
fails closed when an initialized `kotoba/` checkout has local changes, without
initializing the submodule. Submodule provenance is tracked by gitlink; upstream
source is not silently vendored into the Worker bundle.
The Worker mirror only syntax-checks `kbb scripts/submodule-check.cljk --syntax-check`;
the full submodule gate runs on Murakumo.

`pnpm security:check` verifies that the threat model, auth boundaries, public
metadata limits, secret handling, edge-header posture, unit tests, public smoke,
CodeQL, and GitHub mirror wiring stay aligned.

`pnpm observability:check` verifies that request-id echo, safe runtime metadata,
strict-smoke correlation, runbook/service-level references, and the no-raw-error
logging boundary stay aligned.
The Worker mirror only syntax-checks `kbb scripts/observability-check.cljk --syntax-check`;
the full observability gate runs on Murakumo.

`pnpm recovery:check` verifies that rollback drills, B2 metadata audit drills,
cleanup safeguards, data-handling boundaries, release evidence, and Murakumo
release gates stay aligned. The Worker mirror only syntax-checks
`kbb scripts/recovery-check.cljk --syntax-check`; the full recovery gate runs on
Murakumo.

`pnpm runbook:check` verifies that operational runbook procedures, service-level
thresholds, Murakumo release verification, public smoke coverage, GitHub mirrors,
and package scripts stay aligned.

`pnpm predeploy:check` verifies deploy target posture before an operator runs
Wrangler deploy or rollback commands: production stays on explicit `--env=""`,
B2 staging stays on explicit `--env b2`, routes and workers.dev posture match
the environment contract, observability remains enabled, Durable Object bindings
are present, and operator secret values are not committed.
The Worker mirror only syntax-checks `kbb scripts/predeploy-check.cljk --syntax-check`;
the full predeploy posture gate runs on Murakumo.

`pnpm check:quick` runs whitespace checks, metadata checks, ops-script checks,
examples checks, API compatibility checks, submodule provenance checks,
site identity checks, predeploy posture checks, runbook checks, observability checks,
recovery checks, license checks, API contract checks,
security checks, `pnpm audit`, `pnpm supply:check`, SBOM-lite checks, release
evidence checks, unit tests, and typecheck without dry-run deploys or public
network smoke.

`pnpm check:release` runs examples checks, site identity checks, API
compatibility checks, submodule provenance checks, predeploy posture checks, runbook
checks, observability checks, recovery checks, API contract checks, security
checks, license checks, `pnpm audit`, `pnpm supply:check`,
SBOM-lite checks, release evidence checks, unit tests, typecheck, dry-run builds
for production and B2 staging, and public smoke.
The release gate removes `kotobase-api-gateway/dist` and `kotobase-api-gateway/dist-b2` before dry-run
builds, on normal exit, and on SIGINT/SIGTERM interruption.
`scripts/murakumo-worker-check.cljc` also removes those dry-run artifact
directories before release/release-strict/deploy-ready modes and from its JVM
shutdown hook, so fleet interruptions do not leave stale deploy bundles behind.
`KOTOBASE_RELEASE_CHECK_SKIP_PUBLIC_SMOKE=1` is a local debugging escape hatch,
not a deploy-ready substitute; it requires
`KOTOBASE_RELEASE_CHECK_SKIP_PUBLIC_SMOKE_REASON` so skipped public smoke leaves
an auditable reason. The reason must be printable single-line text, must be a single line with 12 to 200 characters, and must not include secret-like values such as token assignments or Bearer credentials.
`release-check --syntax-check` and `supply:check` also mirror the release gate
ordering so whitespace, metadata, ops, supply, evidence, tests, typecheck,
dry-run builds, and public smoke cannot silently move ahead of their
prerequisites.
The metadata portion also checks local Markdown links so release docs and ADR
references cannot silently rot.
Data-handling documentation is kept in the release-doc set because stored
fields, public metadata, and diagnostics affect the deployable trust boundary.
Release-evidence documentation is kept in the same set so deploy proof remains
sanitized and reproducible.

GitHub CodeQL runs JavaScript/TypeScript security analysis for Worker changes
and on a weekly schedule using `security-extended` queries. CodeQL findings are
uploaded through `security-events`. This is advisory visibility; Murakumo
`release-strict` remains the release verification command, and Murakumo
`deploy-ready` is the clean-worktree gate for actual deploy candidates.

Committed JS/MJS/TS is treated as generated or adapter mechanism, never as the
semantic authority. From `kotobase-api-gateway-cljs`, `kbb -M:render-components` derives the
tracked provider-source inventory from Git, records each file's role,
language, provider, byte count and SHA-256, and refreshes the two committed
Worker bundle digests. `kbb -M:test` fails when a tracked provider file is
uncataloged, a cataloged file drifts, or either Worker ESM no longer matches
its checked artifact record. The Worker workflow additionally rebuilds both
bundles from the authoritative ClojureScript and regenerates the catalog; CI
fails if any rebuilt byte or recorded digest differs from the reviewed commit.
The signed release job repeats that rebuild-and-compare step before packaging,
so a stale committed bundle cannot become a signed production artifact merely
because its own stale digest was cataloged consistently. See ADR-2607262100.

## Update Process

- Dependabot opens weekly grouped PRs for Worker npm dependencies and GitHub
  Actions metadata updates.
- Dependency PRs must pass `scripts/murakumo-worker-check.cljc release-strict` on
  the Murakumo fleet. Deploy-affecting dependency PRs must pass
  `scripts/murakumo-worker-check.cljc deploy-ready` before deploy.
- Deploy-affecting dependency updates must record the deployed Worker version ID
  in `deps.toml`, `CHANGELOG.md`, and the relevant ADR after deploy.
- Security fixes should follow `SECURITY.md`; exploitable findings and secret
  exposure stay out of public issues.

## Current Limits

- `pnpm sbom` is the main Worker's local dependency inventory. Main-branch CI
  additionally emits immutable CycloneDX SBOM and SLSA provenance attestations
  for `kotobase-api-gateway`, Authn, protocols Worker and `kotobase-graph-database`, signed
  keylessly with the individual GitHub workflow identity.
- `protocols-worker/upstream-lock.json` pins every sibling source path to an
  exact Git revision. CI rejects source/lock set drift, floating default-branch
  clones, wrong remotes, dirty tracked files and any HEAD that differs from the
  lock before compiling the query gateway or multilingual Gremlin conformance.
- Cloudflare deploy provenance is tracked by the signed artifact digest and
  workflow identity as well as Worker version IDs, release-check output,
  sanitized `pnpm evidence` JSON, `CHANGELOG.md`, `deps.toml`, and ADR updates.
- The production workflows verify the artifact digest, SBOM, provenance and
  exact main-branch builder identity before invoking Wrangler. CI-only deploy
  remains unavailable until least-privilege Cloudflare credentials are placed
  in the protected `production` environment; broad local OAuth credentials are
  not acceptable substitutes for those secrets.
- The Murakumo/Babashka release-gate decision is recorded in
  `docs/adr/2606110004-murakumo-babashka-release-gate.md`.
- The `kotoba` submodule is upstream source, not vendored Worker dependency
  code, and its Apache-2.0 license does not license the root repository. See
  `docs/LICENSING.md` and `docs/SUBMODULES.md`.
