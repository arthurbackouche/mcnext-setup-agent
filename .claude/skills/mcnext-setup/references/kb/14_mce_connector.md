# MCE (Engagement) connector

Covers check S12 (MCE connector in Data 360). MCE is out of scope for this agent to operate directly; this file documents the mechanism only.

## Steps

1. **In MCE**, create an integration user, e.g. `Data360_Connector`, with permission sets **Marketing Cloud Administrator** and **Administrator**. If MCE has multiple business units, associate the default parent business unit to this user and tick **API user**. [AB:connect-mce-d360]
2. In Data Cloud Setup, open the **Marketing Cloud Engagement** tab, click New. A guided wizard has 4 stages: [AB:connect-mce-d360]
   - **Enter Credentials**: click Manage. Recommend an incognito window. The MCE login page appears — this is the OAuth/login step. **Stop and hand back to the user here** if this window appears during automation; never enter MCE credentials.
   - **Data Source Set-up (Optional)**: click Manage. Select MCE Business Units to receive data from, and Bundles (categories: Email, MobileConnect, MobilePush).
   - **Allow Profile Business Unit Mapping Data**.
   - **Select Business Units to Activate**: click Manage. Select which Business Units can receive activated data/segments from Data 360.
3. Create the MCE Data Streams separately from the connector wizard: Data 360 app > Data Streams > New > select **Marketing Cloud** > Next. Choose either a **Bundle** (Email Studio, Mobile Studio, Mobile Push) or select **Data Extensions** directly. Review pre-selected streams/fields, Deploy. [AB:connect-mce-d360]
4. When the MCE Email bundle is ingested, a stream named **"SFMC Ent Profile Attribute"** ingests individuals and party info automatically — this lets segmentation on "Identification Name = MC Subscriber Key" work without extra setup. [AB:party-id-d360]
5. For custom Subscriber Data Extensions not covered by the bundle: create formula fields on the DLO — `Party Identification Type` = `Person Identifier`, `Party Identification Name` = `MC Subscriber Key`, `Party Identification Id` = `'PersonIdentifier_MCSubKey_' + sourceField['SubscriberKey field']` — then map these to the Individual and Party Identification DMOs. [AB:party-id-d360]
6. To unify individuals on Subscriber Key: create an Identity Resolution ruleset with a custom match rule "MC Subscriber Key" — condition Party Identification > Identification Number > Exact; Party Identification Type = Person Identifier; Party Identification Name = MC Subscriber Key. [AB:party-id-d360]
7. When activating individuals back into MCE, filter Activation on Identification Name = MC Subscriber Key to match individuals already in MCE. [AB:party-id-d360]
8. Segment activation into MCE: Data 360 > Segments (create) > Activation Targets > New > Marketing Cloud Engagement > Next > fill name/description/space > select the connection and Business Unit. Then Data 360 > Activation tab > New > Segment > select Data Space, Segment, Activation Target, Activation Membership (Unified Individual or Individual), identity priority (e.g. Email > highest click score), optional filter, name/description, refresh type (Incremental Append or Full Refresh Overwrite). [AB:activate-segment-d360]

## Consent bridge (one-time, not a live sync)

9. MCE consent does not sync automatically to MC Next. Bridge is manual: in MCE create a DE with Email + Consent Date fields; Automation Studio SQL Query activity, e.g. `SELECT EmailAddress AS Email FROM _Subscribers WHERE Status = 'active' AND DateJoined >= DATEADD(year, -1, GETDATE())`; export via SFTP to CSV; in MC Next, Consent Imports tool, select Channel + Subscription, upload CSV. [AB:consent-mce-bridge-mcn]
10. This is a point-in-time snapshot. Consent captured in MCE after the export is not reflected in MC Next unless re-run. No live bidirectional sync is described anywhere in this KB. [AB:consent-mce-bridge-mcn]

