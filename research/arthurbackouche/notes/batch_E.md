# Batch E notes: flows, sites, agents, migration

## Campaign flows

### How to send an email with Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/campaign-flows/how-to-send-an-email-with-marketing-cloud-next/
- Purpose: End-to-end walkthrough of building and activating a Single Email Flow from a Campaign record.
- Prerequisites and order dependencies: Marketing App must be enabled (S7) before Campaigns tab is usable. A Segment or Campaign Members must exist before the flow's Segment step. An Email Template and a Sender/Communication Subscription channel must exist before Configuration step. This is the first-test-send path: Campaign → Brief → Flow → Segment → Email → Configuration → Activate.
- Steps (numbered):
  1. Marketing App > Campaigns tab > New. Fill Campaign Name, Status, Description.
  2. Brief tab: choose existing or create new brief. Fields: Brief Name, Description, Target Audience, Key Message, Additional Information.
  3. Campaign Detail page: Start Date, End Date, Num Sent in Campaign, Expected Response (%), Expected Revenue, Budgeted Cost, Actual Cost.
  4. Campaign Members tab: add Leads/Contacts via top-right buttons.
  5. Create a Flow from the Campaign record. Choose flow type: Single Email, Signup Form, Blank Event, Message Series, or Blank Email.
  6. Single Email Flow: set Schedule (audience entry timing; does not start until flow is activated).
  7. Set Segment: options are Use Quick Filters, Send to Campaign Members, Go to Segment Builder, Select an Existing Segment. Publish the segment.
  8. Select Email Message: pick or create an Email Template.
  9. Configuration: select the Sender and the Communication Subscription channel.
  10. Optional Next Steps: second email and/or Wait.
  11. Activate the campaign/flow.
- Limits and numbers: none stated.
- Gotchas and failure modes: none stated explicitly; article is a happy-path walkthrough.
- Automation route: UI-only. No API endpoints mentioned in this article.
- Verification: Activate button available and clicked implies flow is live; no explicit verification step given (inferred: check FlowDefinitionView / Campaign status).
- Maps to setup checks: S7 (Marketing Cloud/Marketing App enabled is a precondition), S13 (default email channel and sender needed at Configuration step), S14 (this is the minimum path to a first test send).

### How to set-up an A/B Test Flow in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/campaign-flows/how-to-set-up-an-a-b-test-flow-in-marketing-cloud-next/
- Purpose: Build a segment-triggered flow with a Path Experiment (A/B) component.
- Prerequisites and order dependencies: Requires Segment Triggered Flow type to be selectable (this is direct evidence for S14: segment-triggered flow type exists and is choosable at flow creation). Requires an existing segment and at least two email templates/senders.
- Steps:
  1. Create flow, choose flow type = Segment Triggered Flow.
  2. Configure Segment Triggered section: When (schedule) and Who (segment selection).
  3. Drag Path Experiment Component onto canvas. Splits flow into Path A and Path B automatically.
  4. For each path: drag Email Templates Element into the path, select the email template, specify the sender for each email message.
- Limits and numbers: none stated (e.g. no split percentage described in this short article).
- Gotchas and failure modes: "Important: Remember to specify the sender for each email message" -- a stated failure mode is forgetting per-path sender.
- Automation route: UI-only.
- Verification: not stated (inferred: activate flow, confirm both paths configured with sender set).
- Maps to setup checks: S14 (direct evidence segment-triggered flow type exists as a flow creation option; verify by finding "Segment Triggered Flow" as a choice in flow creation, and by ProcessType values from FlowDefinitionView per skill Part 1 S14 check).

### How to Trigger On-Demand Flows with REST API in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/campaign-flows/how-to-trigger-on-demand-flows-with-rest-api-in-marketing-cloud-next/
- Purpose: Trigger a Marketing Cloud Next flow via REST API for near real-time (about 30 seconds) transactional sends.
- Prerequisites and order dependencies: Needs an On-Demand Flow type (a second flow type alongside Segment Triggered, relevant to S14) built and activated first. Needs a Data Graph selected at flow creation. Needs the flow shared with the API-sending user, and that user must be a Flow User. Needs a Salesforce External Client App configured with OAuth before any API call works.
- Steps:
  1. Flow tab > New Flow > search "On-Demand Flow" as the type.
  2. Select a Data Graph for the flow (Data Graphs required infrastructure, ties to S11).
  3. Add an action (e.g. email component) and Save, then Activate.
  4. Click the Gear to edit version properties, copy the Flow API Name (needed later).
  5. On the Flow, click Sharing, select the user that will call the API, and confirm that user is a Flow User.
  6. Salesforce Setup > External Client Apps > Settings > enable "Allow access to External Client App consumer secrets via REST API".
  7. Setup > External Client App Manager > New. Set Name, Contact Email.
  8. In API section: Enable OAuth = True; set Callback URL; OAuth Scopes = "Manage user data via APIs (api)" and "Perform requests at any time (refresh_token, offline_access)"; Enable Client Credentials Flow = True; Require secret for Web Server Flow = True; Require secret for Refresh Token Flow = True; Require PKCE = True. Click Create.
  9. Edit Policies on the new External Client App: enable Client Credentials Flow tickbox, enter the Salesforce username that will run it.
  10. Settings tab > Consumer Key and Secret: retrieve them.
  11. POST to `https://<MyDomain>.my.salesforce.com/services/oauth2/token` with `Content-Type: application/x-www-form-urlencoded`, body `grant_type=client_credentials`, `client_id`, `client_secret`. Returns `access_token`.
  12. POST to `https://<MyDomain>.my.salesforce.com/services/data/v65.0/actions/custom/flow/<Flow_API_Name>` with `Content-Type: application/json`, `Authorization: Bearer <access_token>`, body `{"inputs":[{"EmailAddress": "...", "IndividualId": "..."}]}`. Success = HTTP 200 and email is sent.
