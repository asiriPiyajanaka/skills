# Product Assurance Skills roadmap

## Implemented in v0.1.0

1. **cross-examine** — adaptive question-driven discovery and risk hypothesis generation.
2. **Shared discovery contract v1** — validated JSON profile with actors, markets, features, data, flows, vendors, claims, risk signals and unknowns.
3. **Three synthetic scenario fixtures** and structural tests.

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

1. Build deterministic discovery interview evaluations across the children, finance and SaaS fixtures (including adversarial answers and contradictions).
2. Refine interview state transitions and stable ID reconciliation based on actual Codex/Claude/Cursor runs.
3. Design `rule-hunter` requirement/evidence contract: effective dates, sources, legal versus platform policies, verified applicability, counter-evidence and review dates.
4. Add a separate, approval-protected evidence and findings ledger before building release gates.
5. Support project-private and encrypted evidence references; never store production personal data in the discovery JSON.

## Versioning expectations

Contract `schema_version` is `1.0.0`. Breaking changes require an explicit migration. New skills consume and append their own records rather than silently changing developer facts. Every read/modify/write step should validate afterward and preserve git diffs.
