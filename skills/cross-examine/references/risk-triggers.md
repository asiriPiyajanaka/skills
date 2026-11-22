# Conditional risk triggers — questions, not legal verdicts

Use only triggers relevant to the product. These are interview prompts; verify jurisdiction-specific legal and platform obligations separately.

| Signal | Drill-down questions | Research/audit handoff |
|---|---|---|
| Children or mixed-age audience | Who is the actual user/data subject? What ages? What parental authority? What SDKs and ads are used? | Children's privacy rules, age-specific store requirements, parental consent processes |
| AI features and external inference | Which exact inputs and outputs? Personal or confidential data? Training/retention terms? Moderation? Human review? | Provider terms, AI-specific applicability, data-transfer responsibilities, unsafe output mitigations |
| Finance, banking, budgeting | Read-only display or move/store money? Bank connections? SMS/notification access? Financial advice or credit? | Actual financial-regulatory classification, permission policy, sensitive data access |
| Health and wellness | Medical advice or tracking? Diagnosis/treatment? Medical records? Urgent harm scenarios? | Medical device classification, health-data safeguards, clinical evidence and review |
| Biometrics and identity | Face/voice templates? Authentication versus recognition? Can users opt out? | Biometrics obligations, platform biometric permissions, retention and transfer |
| Location and sensors | Precise/background location? Other people tracked? Device identifiers? | Platform permission policy, tracking disclosures, minimization |
| Subscriptions, payments and ads | Who pays? In-app digital goods? Trials and cancellation? Targeted ads? | App store billing, consumer law, payment-processing scope and disclosures |
| User-generated or copyrighted content | Upload, share, remix or generate? Report/remove? Licenses for inputs and outputs? | Moderation and content rights, service-provider duties, open-source/asset licenses |
| B2B multi-tenant SaaS | Tenant-scoped authorization? Admin privileges? Staff privacy? Shared documents? | Object-level authorization verification, contractual/data-processing roles |
| Cross-border data and vendors | Who receives which data? Where do they process/store? Backup and subprocessors? | Transfer obligations, vendor agreements, current processing terms |
| Privacy rights and deletion | What is retained in backups/logs? Deletion/portability/access? How verified? | Applicable rights, operational capabilities, retention obligations |
| High-impact automated decisions | Employment, education, credit, insurance, safety? Human review? Explainability? | Relevant sector rules, potential automated-decision protections |
| Accessibility or vulnerable populations | Who may be excluded or harmed? Are accommodations practical? | Accessibility requirements and best practices by context |

## Anti-overreach examples

- A parent-owned account does not prove that child-related data is absent.
- A budgeting app does not automatically require a bank license; ask whether it offers regulated activities.
- PCI DSS does not automatically apply to an app simply because users can see financial figures.
- A global website is not automatically subject to every country's laws; determine actual legal connections.
- A payment processor or auth vendor does not independently prove the product's obligations are satisfied.
- A missing privacy policy does not, by itself, establish the existence or severity of every privacy violation.