- Limits and numbers: flow starts "approximately 30 seconds" after the API event.
- Gotchas and failure modes: "the flow must be shared with the user that will send it through the API" and that user must be a Flow User -- easy to miss step, called out explicitly as "something very important."
- Automation route: The trigger itself is REST API (`services/data/v65.0/actions/custom/flow/<name>`) plus OAuth token request -- both automatable outside the UI. Building/activating the flow, sharing it, and creating the External Client App are UI-only in Setup.
- Verification: HTTP 200 response code; email received in inbox confirms end-to-end.
- Maps to setup checks: S14 (On-Demand Flow is the second flow-availability mode to check alongside Segment Triggered; verify via ProcessType in FlowDefinitionView or by confirming "On-Demand Flow" appears as a flow-type option), S11 (Data Graph selection required at flow creation), S6/S5 (Flow User permission and API access depend on permission sets/licences assigned to the running/API user).

## Sites and forms

### How to create a Landing Page in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/sites-and-forms/how-to-create-a-landing-page-in-marketing-cloud-next/
- Purpose: Build a lead-capture landing page inside Marketing Cloud Next's Content Workspace.
- Prerequisites and order dependencies: Marketing App / Content Workspace for Marketing Cloud must exist (S7). A Data Graph is optional and used only for merge-field personalisation (Data Sources setting), so this does not block landing page creation, only personalisation.
- Steps:
  1. Content tab > select Content Workspace for Marketing Cloud.
  2. Click Add > Landing page (or Landing Page Template to make it reusable) in the Create CMS Content pop-up.
  3. Choose "use Components" to start from scratch (no template yet).
  4. Settings: Title, API Name, Description, Content Slug (URL), Favicon, Public Page Title, Public Description, Head Tags (e.g. for Meta Pixel), "Let search engines index this page" toggle.
  5. Style: select a background image.
  6. Data Sources: select a Data Graph to personalise with merge fields (optional).
  7. Add Components: Button, Divider, Heading, HTML, List, Paragraph, Form, Section, Image.
- Limits and numbers: none stated.
- Gotchas and failure modes: Builder is explicitly not comparable to Wix/Elementor/Framer -- set expectations, not a full website builder.
- Automation route: UI-only.
- Verification: not stated (inferred: preview/publish the page and confirm public URL resolves).
- Maps to setup checks: S7 (Marketing App/content workspace precondition), S11 (Data Graph needed only if personalising with merge fields).

### How to integrate External Sites in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/sites-and-forms/how-to-integrate-external-sites-in-marketing-cloud-next/
- Purpose: Enable web tracking on an external (non-MC-Next) website and feed events into Data 360 so segments can be built on browsing behaviour.
- Prerequisites and order dependencies: Requires Data 360 enabled (S3). Requires the External Tracking Data Kit installed before the Web Engagement DMOs exist (this is a specific data kit not otherwise named in earlier batches -- relevant to S8). Requires a Salesforce CRM data stream (MarketingStreamingAppConfig) to link tracking data to a Campaign.
- Steps:
  1. Salesforce Setup > Web Tracking > External Websites section: set "Require Consent to Track" to Disabled (or configure per policy).
  2. Install the External Tracking Data Kit (enables Web Engagement DMOs in Data 360).
  3. Create a Website Connector (Website Tracking Connector), click "Go To Data Streams."
  4. Data 360 App > Data Streams tab > New > Installed Data Kits & Packages > Next.
  5. Search "External Tracking" under Data Kits tab, select all Bundles and Bundle Items.
  6. In the External Tracking Bundle settings, select the Website Connector Type and the connector created in step 3, click Next.
  7. Review the two generated data streams (identity and Behavioral Events), Deploy.
  8. Create a second, separate Data Stream: Salesforce CRM as Data Source, search bundle "MarketingStreamingAppConfig," review attribute fields, Deploy. (This pulls website-connector data into a related Campaign.)
  9. Back in Setup > Web Tracking > Manage Website Connectors: select the connector, choose a Related Campaign, Save.
  10. Copy the generated tracking script.
  11. Add the script to the external website header (Site Wide Script if it should apply to all pages), Publish and Activate.
- Limits and numbers: none stated.
- Gotchas and failure modes: Related Campaign can be swapped over time so that new results populate a new campaign only (e.g. quarterly campaigns) -- a design choice, not a hard limit.
- Automation route: Data Stream creation and deployment are typically Setup UI actions per this article (no REST/SOQL alternative given) -- mark UI-only. Web Tracking toggle and CORS-adjacent settings are UI-only in Setup.
- Verification: not explicitly stated (inferred: confirm the two data streams show status Active/Deployed, and that Website Engagement DMO gets populated after script goes live).
- Maps to setup checks: S3 (Data 360 must be enabled), S4/S8 (a data kit -- External Tracking -- distinct from the four already tracked in S8; note as an additional data kit to check for if the client uses external web tracking), S10 (Website Engagement DMOs relate to Unified Individual DMO for segmentation).

