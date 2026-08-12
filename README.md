# kotobase-docs

Public documentation for **[kotobase.net](https://kotobase.net)** — a
content-addressed knowledge-graph service built on the
[kotoba](https://github.com/kotoba-lang/kotoba) datom plane.

These are the documents the kotobase.net site links to. They live here because
the service's operational repository is private, and a public site must not
link to pages the public cannot open.

| Document | What it covers |
|---|---|
| [USING-AS-A-PIN-SERVICE.md](USING-AS-A-PIN-SERVICE.md) | Quickstart — auth, pin, retrieve, query, quotas, curl examples |
| [PLANS.md](PLANS.md) | Plan tiers, what each one contractually guarantees, and what is not yet in force |
| [ENTERPRISE-READINESS.md](ENTERPRISE-READINESS.md) | P0 admission gates with current status, including the gates that are **not** met |
| [DATA-HANDLING.md](DATA-HANDLING.md) | Data classes, public boundaries, retention and deletion limits |
| [SUPPLY-CHAIN.md](SUPPLY-CHAIN.md) | Dependency and toolchain release gates, provenance and SBOM |
| [OBSIDIAN.md](OBSIDIAN.md) | Obsidian vault import and conflict-safe two-way sync |
| [terms.md](terms.md) | Terms of service |

## What this repository is not

**It is not the source of truth.** These files are published copies of
documents maintained in the operator's private repository. The private copy
wins on any disagreement.

That is a real cost of publishing this way, and it is stated here rather than
discovered later: **a copy can drift from its original.** Two things bound the
drift:

- `sync-check.cljs` compares every file here against the private original and
  reports differences. It requires access to the private repository, so it is
  an operator tool, not a CI gate you can run.
- Each file is published verbatim except for redactions described below.

## Redactions

`ENTERPRISE-READINESS.md` is published with two redactions, both made in the
same direction — removing an attacker's map, never softening a gap:

- Internal release identifiers (Worker version UUIDs, CI run IDs) are removed.
- Sentences that enumerated exactly which change-control and credential
  protections are currently absent are replaced by a statement that the gate is
  not met. The gate status itself (`Partial` / `Not met`) is unchanged.

No document has had a gap, limitation, or "not met" status removed or weakened.
If you are evaluating kotobase and want the unredacted control detail, ask —
that is what the enterprise evidence bundle is for.

## Reporting problems

- Bugs and feature requests in the datom plane:
  [kotoba-lang/kotobase](https://github.com/kotoba-lang/kotobase/issues)
- Security vulnerabilities: **do not open a public issue** — use
  [private vulnerability reporting](https://github.com/kotoba-lang/kotobase/security/advisories/new)
  or email `root@junkawasaki.com` with `[security]` in the subject.
- Errors in these documents: open an issue here.

## Licence

Apache-2.0. See [LICENSE](LICENSE).

## Repository ownership

This repository is owned by the GitHub organization `net-kotobase` as `net-kotobase/docs`. Reusable language and storage contracts remain in `kotoba-lang`.