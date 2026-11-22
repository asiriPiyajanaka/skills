# Discovery workspace contract v2.0.0

The authoritative contract is the [workspace schema](../assets/workspace.schema.json), with an [initial template](../assets/workspace.template.json).

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

Never recycle an ID or renumber a saved workspace. Allocate above the highest number already present or referenced in history for that entity type. Keep referenced records, including contradicted claims, so history stays resolvable. If a fact changes, retain the earlier claim and explanation in history, record the new observation separately where the distinction matters, and update confidence without replacing its original provenance. Update `interview.last_updated` after substantive answers. Validation checks uniqueness and reference integrity within the current snapshot; it cannot prove that an agent preserved every prior version.

## Verified versus reported

`source` indicates origin, not truth. A `repository_observed` item is directly seen in code but is **not necessarily** observed in the deployed system. `confidence: observed` describes evidence of the stated behavior. A claim can keep `source: developer_reported` after independent verification; changing confidence must not erase who originally asserted it.

Actors, features, data categories, flows, vendors and jurisdictions may include `evidence_refs` and `verification_notes`. `confidence: verified` requires a nonempty evidence list and substantive verification notes. Verified jurisdiction applicability additionally requires verified confidence and a rationale. Claim statuses `partially_verified`, `verified` and `contradicted` require nonempty `evidence_refs` and substantive `notes` explaining the support or contradiction.

References must identify evidence actually reviewed: a repository path with a relevant location/revision, a reviewed document URL, a reproducible test artifact, or an existing key in a real external evidence store. Never invent placeholder evidence IDs. Do not add raw sensitive evidence to this workspace. Validation checks that references and notes are present; it does not fetch sources, resolve external keys, run tests or establish that the evidence proves the statement. A vendor's assertion alone is not independent verification. Leave the record reported/observed or the claim unverified when stronger support is unavailable.

## Completion and unknowns

Every domain labelled `sufficient` or `not_applicable` requires a reason, even during an unfinished interview. Open unknowns require an impact, owner and next action; use a role or `unassigned — identify owner` when an owner is not yet known.

`discovery_complete` requires all 12 domains, a substantive product name and summary, product types, actors, actor-linked features, distribution platforms/channels, question history and an update timestamp. Recorded data categories require recorded flows. An empty data inventory requires an explicit explanation in its coverage reason; do not treat an empty array as evidence of no processing. Unresolved research tasks can remain after discovery if their consequences and follow-up are explicit. `blocked_on_unknown` domains keep the interview `in_progress` or `paused`.

These are minimum recording checks. The interviewer must still assess whether the answers meaningfully characterize the product. A structurally valid workspace is not proof of completeness, compliance or readiness.

## Migrating v1 workspaces

Version 2 adds optional evidence provenance fields and enforces the completion, coverage-reason and evidence requirements above. Existing v1 files require an explicit migration; validation never rewrites them.

With the installed skill's validation environment, run:

```bash
python /path/to/cross-examine/scripts/workspace.py migrate \
  --workspace .product-assurance/workspace.json \
  --output .product-assurance/workspace.v2.json
python /path/to/cross-examine/scripts/workspace.py validate \
  --workspace .product-assurance/workspace.v2.json
```

The command refuses an existing output, preserves the source byte-for-byte, and writes a candidate with the new version while preserving the other records and IDs. If old records fail the stricter rules, it returns 1 and explains the repairs needed in the candidate. Do not fabricate evidence, clear history or silently downgrade statuses to make migration pass. Reconcile unsupported statuses with the user, record the reason, validate again and review the diff before replacing the original file.

## Future handoffs

`rule-hunter` will consume jurisdictions, product behavior and signals to create *cited* requirement records separately. `prove-it` will consume features, flows, vendors and claims to assess code, vendor documents and operations. Future skills must not rewrite discovery facts to make their own findings pass. Release gates and their evidence belong in a separate, versioned contract to be designed before `ship-or-stop` exists.

## Outside the discovery contract

This workspace is not a legal register, production data inventory, security attestation, consent management system, or incident platform. Its job is to capture what should be researched and verified.