### How to Track Activity on Landing Pages in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/sites-and-forms/how-to-track-activity-on-landing-pages-in-marketing-cloud-next/
- Purpose: Enable engagement tracking (Page Views, Form Submissions, Link/Button Clicks) specifically on MC Next-hosted Landing Pages (as opposed to external sites).
- Prerequisites and order dependencies: Applies to a Marketing Landing Page already created (see landing page article above). Requires Data Cloud integration added at the Experience Cloud Site level.
- Steps:
  1. Salesforce Setup > All Site > click Builder on the relevant Marketing Landing Pages site.
  2. In the Landing Pages Builder: Settings > Security & Privacy > select "Relaxed CSP: Permit Access to inline Scripts and Allowed Hosts."
  3. Integration tab > add Data Cloud to Site.
  4. Advanced > Edit Head Markup > add a script that dispatches a custom `experience_interaction` event with `name: 'set-consent', value: true` to register consent for tracking.
- Limits and numbers: none stated.
- Gotchas and failure modes: Without the Relaxed CSP setting, inline scripts (like the consent script) may be blocked -- implicit gotcha from the ordering of steps.
- Automation route: UI-only (Site Builder settings and Head Markup edit are Experience Cloud Site Builder actions).
- Verification: not stated (inferred: check Website Engagement DMO in Data 360 for events tied to the landing page site after publishing).
- Maps to setup checks: S3 (Data Cloud/Data 360 integration to the site), S10 (Website Engagement ties to Unified Individual for segmentation).

