# Product Assurance Skills roadmap

## Implemented in the current starter

1. **cross-examine** — adaptive question-driven discovery and risk hypothesis generation.
2. **Discovery contract v2** — validated JSON profile with actors, markets, features, data, flows, vendors, claims, risk signals and unknowns; explicit evidence provenance and minimum completion records.
3. **Four synthetic scenario fixtures** and structural/regression tests, including a completed discovery profile and cases for contradictions, resumption, missing dependencies and invalid inputs.
4. **Explicit v1 migration** — writes a reviewable v2 candidate without overwriting the source or fabricating evidence.
5. **Repository validation and CI** — Python 3.10/3.14 test matrix, temporary-project installs, detached runtime checks, and anonymous public-commit installation after default-branch pushes.

## Planned; not implemented

| Skill | Input contract | Expected outputs | Guardrail |
|---|---|---|---|
| `rule-hunter` | Discovery facts and candidate jurisdictions | Time-stamped sources, applicability decisions, obligations and exclusions | Do not assume applicable law from geolocation alone |
| `prove-it` | Features, claims, flows and researched obligations | Code/data-flow findings, vendor document review, reproducible evidence | Do not mark provider statements verified without support |
| `fix-it-right` | Confirmed findings with evidence | Approved change plans, diffs, regression tests | Require explicit approval before editing product code |
| `fine-print` | Verified product behaviors and obligations | Policy drafts, store disclosure drafts, submission instructions | Documentation is not proof of implementation |
| `ship-or-stop` | Findings, evidence and publishing artifacts | Scoped readiness verdict and sign-off record | A compliant-ready assessment is not legal certification |
| `stay-sharp` | Change/incident events and prior evidence | Targeted re-review, reopened findings, operational follow-up | No autonomous monitoring without configured automation |

## Next engineering tasks

1. Execute repeatable agent interview evaluations across the children, finance and SaaS scenarios, including adversarial answers and contradictions; record observed outcomes rather than matching exact wording.
2. Refine interview state transitions and stable ID reconciliation based on actual Codex/Claude/Cursor runs.
3. Design `rule-hunter` requirement/evidence contract: effective dates, sources, legal versus platform policies, verified applicability, counter-evidence and review dates.
4. Add a separate, approval-protected evidence and findings ledger before building release gates.
5. Support project-private and encrypted evidence references; never store production personal data in the discovery JSON.

## Versioning expectations

Contract `schema_version` is `2.0.0`. Version 2 introduces optional fact evidence references/review notes and stricter coverage, verification, unknown-action and completion requirements. Use [the explicit migration procedure](../../skills/cross-examine/references/workspace-contract.md#migrating-v1-workspaces) for existing v1 files. Migration changes the candidate's version while preserving its other records; invalid old states remain visible for repair rather than being silently downgraded.

Breaking changes require an explicit migration. New skills consume and append their own records rather than silently changing developer facts. Every read/modify/write step should validate afterward and preserve reviewable diffs. The full requirement, evidence and findings ledgers for later skills remain to be designed; v2 evidence references are discovery provenance, not those ledgers.
