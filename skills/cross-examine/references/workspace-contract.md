# Discovery workspace contract v1.0.0

The authoritative contract is `../assets/workspace.schema.json` (relative to this file) and the sample is `../assets/workspace.template.json`.

## Storage

Inside each product repository, keep `.product-assurance/workspace.json` under version control **only after checking that it contains no secrets or raw personal information**. Use safe summaries instead of raw interviews or production user records. Separate sensitive evidence storage is a future concern, not implemented here.

## Keys and stable IDs

- `project`: product description, development stage, product types, business model. An empty product type list means not yet classified.
- `distribution`: business location, target markets and markets where access is possible **separately**. Empty arrays mean not yet recorded, not "none".
- `actors` (`ACT-0001`): user, account holder, payer, admin, child, bystander, consent authority as appropriate. More than one role per real-world person is allowed; model separate actors only when the distinction matters.
- `features` (`FEAT-0001`): implemented/planned product capabilities and affected actors.
- `data_categories` (`DATA-0001`): conceptual classes of information, **not** individual records; link to data subjects and retention/deletion statements.
- `data_flows` (`FLOW-0001`): information movement across systems/vendors. "unknown" cross-border is a legitimate value.
- `third_parties` (`VEND-0001`): processors, platforms, vendors, analytics, payment providers and AI systems that receive product information.
- `jurisdictions` (`JUR-0001`): *candidate applicability* reasoning; `applicable_verified` and `not_applicable_verified` require later, cited rule research.
- `claims` (`CLM-0001`): assertions such as "no data used for model training". `verification` is `unverified`, `partially_verified`, `verified`, or `contradicted` and must not be inflated.
- `unknowns` (`UNK-0001`): open research questions or evidence gaps, prioritized with explicit next action.
- `risk_signals` (`SIG-0001`): triggers that may require investigation. These are **not** legal findings.
- `interview` (`Q-0001`): sanitized question summaries and domain coverage to resume after context loss.

Never recycle an ID. Keep cross-entity references accurate; validate after structural changes. If you discover a fact has changed, update the source/confidence and preserve material decision context in question history.

## Verified versus reported

`source` indicates origin, not truth. A `repository_observed` item is directly seen in code but is **not necessarily** observed in the deployed system. `confidence: observed` describes evidence of the stated behavior. `verified` requires stronger tests/documentation appropriate to the claim; do not assume tests pass without running them. In this phase, `claims[].evidence_refs` are external future-evidence keys: do not invent them and don't mark claims verified until evidence is reviewed.

## Future handoffs

`rule-hunter` will consume jurisdictions, product behavior and signals to create *cited* requirement records separately. `prove-it` will consume features, flows, vendors and claims to assess code, vendor documents and operations. Future skills must not rewrite discovery facts to make their own findings pass. Release gates and their evidence belong in a separate, versioned contract to be designed before `ship-or-stop` exists.

## Out-of-scope for v0.1

This workspace is not a legal register, production data inventory, security attestation, consent management system, or incident platform. Its job is to capture what should be researched and verified.