### How to use Form Handlers in Agentforce Marketing
Source: https://arthurbackouche.com/docs/marketing-cloud-next/sites-and-forms/how-to-use-form-handlers-in-agentforce-marketing/
- Purpose: Ingest submissions from an existing external website form (no rebuild) into a Salesforce object (Contact/Lead/Prospect/Account) via a Form Handler.
- Prerequisites and order dependencies: Marketing App Content workspace must exist. CORS must be configured for the external domain before the form handler can receive cross-origin submissions (last step, but functionally a hard prerequisite for it to work in production).
- Steps:
  1. Content tab of Agentforce Marketing > select the dedicated Workspace.
  2. Add > Content > Form Handler > Create.
  3. Select a Data Source object: Contact, Lead, Prospect, or Account. Example: Name "Contact_Records", Type "Salesforce Record", Object "Contact", Record Type "Contact".
  4. Drag & drop fields from the object to map (example: First Name, Last Name, Email, Mobile Phone, Contact Description).
  5. For each mapped field, reference the corresponding field attribute ID from the actual website form (example given: WordPress Elementor form).
  6. Fill Details: Form Title, API Name, Description.
  7. Set Submission redirect URL (required to save the form).
  8. Save. Before publishing, create a Flow -- one is auto-populated with an element that creates the Contact record in Salesforce CRM. Publish the Form Handler.
  9. Copy the two generated scripts and insert them into the website.
  10. Salesforce Setup > CORS > Add domain (enter the external website's domain, e.g. arthurbackouche.com).
- Limits and numbers: none stated.
- Gotchas and failure modes: Submission redirect URL is required to save the form (cannot skip). CORS must include the domain or cross-domain submissions fail.
- Automation route: UI-only for Form Handler build; CORS domain addition is a Setup UI action (no API route given in this article).
- Verification: not stated (inferred: submit a test form and confirm a Contact record is created via the auto-generated Flow).
- Maps to setup checks: S7 (Marketing App content workspace), none of S1-S21 directly cover CORS or Form Handlers; note as a gap in the current check list (inferred).

## Agentforce agents

### How to create the Nurturing Agent in Agentforce Marketing
Source: https://arthurbackouche.com/docs/marketing-cloud-next/agentforce-agents/how-to-create-the-nurturing-agent-in-agentforce-marketing/
- Purpose: Configure an Agentforce agent that scores Lead interest and replies to Leads by email automatically.
- Prerequisites and order dependencies: Requires Agentforce for Sales enabled. Requires the running user granted "Use Lead Nurturing Agent" access before they can create an agent. Requires an Agent User created and connected to an email inbox (Gmail/Outlook) as a first-class step before agent configuration. Requires a Messaging Channel enabled and associated after activation.
- Steps:
  1. Salesforce Setup > Agentforce for Sales > Lead Nurturing tab > scroll to Lead Nurturing section > Enable it.
  2. Manage Access for Managers and Users section > Manage > assign the user to "Use Lead Nurturing Agent."
  3. Manage Agent's User Record and Email section: create an Agent User (a regular Salesforce user with its own read/write/delete permissions).
  4. Configure the Agent: name it, connect it to an email address (Gmail or Outlook) -- the agent replies on the user's behalf using this mailbox, so choose carefully.
  5. Data Library section: choose what the agent can access -- knowledge base, unstructured PDF documents, or live web search.
  6. Build and Manage Agent > Go > guided setup > select Agent Template "Lead Nurturing."
  7. Answer guided questions about the organisation (activity, how it helps customers). Preview a generated sample email; test against a chosen Lead.
  8. Product knowledge section: select the Data Library created earlier.
  9. Qualification setting: define attribute fields to evaluate and questions to ask the Lead to gauge interest.
  10. Add assignment conditions (e.g. City, Title) so matching Leads are auto-assigned to the Nurturing Agent.
  11. Review and Activate the agent.
  12. After activation, enable and associate a Messaging Channel.
- Limits and numbers: none stated.
- Gotchas and failure modes: Choosing the wrong connected email address is called out explicitly -- the agent replies on your behalf using that inbox.
- Automation route: UI-only.
- Verification: Create a test Lead in Salesforce CRM; confirm an email arrives in the connected inbox within a few minutes.
- Maps to setup checks: none of S1-S21 directly (Agentforce for Sales / Lead Nurturing is a separate licensed feature from the S1-S21 Data 360/MC Next checklist); note as out of current check scope (inferred).

### How to set-up the Campaign Creation Agent in Agentforce Marketing
Source: https://arthurbackouche.com/docs/marketing-cloud-next/agentforce-agents/how-to-set-up-the-campaign-creation-agent-in-agentforce-marketing/
- Purpose: Set up an Agentforce agent that creates Campaigns and auto-populates Campaign Briefs via chat.
- Prerequisites and order dependencies: Requires Einstein turned on, then Agentforce turned on, in that order, before an agent can be built. Agent access must then be separately granted per Profile or Permission Set.
- Steps:
  1. Salesforce Setup > Einstein Setup > Turn on Einstein.
  2. Salesforce Setup > Agentforce Agents > Turn on Agentforce > New Agent.
  3. Agentforce Builder: select the Campaign Creation card > Next.
  4. Confirm pre-added Topics: "Marketing Cloud: Campaign Planning" and "Marketing Cloud: Campaign Preview Refinement." Next.
  5. Fields are pre-populated; add company information. Next.
  6. Select supported languages and agent tone. Click Create.
  7. Activate the Agent.
  8. Grant access: Setup > Profiles > select a Profile (e.g. System Administrator; a Permission Set also works) > scroll to Agent Access > Edit > tick Campaign Creation Agent > Save.
  9. Use: click the Agent button (top right) > Agentforce pop-up > Create Campaign or Create a Brief. Preview via "Generate Campaign Preview" before creating.
- Limits and numbers: none stated.
- Gotchas and failure modes: none stated explicitly.
- Automation route: UI-only.
- Verification: Agent appears Active in Agentforce Agents list; using it from the Agent button produces a populated Brief/Campaign.
- Maps to setup checks: none of S1-S21 directly; Einstein/Agentforce enablement is adjacent to but distinct from the Data 360/MC Next checklist (inferred out of scope).

### How to set-up the Content Builder Agent in Agentforce Marketing
Source: https://arthurbackouche.com/docs/marketing-cloud-next/agentforce-agents/how-to-set-up-the-content-builder-agent-in-agentforce-marketing/
- Purpose: Set up the generative-AI Content Builder Agent inside the Email/Landing Page content editors.
- Prerequisites and order dependencies: Depends on Einstein and Agentforce already being enabled (same steps as the Campaign Creation Agent article, explicitly cross-referenced).
- Steps:
  1. Salesforce Setup > Agentforce Agents > + New Agent.
  2. Select Content Builder Agent card > Next.
  3. Confirm pre-selected "Content Creation" topic > Next.
  4. Add company information > Next.
  5. Optionally select a Data Library as a Data Source (can be skipped) > Create.
  6. Activate the Agent (ignore any warning message shown).
  7. Grant access: Profile > Agent Access > Edit > select Content Builder Agent > Save.
  8. Use: open an Email Template > click the Agentforce icon (top left of email builder) > chat with the agent to update the template.
- Limits and numbers: none stated.
- Gotchas and failure modes: A warning message appears on activation without a Data Library selected; article says to ignore it.
- Automation route: UI-only.
- Verification: Agentforce icon appears in the email/landing page editor and responds to chat prompts.
- Maps to setup checks: none of S1-S21 directly (inferred out of scope, same as other Agentforce agent articles).

## Migration

### How to automate Marketing Cloud Engagement to Data 360 data mapping with Claude
Source: https://arthurbackouche.com/docs/marketing-cloud-next/migration/how-to-automate-marketing-cloud-engagement-to-data-360-data-mapping-with-claude/
- Purpose: Describes a Claude Skill that inventories MCE Data Extensions and Data 360 DMOs, then proposes a field-level migration mapping.
- Prerequisites and order dependencies: Requires both an MCE MCP connector and a Data 360 MCP connector configured before the skill can run. MCE side needs an Installed Package (server-to-server, API Integration component, read-only scopes on Data Extensions/Data Folders, optionally Automations/Journeys). Data 360 side needs a Connected App with OAuth + PKCE and specific scopes. Mapping/design work (Stage 3) depends on completed inventories from Stages 1 and 2.
- Steps (setup-relevant only):
  1. MCE: Setup > Apps > Installed Packages > create server-to-server package > Add API Integration component > grant read-only scopes on Data Extensions and Data Folders (optionally Automations/Journeys for audit features). No write scopes.
  2. Store Client ID, Client Secret, tenant subdomain (from the Authentication Base URI) in a secrets manager.
  3. Claude: Settings > Connectors > Add custom connector > point at the MCE MCP endpoint > authenticate with package credentials. Confirms tools `sfmc_soap_retrieve`, `sfmc_rest_get`, `sfmc_describe_object` appear.
  4. Test with `sfmc_soap_retrieve(object_type="DataExtension", properties=["Name","CustomerKey"])`; success = `OverallStatus: OK` and result lands in a file (not inline).
  5. Data 360: Salesforce Setup > App Manager > new Connected App, OAuth enabled, PKCE. Scopes: `cdp_api`, `cdp_query_api`, `cdp_profile_api`, `api`, `refresh_token`. Note the consumer key.
  6. Pick sandbox vs production MCP URL; for a migration plan, point at the sandbox holding the target model.
  7. Claude: Add connector for Data 360 the same way. Confirms `search`, `payload_examples`, `execute` meta-tools; all `d360_*` tools run through `execute`.
  8. Verify Data 360 connector with `execute(toolName="d360_metadata", paramsJson="{}")` -- confirms the full DMO catalogue (fields, types, category, primary key) is retrievable; success = result stored to a file.
  9. Run the skill in three prompts: (1) Data 360 inventory via `d360_metadata`, (2) MCE inventory via SOAP retrieves narrowed to a shortlist of relevant folders, (3) mapping plan applying tiering rules.
- Limits and numbers: MCE fields retrieved in batches of about 40 customer keys; below 30 the SOAP XML floods the conversation inline, above 40 it lands in a file. Harbourline example: 640 DEs total, shortlisted to 180 relevant ones. Four custom DMOs recommended maximum in the described strategy (Journey_Entry__dlm, Journey_Send_Log__dlm as Engagement; Einstein_Engagement_Score__dlm as Profile; Marketing_Exclusion__dlm as Other).
- Gotchas and failure modes: Authenticating twice to the same MCE MCP endpoint can create a second, non-functional connector whose URL ends in `/oauth/callback` -- delete it, keep the one whose tools resolve. `MktDataModelObject` is a Tooling API entity: querying it via any sObject endpoint returns `INVALID_TYPE` -- do not attempt; use `d360_metadata` instead. Data 360 connector has no SOQL and no getUserInfo -- add the platform sObject connector separately if you need to confirm user/org identity.
- Automation route: MCE inventory via `sfmc_soap_retrieve` (SOAP through MCP); Data 360 inventory via `execute(toolName="d360_metadata")` (this is the same `d360_metadata` call the mcnext-setup skill's S11 check notes is blocked by the guard in our environment -- key: `d360:execute:d360_metadata:any`). Connected App / Installed Package creation is UI-only in Setup.
- Verification: `OverallStatus: OK` for MCE SOAP test call; a stored file result (not inline) for both `sfmc_soap_retrieve` and `d360_metadata` confirms working connectors.
- Maps to setup checks: S3 (Data 360 instance must be enabled for `d360_metadata` to return data), S4 (CRM connector data streams are what `d360_metadata` inventories), S12 (MCE connector/tenant is the second side of the mapping and needs its own auth), S11 (this article independently confirms `d360_metadata` is the only reliable way to get the full DMO catalogue, matching the guard-blocked key already flagged in our skill).

### Is it worth migrating to Marketing Cloud Next now?
Source: https://arthurbackouche.com/docs/marketing-cloud-next/migration/is-it-worth-migrating-to-marketing-cloud-next-now/
- Purpose: Strategic/architectural overview of Marketing Cloud Engagement+ and the recommended 60-day path to Marketing Cloud Next, including the setup prerequisites for each of the five "low-lift" use cases.
- Prerequisites and order dependencies: This article is the clearest single source for setup sequencing. It states the whole Days 1-20 admin sequence (Enable Data 360 → create Engagement admin user in core org → create Data Spaces and map BUs → turn on Engagement data bundles → enable Marketing app and analytics dashboards → add marketing users and assign standard Marketing Cloud permission sets → configure and run identity resolution → create a Data Graph → optionally sync key DEs as custom DMOs and create an Activation Template for Flow). Steps 1-6 alone give "a working Next environment"; steps 7-8 (identity resolution, Data Graph) unlock Flow decisioning, personalisation and agents -- can be deferred if the first use case is reporting-only.
- Steps (the 60-day plan, setup-relevant):
  1. Days 1-20 (Foundation): Enable Data 360; create Engagement admin user in the core org; create Data Spaces (recommend 1:1 mapping of each MCE Business Unit to one Data Space, starting with just one or two BUs tied to the first use case); turn on out-of-the-box Engagement data bundles and map BUs; enable the Marketing app and out-of-the-box analytics dashboards; add marketing users to the core org and assign standard Marketing Cloud permission sets; configure and run identity resolution (creates Unified Individual); create a Data Graph; optionally sync one or two key DEs to Data 360 as custom DMOs and create an Activation Template for Flow.
  2. Days 21-40 (Configure one use case): open Digital Wallet and Marketing Performance dashboards; connect existing journeys to Campaign records; build a V1 of the chosen use case using only out-of-the-box features.
  3. Days 40-60 (Launch): deploy to an internal/small audience, measure, run a feedback session, then move to the next use case.
- Limits and numbers: Initial Engagement-to-Data 360 connection backfills only 90 days of send/engagement data. Event latency from Engagement to Flow is 15 minutes to 1 hour (not suitable for real-time transactional triggers -- use the REST API on-demand flow trigger for that instead, per the campaign-flows article). Shared-sending domain warm-up: 4 to 8 weeks. Journey Decisioning Agent suits segments under 20,000 (consumes Flex credits). First Flow recommended to stay under 1 million audience per hour.
- Gotchas and failure modes:
  - Business Unit to Data Space mapping is effectively permanent: you cannot uninstall the Marketing app from a Data Space once installed. Mapping several MCE BUs into one Data Space and later removing one deletes all historical data for that BU in the Data Space, breaking every dependent report/segment/Flow. Start narrow (1:1, one or two BUs); adding mappings later is easy, removing is not.
  - Install the Marketing app into a production-grade BU, not a test BU. Use sandbox orgs for testing instead.
  - Next business units are not a copy of Engagement business units -- permissions, sender identities and consent behave differently. Read Data Space docs before mapping a complex multi-brand org.
  - Consent semantics differ: Engagement checks consent at the subscriber level; Next checks consent at the Contact Point (email/phone) plus Communication Subscription level. If two subscriber records share one email and that address opts out, both are suppressed in Next (only the opted-out record is suppressed in Engagement). Households sharing an email are the classic edge case -- test it. A global opt-out at the Contact Point level is planned for Winter '27, i.e. not yet available.
  - Shared sending: domains carry over, IPs and reputation do not -- plan a warm-up.
  - AMPscript must be audited before assuming any template will "just work" in Next.
  - Agentic features consume Flex credits (consumption-based pricing) -- monitor via Digital Wallet from day one.
  - The CRM admin becomes a de facto marketing team member; permissions, identity resolution rules and Campaign object customisations cross that line -- a change-management issue, not just technical.
- Automation route: UI-only / admin-process-only; this article gives no API detail. (It references that MC Next relies on Data 360, identity resolution, Data Graphs and Flow -- the "building blocks" -- consistent with earlier batches.)
- Verification: not explicitly given per step (inferred: after Days 1-20, confirm Data 360 enabled, Data Spaces created and mapped to correct BUs, permission sets assigned, identity resolution run producing Unified Individuals, and a Data Graph built -- i.e. re-run the S1-S21 checklist).
- Maps to setup checks: S1 (sandbox awareness -- use sandbox orgs for testing, not production-grade BU), S2/S5/S6 (assign standard Marketing Cloud permission sets to marketing users), S3 (Enable Data 360 first, step 1), S7 (enable the Marketing app), S9 (Data Space creation and 1:1 BU mapping -- directly informs S9's "which data space MC uses" question, currently marked UI-only/unknown in the skill; this article gives concrete guidance: one Data Space per BU, start narrow), S10 (configure and run identity resolution to create Unified Individual), S11 (create a Data Graph -- required to unlock Flow decisioning and personalisation, i.e. is the minimum extra step beyond S7 needed before decisioning-based flows work), S12 (Engagement data bundles / BU mapping is the MCE connector setup), S13 (shared sending / sender identities, consent -- directly relevant to S13 and S16), S14 (Flow orchestration use case explicitly needs "connected data, a Data Graph to expose data to Flow, audiences and events created"; identity resolution is optional at Level 1-2 of Flow orchestration but mandatory for Level 3 Journey Decisioning).

### Migrate AMPscript emails to Marketing Cloud Next with a Claude Skill
Source: https://arthurbackouche.com/docs/marketing-cloud-next/migration/migrate-ampscript-emails-to-marketing-cloud-next-with-a-claude-skill/
- Purpose: Describes a packaged Claude Skill that audits an MCE email estate for AMPscript compatibility with MC Next and produces a client-ready report, plus how to set up the MCE MCP connector needed to run it.
- Prerequisites and order dependencies: Requires the MCE MCP Server connected before the skill can pull any content. Connector setup (Part A MCE side, Part B Claude side) must both succeed before Stage 2 (pull the estate) can run.
- Steps (setup-relevant):
  1. MCE Setup > Platform Tools > Apps > Installed Packages > New. Name it.
  2. Add Component > API Integration > Public App.
  3. Enter a placeholder Redirect URI (e.g. `https://salesforce.com`) since the real one isn't known yet.
  4. Grant scopes: minimum "Content Builder Read" for this skill; expand only as needed.
  5. Note Tenant ID (subdomain before `.auth.marketingcloudapis.com` in the Authentication Base URI) and Client ID (shown on the package).
  6. Go back into the API Integration component > Edit > set the real Redirect URI: `https://mai-mce-mcp-cdp1.sfdc-yfeipo.svc.sfdcfc.net/t/{TENANT_ID}/c/{CLIENT_ID}/api/mcp/oauth/callback` (US host; EU swaps `sfdc-yfeipo` for `sfdc-yzvdd4`). Save.
  7. Claude: Settings > Connectors > Add custom connector. Name it.
  8. MCP Server URL = same base URL without `/oauth/callback` suffix (ends in `/api/mcp`).
  9. Leave Advanced settings (Client ID/Secret) blank -- the server advertises its own OAuth details. Click Add, sign in to Marketing Cloud, approve.
  10. Run skill stages: refresh AMPscript support baseline from Salesforce docs; pull all emails/templates via Content Builder API through the MCP connector; parse and classify each email A-F; find the systemic fix that unlocks the largest category; build and self-QA a PDF report.
- Limits and numbers: Page sizes above 50 crash the MCE MCP connector with a Java heap error; keep between 25 and 50. In the article's real client run: 494 emails audited; one data-prep change (a systemic fix) unlocked 335 emails at once.
- Gotchas and failure modes: The MCP Server URL and the Redirect URI look nearly identical (same base, one has `/oauth/callback` appended); mixing them up produces a cryptic HTTP 500 with no clue why -- "the one thing that trips everyone up." If Data Extension calls are denied, the audit can continue -- it only needs Content Builder access. Sanity-check the function census before building the report; if top functions are unrecognisable, something is being misread. Page through three asset types (templatebasedemail, htmlemail, template), not just one.
- Automation route: Connector setup (Installed Package, API Integration component, Redirect URI) is UI-only in MCE Setup. Once connected, all data pulls run through the MCP tools (`sfmc_soap_retrieve`/Content Builder API) -- automatable, not UI. Skill install: enable Code execution under Settings > Capabilities in Claude, then Skills > upload zip -- UI action in Claude, not Salesforce.
- Verification: Confirm connector works by checking the four MCP tools resolve after adding the connector; a successful audit run produces `reports/inventory.csv`/PDF output.
- Maps to setup checks: S12 (this is a second, independent worked example of MCE connector authentication, reinforcing that Tenant ID + Client ID + a precisely-matched Redirect URI is the trap to watch for when setting up any MCE integration, including the Data 360 MCE connector in step F of our Part 2).

### Migrating email templates from Marketing Cloud Engagement to Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/migration/migrating-email-templates-from-marketing-cloud-engagement-to-marketing-cloud-next/
- Purpose: Long-form guide (with a Claude Code agent design) for rewriting AMPscript email templates from MCE's Data Extension model to MC Next's Data 360 / Data Graph / Handlebars model.
- Prerequisites and order dependencies: A completed field map (Data Extension field -> Data 360 object/field) is described as the single most important artefact and must exist before any template rewrite. The field map itself depends on Data 360 objects being ingested and, where used, a Data Graph being built and its schema exported (`data-graph-schema.json`) so the agent can validate paths exist. So the dependency chain for this migration workstream is: Data 360 ingestion (S4/S8) → Data Graph built (S11) and its schema exported → field map built (human, workshop with data team) → template rewrite (agent) → validate in MC Next editor (human) → redesign reds (human).
- Steps (setup-relevant only):
  1. Inventory every email/template asset; tag AMPscript density, Data Extensions touched, last-sent date (anything unsent in 12 months goes to an archive list, not migrated), and an owner.
  2. Build the field map: one row per DE field referenced, columns `de_name, de_field, mcn_source, mcn_object, mcn_field, in_data_graph, notes`. `mcn_source` is one of `datagraph`, `marketing_object`, `crm`, `calculated_insight`, `drop`.
  3. Export the Data Graph definition from Data 360 as `data-graph-schema.json` so template rewrites can be checked against real paths.
  4. Rewrite templates against the field map and the supported/unsupported AMPscript function reference (agent step; not itself a setup step).
  5. Validate every rewritten template in the MC Next content editor's syntax validator, then preview against chosen test contacts.
  6. Redesign "red" (unsupported, no drop-in) patterns as Flow-triggered writes, Data 360 upstream pre-computation, or Marketing Object lookups, as appropriate.
- Limits and numbers: Of 150 AMPscript functions total in MCE, only 41 are supported in MC Next as of Summer '26 (roughly 30%); 109 are unsupported (mostly ones that write data, call APIs, or serve CloudPages). Supported categories: Math (5), Date/time (6), String (11), Utilities (10), Data access (5: Lookup, Field, Row, RowCount, BuildRowsetFromJson), Salesforce (1: RetrieveSalesforceObjects, read-only), Content (3: ContentBlockById/ByKey/ByName). Control flow (IF/ELSEIF/ELSE/FOR) still works.
  - MC Next data-access concepts relevant to setup: Data Model Objects (DMOs, the Customer 360 model), Data Graphs (denormalised pre-computed view a template actually reads from -- not raw DMOs), Marketing Objects (new in Summer '26; a Data-Extension-like container populated only by manual CSV import at time of writing, not a CRM sync replacement), and `RetrieveSalesforceObjects()` (read-only CRM object access, no create/update).
- Gotchas and failure modes:
  - Templates personalise from a Data Graph, not from raw DMOs directly -- if a field/object isn't in the Data Graph, the template cannot reach it even if the DMO has the data (directly relevant to S11: the Data Graph must include every DMO/related object a template needs, not just Unified Individual).
  - AMPscript in MC Next is converted to Handlebars before rendering; a function listed as "supported" can still fail if the underlying Handlebars capability isn't there yet -- test in the editor, don't trust the support list alone.
  - Marketing Objects only support manual CSV import (no automated CRM sync) at time of writing -- not a substitute for a proper Data 360/DMO sync for CRM data.
  - No CloudPages, no SSJS, no outbound HTTP calls, no DE writes, no encryption functions at send time in MC Next -- all of these need to be redesigned as upstream Data 360 ingestion or a Flow, before the send.
  - System timezone for AMPscript date functions in MC Next is UTC -- a stated source of test failures if not accounted for.
- Automation route: Content Builder REST API (`POST /asset/v1/content/assets/query`, paged, `pageSize` up to 50 shown in the article's example script) can export MCE templates programmatically -- this is a genuine documented API route, not UI-only. Client-credentials OAuth token request against `https://<subdomain>.auth.marketingcloudapis.com/v2/token` is also shown as a scriptable step. Building/exporting the Data Graph schema and validating templates in the MC Next editor's syntax validator are UI-only per this article (no API given for those).
- Verification: MC Next content editor's built-in syntax validator flags errors inline. Beyond syntax, the article recommends rendering each template against a deliberately chosen set of test contacts (one per logic branch: empty first name, Gold tier, no orders, five orders, each locale) and comparing rendered output side-by-side against the old MCE render of the same contact.
- Maps to setup checks: S4/S8 (Data 360 ingestion of the CRM/DE data that templates will read), S10 (Unified Individual / Individual DMO is the object most merge fields resolve against), S11 (Data Graph must include every related object a template needs -- direct, detailed evidence for why S11 matters and how to verify it: export the Data Graph schema and confirm required objects/fields are present), S21 (custom DMO mappings, analogous to this article's "custom DMO" `mcn_source` category for fields that don't fit a standard DMO).

## Blog: multi-agent orchestration (setup-relevant excerpt only)

### How to Orchestrate Multi-Agents with Claude for Salesforce Delivery
Source: https://arthurbackouche.com/how-to-orchestrate-multi-agents-with-claude-for-salesforce-delivery/
- Purpose: Explains multi-agent orchestration concepts (Coordinator + Worker agents) and walks through setting up Claude Platform agents connected to Salesforce and Data 360 via MCP, for general Salesforce delivery work (not MC Next-specific).
- Prerequisites and order dependencies: Requires a Salesforce External Client App with OAuth + PKCE + JWT-based tokens for named users, configured before Claude Console connectors can be added. Requires the "MCP Servers" feature enabled in Salesforce Setup (specifically the `data-cloud-queries` Salesforce Server, and optionally `sobject-all`) before the Data 360 and Salesforce Platform connectors will expose tools in Claude.
- Steps (setup-relevant):
  1. Salesforce Setup > External Client App Manager > New External Client App. Set Name, Contact Email, Distribution State = Local, Enable OAuth = True, Callback URL = `https://claude.ai/api/mcp/auth_callback`.
  2. Select scopes: `refresh_token`/`offline_access`, `mcp_api` (Access Salesforce hosted MCP servers), `data_cloud_user_claims`, `cdp_api`, `interaction_api`, `sfap_api`, `cdp_calculated_insight_api`, `cdp_identityresolution_api`, `cdp_segment_api`, `cdp_profile_api`, `cdp_ingest_api`, `api`.
  3. Security: enable PKCE and "Issue JSON Web Token (JWT)-based access tokens for named users." Create.
  4. Settings tab > Consumer Key and Secret; also enable Client Credentials Flow with the relevant username.
  5. Salesforce Setup > MCP Servers > Salesforce Servers tab > enable `data-cloud-queries` (and optionally `sobject-all`).
  6. Salesforce Setup > OAuth and OpenID Connect Settings > turn on "Require Proof Key for Code Exchange (PKCE) Extension for Supported Authorization Flows."
  7. Claude Console > Credential vaults > Add credential. Provide Name, MCP Server URL (e.g. `https://api.salesforce.com/platform/mcp/v1/data/data-cloud-queries`), Client ID, Client Secret. Connect.
  8. Create Coordinator and Worker agents via YAML pasted into Claude's Quick Start tab.
- Limits and numbers: Multi-agent output quality reported "up to 90.2% better" than single-agent, at up to 15x the cost per request -- a trade-off, not a hard technical limit.
- Gotchas and failure modes: none specific to setup beyond the OAuth scope list needing to be complete for the intended Data 360 API calls to work (inferred from the specificity of the scope list).
- Automation route: UI-only for the External Client App and MCP Servers enablement in Salesforce Setup; Claude Console connector setup is also UI-only (no REST alternative given).
- Verification: not explicitly stated (inferred: connector shows tools resolving, e.g. `search`/`payload_examples`/`execute` for Data 360, after Connect succeeds).
- Maps to setup checks: S11 (this article independently confirms `d360_metadata`-style Data Cloud API access requires the `MCP Servers > Salesforce Servers > data-cloud-queries` toggle enabled in Setup -- a concrete, previously-undocumented-in-our-skill UI location to check/enable if S11's `d360_metadata` call is guard-blocked or returns nothing). This is the most useful new fact from this article for our setup work, even though the article itself is about general Salesforce delivery, not MC Next.

## Batch E cross-cutting findings

Setup items a Build phase (flows, sites, agents) depends on:
- Segment-triggered flows (S14) require nothing beyond a working segment and the flow-type picker offering "Segment Triggered Flow" -- confirmed directly in the A/B Test Flow article. On-demand flows (the second S14-relevant flow type) additionally require a Data Graph selection at creation time, Flow Sharing to the API user, that user being a Flow User, and a working External Client App with OAuth for the REST trigger.
- The minimum setup for a first test send from a flow (per the "send an email" article) is: Marketing App/Campaigns enabled (S7), at least one segment or Campaign Members list, one Email Template, and a configured Sender + Communication Subscription channel (S13). No Data Graph or identity resolution is required for this simplest path -- those only matter once personalisation from Data 360 fields is needed (Merge fields, Handlebars against DMOs) or on-demand/decisioning flows are used.
- Landing pages, form handlers, and web tracking all optionally use a Data Graph (S11) for personalisation but do not require one to function at a basic level; web tracking additionally needs the External Tracking Data Kit installed (a specific data kit not previously enumerated under S8) and CORS domain configuration for form handlers.
- Agentforce agents (Nurturing, Campaign Creation, Content Builder) sit outside the S1-S21 checklist entirely -- they depend on Einstein + Agentforce being turned on in Setup, which is a separate enablement track from Data 360/MC Next. None of the three agent articles reference Data 360, Data Graphs, or identity resolution.
- Migration work (moving MCE journeys, emails, data) has the clearest dependency chain of the batch: Data 360 enabled and CRM/MCE connectors streaming (S3/S4/S12) → identity resolution run, Unified Individual exists (S10) → Data Graph built including every object templates/flows need (S11) → field map built by humans → template/flow rewrite → validation in the MC Next editor against real test contacts. Skipping the field-map step is explicitly called out as "the reason migrations stall."
- Two independent articles in this batch (the multi-agent orchestration blog, and the AMPscript-to-Data-360 mapping article) both point at Salesforce Setup > MCP Servers > Salesforce Servers > `data-cloud-queries` as a toggle that must be enabled for `d360_metadata` and other Data Cloud API calls made via a Salesforce-hosted MCP server to work. This is a new, more specific candidate cause for our skill's S11 guard-block (`d360:execute:d360_metadata:any`) than anything found in earlier batches: worth checking this Setup toggle on a live org if/when the guard is lifted for that key.

Contradictions between articles: none found. The flows, sites, and migration articles are consistent with each other and with the "Is it worth migrating" article's 60-day plan on sequencing (Data 360 → identity resolution → Data Graph → Flow/personalisation). The Agentforce agent articles do not mention Data 360 setup at all, which is consistent with them being a separate enablement track rather than a contradiction.
