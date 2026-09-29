# Identity resolution

Covers check S10 (identity resolution ruleset run, Unified Individual created).

## Steps

1. Comes after Data 360 is enabled and CRM/other data streams exist — there must be Individual records to resolve. Third and last Basic Settings step. [AB:identity-resolution-mcn]
2. Setup > Assistant Home > Basic Settings > bottom of page, "Set Up Identity Resolution" — if no ruleset can be auto-generated, click **Manually Create One**. [AB:identity-resolution-mcn]
3. Identity Resolution page > New > "Create a New Ruleset". Select Data Space "Default", Data Model Object "Individual", add a reference number. Name and describe, Save. [AB:identity-resolution-mcn] [AB:setup-d360]
4. Configure Match Rules. Two documented patterns:
   - **Normalised Email**: DMO "Contact Point Email", field "Email Address", Match Method "Exact Normalised" (case-insensitive exact match). [AB:identity-resolution-mcn]
   - **Fuzzy Name and Normalized Email**: a combined matching rule offered directly in the standard wizard. [AB:setup-d360]
   - **Lead to Contact**: DMO "Identity Match", field "Identity Match Type", Match Method "Exact" > Advanced Settings > set Identity Match Type value to "lead-to-contact". [AB:identity-resolution-mcn]
   - **MC Subscriber Key** (for MCE-sourced individuals): Party Identification > Identification Number > Exact; Party Identification Type = Person Identifier; Party Identification Name = MC Subscriber Key. See `14_mce_connector.md`. [AB:party-id-d360]
5. Save the Matching Rules, click Save, then **Run the Ruleset**. [AB:identity-resolution-mcn]
6. "Run jobs automatically" is enabled by default in the standard wizard (ongoing schedule), not just a one-time run. [AB:setup-d360]
7. Review the result: a **Consolidation Rate** is reported (percentage of individuals unified). Example run: 4%. [AB:identity-resolution-mcn]
8. Back in Basic Settings, the Unified Individual DMO to be used by MC Next is now listed by name.
9. STO (Einstein Send Time Optimization) and other Einstein features have identity resolution as an explicit prerequisite on the Individual DMO — see `19_einstein.md`.

## Limits

- No numeric cap given for number of match rules or ruleset run time.
- Example Consolidation Rate observed: 4% (illustrative, not a target or limit).

## Gotchas

- **Auto-generation of the ruleset is not always available.** One implementation states "we don't have the possibility to automatically generate one" — manual creation may be required even on a fresh org. [AB:identity-resolution-mcn]
- [FIELD] **in a live org, Basic Settings did offer "Generate Ruleset" and it was used**. Do not assume manual build is always required — check what the org's Basic Settings page actually offers before planning a manual build.
- **The Unified Individual DMO name is NOT a fixed/predictable string.** One implementation produced `UnifiedssotIndividual888__dlm`, not a standard `ssot__UnifiedIndividual__dlm`. [AB:identity-resolution-mcn]
- [FIELD] in a live org the DMO is `UnifiedssotIndividual<ruleset id>__dlm`, hidden in the DMO catalogue UI, confirming the naming pattern is `UnifiedssotIndividual<ruleset id>__dlm` and is genuinely org-specific — read it from Basic Settings or the ruleset's own output, never hardcode a name.
- Any automated check assuming a fixed DMO name (e.g. this skill's own S10 check text suggesting `ssot__UnifiedIndividual__dlm` as a guess) is contradicted by direct evidence. See `91_contradictions.md`.

## Automation route

- UI-only for ruleset creation and running, across every article in this KB.
- (inferred) Once created, the resulting DMO is queryable via Data 360 SQL/REST — no article gives a direct API for creating or running the ruleset itself.

## Verification

- The Basic Settings page lists the exact Unified Individual DMO name after a successful run — read that name, then query row counts on it.
- The ruleset detail page shows the Consolidation Rate as the run's success indicator.
- Data Streams / Identity Resolution page shows Consolidation Rate, Known Unified Profiles, Anonymous Unified Profiles after save. [AB:setup-d360]
- [FIELD] `d360_data_graph_get` and SQL queries against `UnifiedssotIndividual<ruleset id>__dlm` confirm the ruleset ran and produced the Unified Individual DMO in a live org. Use the Graph **API name**, not the display name, with `d360_data_graph_get`.

## Sources

[AB:identity-resolution-mcn] How to Configure Identity Resolution Rulesets in Marketing Cloud Next
[AB:setup-d360] How to set-up Data 360
[AB:party-id-d360] Understanding Party identification in Data 360 for Marketing Cloud Engagement
[FIELD] observed directly in a live implementation
