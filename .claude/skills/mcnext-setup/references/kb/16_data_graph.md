# Data Graph

Covers check S11 (Data Graph on Unified Individual). This is the most contradiction-prone and most open-item-heavy topic in the KB — see `90_open_items_a live org.md` and `91_contradictions.md`.

## Steps

1. During Marketing Cloud Next enablement you are asked to select a Data Graph. The currently selected graph is shown at Assistant Home > **Customer Engagement** tab > **"Configure Basic Personalization"** section (example: "Data Graph: Unified Individual"). [AB:data-graph-understand-mcn]
2. Marketing Setup > Customer Engagement > **Go to Data Graphs**. List view shows existing graphs. [AB:data-graph-use-mcn] [AB:data-graph-understand-mcn]
3. Click **New > "start from scratch"** (or "Create from Scratch"). [AB:data-graph-use-mcn] [AB:data-graph-understand-mcn]
4. Select the **primary Data Model Object**: recommended **Unified Individual**. Give Name, Description, Data Space (e.g. Default). [AB:data-graph-use-mcn] [AB:data-graph-understand-mcn]
5. Select related DMOs used for the send channel: recommended **Unified Indv Contact Point Address, Unified Indv Contact Point Email, Unified Indv Contact Point Phone**. Other common choices: Individual, Contact Point Email, Contact Point Phone, Contact Point Address, Email Engagement, Website Engagement. [AB:data-graph-use-mcn] [AB:data-graph-understand-mcn]
6. **To reach the "Individual" DMO you must also select the "Unified Link Individual" DMO** — it acts as the identity-resolution join between Unified Individual and Individual. Forgetting this link is a likely misconfiguration point. [AB:data-graph-understand-mcn]
7. Tick checkboxes for each field to import from every selected object; article recommends selecting all fields. [AB:data-graph-use-mcn]
8. Click **Save and Build**; a pop-up asks for a refresh schedule (30 minutes to once a month, per the UI-schedule articles — see contradiction below). [AB:data-graph-use-mcn] [AB:data-graph-understand-mcn]
9. A Data Graph is "always built from a single primary Data Model Object" — changing the primary DMO likely means starting a new graph rather than editing (inferred, not tested directly in any article).
10. **Editing an existing Data Graph to add a new related DMO and fields is confirmed as a supported, normal path** — both Einstein Engagement Frequency and Einstein Engagement Scoring articles add DMOs (Email Engagement Frequency; Einstein Engagement Score) to a previously-built graph rather than rebuilding. [AB:einstein-frequency-mcn] [AB:einstein-scoring-mcn]
11. To use it: in Email Builder, the Data Source shown is the selected graph. In a text/heading widget, "Add a merge field" > "Select Data Graph Attribute" > pick a field. A pop-up lets you set a default/fallback text (e.g. "Customer") if the attribute is not found. [AB:data-graph-understand-mcn] [AB:merge-fields-mcn]
12. Templates personalise from the **Data Graph**, not raw DMOs directly — if a field/object isn't in the graph, the template cannot reach it even if the DMO has the data. Export the graph definition as `data-graph-schema.json` from Data 360 to validate template rewrites against real paths during a migration. [AB:email-templates-migration-mcn]
13. Real-Time Segments require a distinct **Real-Time Data Graph**, not the Standard graph used for email personalisation. [AB:segment-create-mcn] [AB:data-graphs-agentforce]
14. Salesforce Personalization (web/product personalization, a separate feature) states "Create a Salesforce DataGraph" as a hard prerequisite but does not name which graph to select — it deploys against whichever data space's Foundation Data you deploy. [AB:sf-personalization-mcn]

## Limits

- **No article in this KB states a numeric field-count cap for a Data Graph.** This is a documentation gap, not resolved by any arthurbackouche.com article. [AB:data-graph-use-mcn] [AB:data-graph-understand-mcn] [AB:data-graphs-agentforce]
- [FIELD] **a live org direct limits: 50 fields per object, 200 fields per graph.** A graph close to 200 fields leaves no room to add related objects: trim duplicates first. These numbers are org-observed facts, not documented anywhere in the KB corpus — treat as authoritative for a live org and note the KB gap when reporting to the client.
- Refresh schedule: 30 minutes to once a month, per the direct how-to articles. [AB:data-graph-use-mcn] [AB:data-graph-understand-mcn]
- Data Graphs consume Data Cloud credits per build/refresh, tracked via the Salesforce Digital Wallet. More frequent refresh = more credits. [AB:data-graph-understand-mcn]
- Minimum volume for Einstein Engagement Frequency modeling to activate: 10 subscribers, 5 frequency variants over 28 days (a Data Graph DMO-add prerequisite, not a graph limit itself — see `19_einstein.md`).