## Two independent worked examples of MCE MCP/API authentication (agent tooling, not the Data 360 connector, but same trap)

11. Both use: MCE Setup > Installed Packages > New > API Integration component > scopes (Content Builder Read minimum, or Data Extensions/Data Folders read-only) > note Tenant ID (subdomain before `.auth.marketingcloudapis.com`) and Client ID. [AB:claude-mapping-mcn] [AB:ampscript-skill-mcn]
12. **The trap that trips everyone up**: the Redirect URI and the MCP Server URL look nearly identical (same base, one has `/oauth/callback` appended). Mixing them up produces a cryptic HTTP 500 with no clue why. [AB:ampscript-skill-mcn]
13. Authenticating twice to the same MCE MCP endpoint can create a second, non-functional connector whose URL ends in `/oauth/callback` — delete it, keep the one whose tools resolve. [AB:claude-mapping-mcn]

## Limits

- Segment activation into MCE timing: **contradicted between articles**, see `91_contradictions.md`. One article says up to 30 min, the dedicated activation article says up to 24 hours — treat 24 hours as the safer planning number.
- Initial Engagement-to-Data 360 connection backfills only **90 days** of send/engagement data. [AB:worth-migrating-mcn]
- Event latency from Engagement to Flow: **15 minutes to 1 hour** — not suitable for real-time transactional triggers; use the On-Demand Flow REST trigger instead (see `21_flows_and_sends.md`). [AB:worth-migrating-mcn]
- MCE fields/DEs retrieved via SOAP through MCP in batches of about 40 customer keys (page size 25-50, matches this project's own platform note; above 50 crashes with a Java heap error). [AB:claude-mapping-mcn] [AB:ampscript-skill-mcn]

## Gotchas

- Integration user needs both Marketing Cloud Administrator and (system) Administrator permission sets in MCE; multi-BU tenants need parent BU association and the API user flag. [AB:connect-mce-d360]
- Skipping the formula-field/DLO-mapping step for custom Subscriber DEs means those individuals carry no Party Identification link back to MCE — Subscriber-Key segment filters and unification silently fail for them. [AB:party-id-d360]
- MC Next consent and MCE consent are two separate stores connected only by the manual export/import bridge described above. [AB:consent-mce-bridge-mcn]

## Automation route

- The credential/OAuth step is a login window — always a stop-and-handback point, never scriptable.
- Data Source Set-up, Business Unit selection, Data Stream creation: **UI-only**, no API given for the native MCE connector itself.
- Segment activation: **UI-only**.
- MCE consent bridge: MCE-side steps (DE, Automation Studio, SFTP) are out of scope for this agent; MC Next-side import is UI-only (Consent Imports CSV upload).
- MCE MCP tooling (`sfmc_soap_retrieve`, Content Builder REST API) is a genuine API route for read access once auth is set up, distinct from the native Data 360 MCE connector.

## Verification

- After deploy, the MCE Data Streams list appears in the Data Streams tab of Data 360.
- `d360_datastream_list`: streams with a Marketing Cloud connector type, or DE-named streams. None = missing (per this skill's S12 check).
- Segment folder visible in MCE containing activated members, after up to 24 hours.

## Sources

[AB:connect-mce-d360] How to connect Marketing Cloud Engagement to Data 360
[AB:party-id-d360] Understanding Party identification in Data 360 for Marketing Cloud Engagement
[AB:activate-segment-d360] How to Activate a Data 360 Segment into Marketing Cloud Engagement
[AB:consent-mce-bridge-mcn] How to manage Consent between Marketing Cloud Engagement and Marketing Cloud Next
[AB:claude-mapping-mcn] How to automate Marketing Cloud Engagement to Data 360 data mapping with Claude
[AB:ampscript-skill-mcn] Migrate AMPscript emails to Marketing Cloud Next with a Claude Skill
[AB:worth-migrating-mcn] Is it worth migrating to Marketing Cloud Next now
