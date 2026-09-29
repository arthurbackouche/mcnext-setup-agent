# Migration considerations (MCE to MC Next)

Cross-cutting file. Feeds S4, S8, S10, S11, S12 in a migration-specific context. Not a single S-check; this is the "how the migration workstream actually runs" reference.

## Steps

### Strategic sequencing (the 60-day plan — clearest single source for setup order)

1. **Days 1-20 (Foundation)**: Enable Data 360; create Engagement admin user in the core org; create Data Spaces (recommend 1:1 mapping of each MCE Business Unit to one Data Space, starting with one or two BUs tied to the first use case); turn on out-of-the-box Engagement data bundles and map BUs; enable the Marketing app and out-of-the-box analytics dashboards; add marketing users and assign standard Marketing Cloud permission sets; configure and run identity resolution (creates Unified Individual); create a Data Graph; optionally sync one or two key DEs to Data 360 as custom DMOs and create an Activation Template for Flow. Steps 1-6 alone give "a working Next environment"; identity resolution + Data Graph (7-8) unlock Flow decisioning, personalisation and agents — can be deferred if the first use case is reporting-only. [AB:worth-migrating-mcn]
2. **Days 21-40 (Configure one use case)**: open Digital Wallet and Marketing Performance dashboards; connect existing journeys to Campaign records; build a V1 of the chosen use case using only out-of-the-box features. [AB:worth-migrating-mcn]
3. **Days 40-60 (Launch)**: deploy to an internal/small audience, measure, run a feedback session, then move to the next use case. [AB:worth-migrating-mcn]

### Account Engagement (Pardot) historical data — a different product from MCE, same install pattern

4. Data Cloud Setup > Salesforce CRM tab > install the "Marketing – Account Engagement CRM Data" Bundle (Admin only) > Data Cloud > Data Streams > New > Salesforce CRM connector > Bundle "Marketing – Account Engagement CRM" > Deploy. Salesforce Setup > "Data Cloud Integration" > select the Account Engagement Business Unit. Create an Account Engagement Data Stream (type: Email Engagement Data, Form Engagement Data, Web Page Engagement Data, or Custom URL Engagement Data). In Account Engagement: Connectors > edit the Data Cloud Connector > set look-back date **up to 2 years** > activate. [AB:migrate-ae-mcn]
5. This is a **different connector/bundle from the native MCE (Engagement)/ExactTarget connector** (see `14_mce_connector.md`) — do not conflate Account Engagement (Pardot) streams with Marketing Cloud Engagement streams. the client' migration is from MCE, so this specific bundle likely does not apply directly, but the "install bundle > create stream > configure look-back > activate connector" pattern is the closest documented analogy for the MCE connector. [AB:migrate-ae-mcn]

### Claude-assisted MCE-to-Data-360 field mapping