## Gotchas

- **Standard vs Real-Time refresh cadence is contradicted between articles** — see `91_contradictions.md`. Treat the 30-min-to-1-month schedule as the operative one for the graph editor UI (matches direct how-to steps with screenshots); treat "every few seconds" as a higher-level marketing description, possibly a different/newer refresh mode.
- **No article describes a field-removal flow** for an existing Data Graph, only field-addition. This is unknown from the KB — directly relevant to any plan to remove fields 32 duplicated fields from the org's Unified Individual graph. [AB:data-graph-use-mcn]
- Forgetting the "Unified Link Individual" DMO when trying to relate the "Individual" DMO is a likely and specifically-called-out misconfiguration.
- [FIELD] **Lightning combobox, radio, and graph field checkboxes often ignore Chrome automation in a live org.** Only one Chrome agent at a time. This is an org/tooling behaviour, not documented in any article — plan for manual fallback or retries when editing a Data Graph through Chrome automation.
- No article shows any REST, Metadata API, or Tooling API path for Data Graph creation or editing anywhere in this KB — consistent with this project's own note that `d360_metadata` is guard-blocked.

## Automation route

- **UI-only, confirmed across all Data Graph articles in this KB** (How to use, Understanding, Agentforce blog, both Einstein articles that edit a graph). No REST, Metadata API, or Tooling API path is mentioned anywhere.
- [FIELD] The guard block on `d360_metadata` and `d360_datagraph_metadata` in this project is caused by the project's own guard hook (tool name has no read verb), **not by an org toggle.** Do not treat it as evidence the org itself is missing a Data Graph API.
- One unverified, separate lead: two independent articles both point at Salesforce Setup > **MCP Servers > Salesforce Servers > `data-cloud-queries`** as a toggle that must be enabled for `d360_metadata`-style Data Cloud API calls made via a Salesforce-hosted MCP server to work. [AB:multi-agent-orchestration] [AB:claude-mapping-mcn] This is an **unverified org-side prerequisite for hosted MCP access**, recorded separately from the guard-hook cause above — do not conflate the two.

## Verification

- New graph appears in the Data Graphs list view.
- Email Builder Data Source tab shows the graph and its fields available as merge fields; a merge field renders with the chosen default text as fallback if the attribute is not found.
- Digital Wallet shows credit consumption tied to the graph.
- Data Cloud Object Explorer shows the added DMO's fields populated once an Einstein feature is wired in (e.g. "Email Engagement Classification").
- [FIELD] Graph **API name** (not display name) works with `d360_data_graph_get` in a live org — use the API name for any read tool call.
- [FIELD] Data Graph selection for Salesforce Personalization is confirmed at Assistant Home > Customer Engagement > **Configure Basic Personalization**, matching [AB:data-graph-understand-mcn].

## Sources

[AB:data-graph-use-mcn] How to use Data Graph in Marketing Cloud Next
[AB:data-graph-understand-mcn] Understanding Data Graph in Marketing Cloud Next
[AB:data-graphs-agentforce] Understanding Data Graphs in Agentforce Marketing
[AB:einstein-frequency-mcn] How to setup Einstein Engagement Frequency in Marketing Cloud Next
[AB:einstein-scoring-mcn] How to setup Einstein Engagement Scoring in Marketing Cloud Next
[AB:merge-fields-mcn] How to Personalise Emails with Merge Fields in Marketing Cloud Next
[AB:segment-create-mcn] How to create a Segment in Marketing Cloud Next
[AB:sf-personalization-mcn] How to Setup Salesforce Personalization for Marketing Cloud Next
[AB:email-templates-migration-mcn] Migrating email templates from Marketing Cloud Engagement to Marketing Cloud Next
[AB:multi-agent-orchestration] How to Orchestrate Multi-Agents with Claude for Salesforce Delivery
[AB:claude-mapping-mcn] How to automate Marketing Cloud Engagement to Data 360 data mapping with Claude
[FIELD] observed directly in a live implementation
