# Adaptive interview method (cross-examine v0.1)

## Question selection algorithm

1. Establish product intent and core actors. With no product idea, start there.
2. Enumerate features and data flows that create new exposures; distinguish current implementation from planned behavior.
3. Score possible questions qualitatively: **impact of being wrong**, **architectural or legal consequence**, **uncertainty**, and **information gain**. Focus the highest-scoring question first.
4. Ask one plain-language question. Explain the specific decision it informs (one sentence, not a lecture).
5. On response, write sanitized, attributed facts and link evidence; if no evidence exists mark `reported` or `unknown`.
6. If response has "don't know", create one `UNK-####` with next action and stop pressing the same question without new context.
7. Reassess prioritization and repeat. Do not march down topic numbers.

On resumption, read saved history, coverage reasons, unresolved claims and priority unknowns first. Do not repeat answered questions without a concrete change, contradiction or missing detail. Append new history and preserve IDs; a request to stop should produce a paused, scoped handoff rather than another mandatory question.

## Domain coverage

Capture a reason for every domain marked sufficient or not applicable:

- product_and_business — core promise, product lifecycle, monetization, accountability
- actors_and_age — real users versus payers/owners, minors, bystanders, consent roles
- markets_and_distribution — establishment, target and accessible markets, channels, geo restrictions
- features_and_content — functionality, generated/user content, moderation, intellectual property
- data_inventory_and_flows — identifiers, inferred data, data subjects, data origins, onward transfers
- device_permissions_and_tracking — SMS, notifications, microphone, camera, location, advertising identifiers
- ai_and_third_parties — inference, training, subprocessors, model output, hosting jurisdictions
- security_and_access — auth, tenant boundaries, authorization, secrets, abuse prevention
- payments_and_marketing — subscriptions, cancellation, refunds, promotions, analytics and ads
- regulated_activities_and_ip — financial/health/education and other regulated functions, licensing
- retention_rights_and_operations — deletion, access requests, incident response, backups, vendor lifecycle
- accessibility_and_user_harm — disability accommodations, vulnerable people, product misuse/harm

## Stop conditions

`discovery_complete` is **not** a compliance verdict. Set it only when:
- core purpose, users, distribution, feature inventory and material data paths are reasonably characterized;
- all 12 domain coverage items are `sufficient` or justified `not_applicable`, or a clearly documented blocker requires pausing (`blocked_on_unknown` means leave `in_progress` / `paused` instead);
- every high-impact unresolved issue exists in `unknowns` with a next action;
- important third-party and platform assumptions have explicit provenance;
- a new question would no longer materially change the initial research/audit scope.

The core profile must include a substantive name and summary, product types, actual actors, actor-linked features, and distribution platforms/channels. Record material data flows when the inventory contains data, append sanitized question history, and update the timestamp. These minimum checks prevent completion of an empty template by changing coverage flags. A domain can be sufficiently characterized while a clearly scoped research task remains; use `blocked_on_unknown` when the missing answer prevents characterizing the domain itself.

When uncertain, `paused` is better than falsely declaring discovery complete. The user can always choose to end questioning and receive an incomplete handoff.

## Contradictions

If a developer says "no user data leaves the device" but code observation shows a cloud upload:
1. Preserve the original claim in `claims` as `contradicted` only if evidence supports that contradiction (otherwise `unverified`).
2. Record the specific observed flow as `repository_observed` / `observed`, and link it to a research unknown if needed.
3. Explain the discrepancy without accusing the developer; ask which behavior is intended and whether the implementation is current.
4. Do not silently erase earlier answers. Retain question history as an audit trail.
5. A `contradicted` claim needs the reviewed evidence reference and explanatory notes. If the observation only raises doubt, keep the claim `unverified`, record the observation and a reconciliation unknown, and avoid claiming a deployed defect.

## Handoff format

Return these paragraphs or sections in the conversation, and persist equivalent structured data when file access exists:
- Product profile: audience, distribution, key features and commercial model.
- Material processing: data categories and flows, including unknown transfers.
- Candidate jurisdictions: with *rationale*, not legal conclusions.
- Risk signals: clearly labeled conditional hypotheses.
- Priority unknowns: impact and specific next research/evidence action.
- Next workflow: specific tasks for `rule-hunter` and `prove-it`, linked to relevant fact/claim/unknown IDs, with missing inputs and evidence needs. These are handoffs; neither skill is implemented yet.

Never claim "approved for launch" or produce generic legal documents from unverified facts.