6. Requires both an MCE MCP connector and a Data 360 MCP connector configured. MCE side: Installed Package (server-to-server, API Integration component, read-only scopes on Data Extensions/Data Folders, optionally Automations/Journeys). Data 360 side: Connected App with OAuth + PKCE, scopes `cdp_api`, `cdp_query_api`, `cdp_profile_api`, `api`, `refresh_token`. [AB:claude-mapping-mcn]
7. Data 360 inventory is pulled via `execute(toolName="d360_metadata")` — confirms the full DMO catalogue (fields, types, category, primary key) is retrievable this way. This is the **same call this project's own skill notes as guard-blocked** (key `d360:execute:d360_metadata:any`). [AB:claude-mapping-mcn]
8. MCE inventory via `sfmc_soap_retrieve` in batches of about 40 customer keys (below 30 the SOAP XML floods the conversation inline; above 40 it lands in a file; page size 25-50 per this project's own platform note). [AB:claude-mapping-mcn]
9. `MktDataModelObject` is a Tooling API entity — querying it via any sObject endpoint returns `INVALID_TYPE`. Use `d360_metadata` instead. Data 360 connector has no SOQL and no getUserInfo — add the platform sObject connector separately for user/org identity. [AB:claude-mapping-mcn]
10. Recommended custom DMO strategy from a worked example: four custom DMOs maximum (`Journey_Entry__dlm`, `Journey_Send_Log__dlm` as Engagement; `Einstein_Engagement_Score__dlm` as Profile; `Marketing_Exclusion__dlm` as Other). [AB:claude-mapping-mcn]

### Email template migration (AMPscript to MC Next)

11. Dependency chain: Data 360 ingestion (S4/S8) → Data Graph built (S11) and its schema exported → field map built (human, workshop with data team) → template rewrite (agent) → validate in MC Next editor (human) → redesign "red" (unsupported) patterns (human). Skipping the field-map step is explicitly called out as "the reason migrations stall." [AB:email-templates-migration-mcn]
12. Inventory every email/template asset; tag AMPscript density, Data Extensions touched, last-sent date (anything unsent in 12 months goes to an archive list, not migrated), owner. [AB:email-templates-migration-mcn]
13. Field map: one row per DE field referenced — columns `de_name, de_field, mcn_source, mcn_object, mcn_field, in_data_graph, notes`. `mcn_source` is one of `datagraph`, `marketing_object`, `crm`, `calculated_insight`, `drop`. [AB:email-templates-migration-mcn]
14. Export the Data Graph definition from Data 360 as `data-graph-schema.json` so rewrites can be checked against real paths. [AB:email-templates-migration-mcn]
15. Of 150 AMPscript functions total in MCE, only **41 supported** in MC Next (Summer '26), roughly 30%. Supported: Math (5), Date/time (6), String (11), Utilities (10), Data access (5: Lookup, Field, Row, RowCount, BuildRowsetFromJson), Salesforce (1: RetrieveSalesforceObjects, read-only), Content (3: ContentBlockById/ByKey/ByName). Control flow (IF/ELSEIF/ELSE/FOR) still works. [AB:email-templates-migration-mcn]
16. New MC Next data-access concepts: **Data Model Objects (DMOs)**, **Data Graphs** (denormalised view templates actually read from — not raw DMOs), **Marketing Objects** (new in Summer '26, a DE-like container populated only by manual CSV import, not a CRM sync replacement), and `RetrieveSalesforceObjects()` (read-only CRM access, no create/update). [AB:email-templates-migration-mcn]
17. Content Builder REST API can export MCE templates programmatically: `POST /asset/v1/content/assets/query`, paged, `pageSize` up to 50. Client-credentials OAuth against `https://<subdomain>.auth.marketingcloudapis.com/v2/token`. This is a genuine documented API route, not UI-only. [AB:email-templates-migration-mcn]

### AMPscript audit skill (MCE MCP connector setup)

18. MCE Setup > Platform Tools > Apps > Installed Packages > New > API Integration > Public App > placeholder Redirect URI initially > minimum "Content Builder Read" scope > note Tenant ID and Client ID > edit real Redirect URI matching the exact MCP host pattern (US: `sfdc-yfeipo`, EU: `sfdc-yzvdd4`). Claude: Settings > Connectors > Add custom connector, MCP Server URL ending `/api/mcp`, leave Client ID/Secret blank. [AB:ampscript-skill-mcn]
19. **The MCP Server URL and the Redirect URI look nearly identical** (same base, one has `/oauth/callback` appended) — mixing them up produces a cryptic HTTP 500. [AB:ampscript-skill-mcn]
20. Page sizes above 50 crash the MCE MCP connector with a Java heap error; keep between 25 and 50 (matches this project's own platform note). [AB:ampscript-skill-mcn]

## Limits

- Account Engagement look-back: up to 2 years. [AB:migrate-ae-mcn]
- MCE-to-Data-360 backfill: only 90 days of send/engagement data on initial connection. [AB:worth-migrating-mcn]
- Event latency Engagement to Flow: 15 minutes to 1 hour.
- Shared sending domain warm-up: 4 to 8 weeks.
- 41 of 150 AMPscript functions supported in MC Next (~30%).
- MCE SOAP batch size: ~40 customer keys (page size 25-50).

## Gotchas

- Business Unit to Data Space mapping is effectively permanent — see `11_data360_enablement_basic_settings.md`.
- Consent semantics differ between MCE and MC Next — see `18_consent.md`.
- AMPscript in MC Next is converted to Handlebars before rendering; a function listed "supported" can still fail if the underlying Handlebars capability isn't there yet — test in the editor, don't trust the support list alone. [AB:email-templates-migration-mcn]
- No CloudPages, no SSJS, no outbound HTTP calls, no DE writes, no encryption functions at send time in MC Next — all need redesign as upstream Data 360 ingestion or a Flow. [AB:email-templates-migration-mcn]
- System timezone for AMPscript date functions in MC Next is UTC — a stated source of test failures if not accounted for. [AB:email-templates-migration-mcn]
- The CRM admin becomes a de facto marketing team member; permissions, identity resolution rules and Campaign object customisations cross that line — change-management, not just technical. [AB:worth-migrating-mcn]
- Authenticating twice to the same MCE MCP endpoint creates a duplicate, non-functional connector — see `14_mce_connector.md`.

## Automation route

- MCE inventory: `sfmc_soap_retrieve` via MCP (API-driven).
- Data 360 inventory: `execute(toolName="d360_metadata")` (API-driven, but guard-blocked in this project — key `d360:execute:d360_metadata:any`).
- Content Builder REST API for template export: genuine API route (`POST /asset/v1/content/assets/query`).
- Connected App / Installed Package / Data Graph schema export / template validation: **UI-only**.
- Everything in the 60-day plan (Data Spaces, bundles, Marketing app, permission sets, identity resolution, Data Graph) is UI-only/admin-process-only per that article — no API detail given.

## Verification

- `OverallStatus: OK` for MCE SOAP test call; a stored file result (not inline) for both `sfmc_soap_retrieve` and `d360_metadata` confirms working connectors.
- MC Next content editor's built-in syntax validator flags template errors inline.
- Recommended test-contact set per logic branch: empty first name, Gold tier, no orders, five orders, each locale — compare rendered output side-by-side against the old MCE render of the same contact. [AB:email-templates-migration-mcn]
- After Days 1-20 of the 60-day plan: re-run the S1-S21 checklist to confirm Data 360 enabled, Data Spaces mapped, permission sets assigned, identity resolution run, Data Graph built.

## Out of scope note: Agentforce agents

- Agentforce agents (Nurturing, Campaign Creation, Content Builder) sit outside the S1-S21 checklist entirely. They depend on Einstein + Agentforce being turned on in Setup, a separate enablement track. None reference Data 360, Data Graphs, or identity resolution. [AB:nurturing-agent-mcn] [AB:campaign-agent-mcn] [AB:content-agent-mcn]

## Sources

[AB:worth-migrating-mcn] Is it worth migrating to Marketing Cloud Next now
[AB:migrate-ae-mcn] Migrate Engagement Data from Account Engagement to Marketing Cloud Next
[AB:claude-mapping-mcn] How to automate Marketing Cloud Engagement to Data 360 data mapping with Claude
[AB:email-templates-migration-mcn] Migrating email templates from Marketing Cloud Engagement to Marketing Cloud Next
[AB:ampscript-skill-mcn] Migrate AMPscript emails to Marketing Cloud Next with a Claude Skill
[AB:nurturing-agent-mcn] How to create the Nurturing Agent in Agentforce Marketing
[AB:campaign-agent-mcn] How to set-up the Campaign Creation Agent in Agentforce Marketing
[AB:content-agent-mcn] How to set-up the Content Builder Agent in Agentforce Marketing
