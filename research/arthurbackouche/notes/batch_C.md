# Batch C: Data 360 (14 articles)

### How to set-up Data 360
Source: https://arthurbackouche.com/docs/data-360/data-ingestion/how-to-set-up-data-360/
- Purpose: enable Data 360, ingest CRM data, run a basic identity resolution.
- Prerequisites and order dependencies: none before this. This is the entry point. Unblocks: any Data 360 read, Salesforce CRM data stream, identity resolution.
- Steps:
  1. Setup > Permission Sets > select **Data Cloud Architect** > Manage Assignments > add the running user > Assign and Validate.
  2. Refresh the browser. Click the gear icon to find **Data Cloud Set-up**, which opens the Data Cloud Set-up Home page.
  3. In the Data 360 app, open the **Data Stream** app (tab), click **New**, select **Salesforce CRM** as the data stream source.
  4. Select the **Sales Bundle**: Account, User, OpportunityContactRole, Opportunity, Contact, Lead.
  5. Review objects and fields (default fields pre-selected; custom fields can be added later). Click through to the deploy confirmation screen and click **Deploy**.
  6. In Data 360, go to **Identity Resolution**, click **New** > **Create new ruleset** > Next.
  7. Pick a Data Model Object to resolve on (here: **Individual**) and an identifier (article uses "1").
  8. Name and describe the ruleset, Save. "Run jobs automatically" is enabled by default (ongoing schedule).
  9. Click **Configure**, select Matching Rule **Fuzzy Name and Normalized Email**, Next.
  10. Review matching details by DMO/field/method, Next, Save.
- Limits and numbers: none given (no timings, no caps).
- Gotchas and failure modes: permission set must be assigned and the browser refreshed before Data Cloud Set-up appears in the gear menu, otherwise it looks missing.
- Automation route: permission set assignment is CLI-doable (`sf org assign permset`). Everything else (Data Cloud Set-up enablement, data stream creation, identity resolution ruleset) is UI-only per this article; no API mentioned.
- Verification: Data Streams list shows the new Salesforce CRM stream; Identity Resolution page shows Consolidation Rate, Known Unified Profiles, Anonymous Unified Profiles after save.
- Maps to setup checks: S2, S3, S4, S5, S6, S10.

### How to configure the Salesforce CRM Connector in Data 360
Source: https://arthurbackouche.com/docs/data-360/data-ingestion/how-to-configure-the-salesforce-crm-connector-in-data-360/
- Purpose: step-by-step for creating a Salesforce CRM data stream (bundle or individual objects).
- Prerequisites and order dependencies: Data 360 must already be enabled (see "How to set-up Data 360"). Unblocks: any downstream identity resolution or DMO mapping that needs CRM fields.
- Steps:
  1. Data 360 app > **Data Streams** tab > **New**.
  2. Select **Salesforce CRM** as the Connected Source, Next.
  3. Select the **Sales Bundle**, or — important for custom objects — select **Objects individually** instead of a bundle.
  4. Review each object and its field attributes; bundle defaults pre-select standard fields, custom fields must be selected manually, Next.
  5. Select the **Data Space** the stream deploys into. Optionally add filters per data stream to scope which records import. Click **Deploy**.
- Limits and numbers: none given.
- Gotchas and failure modes: none stated explicitly, but the article implies custom fields/custom objects are not included by bundle defaults and must be added by hand.
- Automation route: UI-only per this article. (Cross-reference: the REST API connector article shows a generic `ssot/connections` API exists for "Other Connectors"/custom connector types; this article does not confirm the Salesforce CRM connector itself can be built or edited that way.)
- Verification: Data Streams list view shows, per stream: Data Connector Type (Salesforce CRM), Streaming Type (Ingest), Last Refresh Status (Success/Fail), Data Stream Status (Active/Processing), Last Processed Record, Total Record, Last Refreshed.
- Maps to setup checks: S4 (this is the key article — confirms custom objects are addable via "select Objects individually" rather than only Sales Bundle).

### How to connect Marketing Cloud Engagement to Data 360
Source: https://arthurbackouche.com/docs/data-360/data-ingestion/how-to-connect-marketing-cloud-engagement-to-data-360/
- Purpose: connect an MCE (Engagement) tenant to Data 360 and create MCE data streams.
- Prerequisites and order dependencies: Data 360 enabled. An MCE integration user must exist before starting the wizard. Unblocks: MCE data streams (Email/MobileConnect/MobilePush bundles or individual Data Extensions), and later segment activation back into MCE.
- Steps:
  1. In MCE, create an integration user named **Data360_Connector** with permission sets **Marketing Cloud Administrator** and **Administrator**. If MCE has multiple business units, associate the default parent business unit to this user and tick **API user**.
  2. In Data Cloud Setup, open the **Marketing Cloud Engagement** tab, click **New**. A guided wizard appears with 4 stages: Enter Credentials, Data Source Set-up (Optional), Allow Profile Business Unit Mapping Data, Select Business Units to Activate.
  3. **Enter Credentials**: click **Manage**. Recommend logging in via an incognito window. The MCE login page appears (this is the OAuth/login step) — enter the integration user's credentials there to establish the connection.
  4. **Data Source Set-up**: click **Manage**. Select the MCE Business Units to receive data from, and the Bundles (categories: Email, MobileConnect, MobilePush).
  5. **Select Business Units to Activate**: click **Manage**. Select which Business Units can receive activated data/segments from Data 360.
  6. Create the MCE Data Streams: Data 360 app > **Data Streams** > New > select **Marketing Cloud** > Next.
  7. Choose either a **Bundle** (Email Studio, Mobile Studio, Mobile Push — pre-configured streams and fields) or select **Data Extensions** directly.
  8. Review pre-selected streams and fields per bundle, click **Deploy**.
- Limits and numbers: none given.
- Gotchas and failure modes: the integration user needs both Marketing Cloud Administrator and (system) Administrator permission sets in MCE; multi-BU tenants need the parent BU association and API user flag or the connector setup can misbehave (implied, not stated as an explicit failure).
- Automation route: UI-only. The credential step is a login window (OAuth), described in this skill's Part 2 step F as a stop-and-handback point for the user. No REST/CLI alternative given here for MCE connector creation itself; contrast with the generic REST connector article which covers "Other Connectors" (AWS RDS etc.), not the native Marketing Cloud connector type explicitly.
- Verification: after deploy, the MCE Data Streams list appears in the Data Streams tab of Data 360.
- Maps to setup checks: S12 (primary — this is the special-focus article: order is Enter Credentials -> Data Source Set-up -> Select Business Units to Activate, then separately create Data Streams from a Bundle or individual DEs).

### Understanding Party identification in Data 360 for Marketing Cloud Engagement
Source: https://arthurbackouche.com/docs/data-360/data-unification/understanding-party-identification-in-data-360-for-marketing-cloud-engagement/
- Purpose: explain the Party Identification DMO and how to unify/cross-reference individuals with MCE Subscriber Keys.
- Prerequisites and order dependencies: requires MCE already connected and ingested (references the MCE connector article). Feeds into identity resolution and segment activation back to MCE.
- Steps (conceptual + practical):
  1. Understand the "Party" area of the Customer 360 Data Model: DMOs storing information about Individuals (who they are, how to identify them, how to contact them).
  2. Party Identification DMO links external-platform identifiers (UID) to the Individual DMO. Key fields: **Individual ID**, **Identification Type**, **Identification Number**.
  3. All Party-area DMOs are many-to-one with Individual: one Individual can have many Party Identifications, many Contact Point Emails, many Contact Point Phones, many Contact Point Addresses.
  4. When the MCE Bundle is ingested, a data stream named **"SFMC Ent Profile Attribute"** ingests individuals and party info automatically, letting you segment on "Identification Name = MC Subscriber Key".
  5. Alternative for custom Data Extensions (e.g. Master Subscribers DE): create formula fields on the DLO:
     - `Party Identification Type` = `Person Identifier`
     - `Party Identification Name` = `MC Subscriber Key`
     - `Party Identification Id` = `'PersonIdentifier_MCSubKey_' + sourceField['SubscriberKey field']`
     Then map these formula fields to the Individual and Party Identification DMOs.
  6. To unify individuals on Subscriber Key, create a new Identity Resolution ruleset with a custom match rule named **"MC Subscriber Key"**: Condition = Party Identification > Identification Number > Exact; Party Identification Type = Person Identifier; Party Identification Name = MC Subscriber Key.
  7. When activating individuals into MCE, filter Activation on Identification Name = MC Subscriber Key to correctly match individuals that already exist in MCE.
- Limits and numbers: activating a Data 360 segment into MCE "can take up to 30 min". (Contradicts the Activation article below, which says up to 24 hours — see cross-cutting findings.)
- Gotchas and failure modes: if you skip the formula-field/DLO-mapping step for custom Subscriber DEs, individuals from that DE will not carry a Party Identification linking them back to MCE, and Subscriber-Key-based segment filters or unification will not work for those records.
- Automation route: formula fields on a DLO and the mapping to DMOs are described as UI actions ("mapping these formula fields to the Individual and Party Identification Data Model Objects"); no API given. UI-only per this article.
- Verification: segment query "Identification Name = MC Subscriber Key" returns the expected individuals; identity resolution consolidation stats reflect the new custom match rule.
- Maps to setup checks: S10, S12 (this is the key article for open item S12/DLO-DMO mapping for custom objects and for identity resolution against MCE-sourced data).

### How to create a Data 360 Connector with the REST API
Source: https://arthurbackouche.com/docs/data-360/data-ingestion/how-to-create-a-data-360-connector-with-the-rest-api/
- Purpose: build a Data 360 "Other Connector" (example: AWS RDS MySQL) via REST API instead of the UI wizard, once its schema is known from a UI-built example.
- Prerequisites and order dependencies: an External Client App must exist for OAuth first. At least one connector of the same connector type should already exist, built via the UI, to capture its schema (matches this skill's documented behaviour: "GET a UI-built object first and use it as the template").
- Steps:
  1. Setup > **External Client App** > New. Name `api_connector_d360`, API name same, Contact Email, Distribution State **Local**.
  2. Enable OAuth: True. Callback URL `http://localhost:3000/oauth/callback`. OAuth Scopes: `api`, `refresh_token`, `offline_access`. Enable Client Credentials Flow: True. Require secret for Web Server Flow: True. Require secret for Refresh Token Flow: True. Require PKCE: True.
  3. Add Data 360 scopes: `cdp_api`, `cdp_query_api`, `cdp_profile_api`, `cdp_ingest_api`. Click Create.
  4. On the app's **Policies** tab, Edit: set Permitted Users = "Admin approved users are pre-authorized"; under OAuth Flows and External Client App Enhancements, add your username.
  5. On **Settings** tab, view Consumer Key and Secret.
  6. In Postman, POST `https://<Domain>.my.salesforce.com/services/oauth2/token` with `grant_type=client_credentials`, `client_id`, `client_secret` (Content-Type: `application/x-www-form-urlencoded`) to get a Salesforce access token.
  7. POST `https://<Domain>.sandbox.my.salesforce.com/services/a360/token` with `grant_type=urn:salesforce:grant-type:external:cdp`, `subject_token=<SF access token>`, `subject_token_type=urn:ietf:params:oauth:token-type:access_token`, `dataspace=default` to get a Data 360 access token.
  8. Sanity check: POST `https://<Data360InstanceURL>.c360a.salesforce.com/api/v2/query` with header `Authorization: Bearer <Data360 token>`, body `{"sql": "SELECT 1"}`.
  9. GET existing connectors of a type: `GET https://<SalesforceOrg>/services/data/v66.0/ssot/connections?connectorType=AwsRdsMySql`.
  10. GET a specific connector's schema/template: `GET https://<SalesforceInstanceDomain>/services/data/v66.0/ssot/connections/<ConnectorID>`.
  11. POST to create a new connector: `POST <SalesforceDomain>/services/data/v66.0/ssot/connections` with body containing `connectorType`, `label`, `name`, `method` ("Ingress"), `credentials[]`, `parameters[]` (e.g. `jdbc_connection_url`, `DATABASE`).
- Limits and numbers: none given.
- Gotchas and failure modes: none explicit; implicitly, you need a UI-built connector of the same type first to know the correct body shape (documented field names are not published/reliable — matches this skill's platform-behaviour note).
- Automation route: this entire flow IS the automation route. **CLI/API-capable**: External Client App creation is normally Setup UI, but the connector itself (`ssot/connections` REST endpoint) is create/list/get-able via REST once auth is set up. This is the strongest evidence of a non-UI route in this batch, but it is demonstrated only for "Other Connectors" (AWS RDS MySQL), not for the Salesforce CRM connector or the native Marketing Cloud Engagement connector.
- Verification: GET `/services/data/v66.0/ssot/connections?connectorType=...` returns the new connector; Data Cloud Setup > Other Connectors shows it in the UI.
- Maps to setup checks: S3, S4 (partially — REST route exists for generic connectors, not confirmed for CRM/MCE connector types), open item (4).

### How to use the Ingestion API Data Stream in Data 360
Source: https://arthurbackouche.com/docs/data-360/data-ingestion/how-to-use-the-ingestion-api-data-stream-in-data-360/
- Purpose: build a custom data stream backed by a REST Ingestion API (for sources with no native connector) and push records to it.
- Prerequisites and order dependencies: an External Client App for auth (cross-references the REST connector article). Unblocks: pushing arbitrary JSON records into a new DLO from any external system without a native connector.
- Steps:
  1. Data Cloud Setup > **Ingestion API** tab > New. Name it (e.g. `Data-360-Connector`).
  2. Upload an OpenAPI (OAS) 3.0.1 schema file describing the object structure (example: a `Customer` object with `email`, `firstName`, `lastName`). Confirm the read structure. Save.
  3. Data 360 app > **Data Stream** tab > New > select **Ingestion API Source** > Next.
  4. Select the Ingestion API connector just created and the Object defined in the schema (e.g. Customer).
  5. Select the Category (e.g. Profile) and the Primary Key (e.g. email).
  6. Select ingestion mode: **Upsert** (default, adds on top) or other. Optionally select Data Space and a filter. Click **Deploy**.
  7. Deploying auto-creates the Data Lake Object (DLO), e.g. `Data-360-demo-Customer`.
  8. Get a Salesforce access token: `POST https://<domain>.my.salesforce.com/services/oauth2/token` (`grant_type=client_credentials`, `client_id`, `client_secret`).
  9. Get a Data 360 token: `POST https://<domain>.my.salesforce.com/services/a360/token` (`grant_type=urn:salesforce:grant-type:external:cdp`, `subject_token=<SF token>`, `subject_token_type=...access_token`, `dataspace=default`).
  10. Download "Download All Object Endpoints" file from the Ingestion API connector to get the ingest host, e.g. `https://<host>.c360a.salesforce.com`.
  11. POST records: `POST <host>/api/v1/ingest/sources/<ConnectorName>/<ObjectName>` header `Authorization: Bearer <Data360 token>`, body `{"data": [{...}]}`.
- Limits and numbers: none given.
- Gotchas and failure modes: none explicit.
- Automation route: this is a fully API-driven ingestion path (OAS schema upload is UI, but data push is REST). Useful pattern for client custom objects that have no native connector, though the schema/connector/data-stream creation steps themselves are shown only via the UI in this article (OAS upload happens "within the API Ingestion Connector" in Setup).
- Verification: Data Explorer > select the Data Lake Object created (e.g. Customer) and see the pushed record.
- Maps to setup checks: S4 (alternate ingestion route for custom data with no connector), open item (4).

### How to Activate a Data 360 Segment into Marketing Cloud Engagement
Source: https://arthurbackouche.com/docs/data-360/data-activation/how-to-activate-a-data-360-segment-into-marketing-cloud-engagement/
- Purpose: push a Data 360 segment into MCE as a usable list/segment.
- Prerequisites and order dependencies: requires the MCE connection already created (references the MCE connector article, S12) and a Data 360 segment already built.
- Steps:
  1. Data 360 > **Segments** > create new segment.
  2. Data 360 > **Activation Targets** > New > select **Marketing Cloud Engagement** > Next.
  3. Fill Activation Target Name, Description, Space (Default), then select the connection created earlier and the Business Unit that can access the segment.
  4. Data 360 > **Activation** tab > New > select **Segment**.
  5. Select Data Space (default), the Segment, the Activation Target, and **Activation Membership**: Unified Individual or Individual.
  6. Select how Data 360 prioritises identifying the customer (e.g. Email -> highest click score).
  7. Optionally filter data to be activated.
  8. Name and describe the Activation, choose refresh type: **Incremental (Append)** or **Full Refresh (Overwrite)**. Save.
  9. Check MCE: the segment appears in a folder there.
- Limits and numbers: "it can take up to 24 Hours when initiating the process" for the segment to appear in MCE.
- Gotchas and failure modes: none explicit beyond the delay.
- Automation route: UI-only per this article.
- Verification: segment folder visible in MCE containing the activated members.
- Maps to setup checks: S12 (downstream of the connector setup).

### How to create a Calculated Insight for Email Engagement in Data 360
Source: https://arthurbackouche.com/docs/data-360/data-analytics/how-to-create-a-calculated-insight-for-email-engagement-in-data-360/
- Purpose: build a SQL-based Calculated Insight scoring email engagement from MCE-ingested data.
- Prerequisites and order dependencies: MCE must already be connected and Email data ingested (references the MCE connector article). Confirms the DMO name `ssot__EmailEngagement__dlm` used in S8 checks is real, plus field `ssot__IndividualId__c` and `ssot__EngagementChannelActionId__c`. Unblocks: reporting, segmentation/activation filters, and Copy Field Enrichment back to CRM Contact.
- Steps:
  1. Data 360 > **Calculated Insights** > New > select Calculated Insight, **Use SQL Authoring** > Next.
  2. Name it (e.g. "Email Engagement Score").
  3. Paste SQL querying `ssot__EmailEngagement__dlm`, grouped by `ssot__IndividualId__c`, summing weighted scores per `ssot__EngagementChannelActionId__c` value (Open +5, Click +10, Bounce -15, Unsubscribe -25), plus counts of opens/clicks.
  4. Set a refresh schedule (example: every 24 hours). Click Enable.
  5. Once Active, click **Create Report** to visualise scores per Unified Individual.
  6. Optionally add the score to a Contact/Lead Salesforce page: edit page, add **Data Cloud Profile Insight** widget/LWC, select the Calculated Insight.
- Limits and numbers: example schedule "every 24 hours" (configurable, not a hard limit).
- Gotchas and failure modes: none explicit; the SQL depends on the `ssot__EmailEngagement__dlm` DLM/DLO existing, i.e. it depends on the MCE Email data stream/bundle already being deployed.
- Automation route: SQL authoring happens through the Data 360 Calculated Insights UI; the SQL itself could plausibly run through the Data 360 query API for read purposes, but this article does not describe creating the Calculated Insight object via API. UI-only per this article for creation; SQL query mechanism matches the `d360_query_sql`-style tool used elsewhere in this project.
- Verification: report shows EngagementScore__c, TotalOpens__c, TotalClicks__c per individual; LWC widget on Contact/Lead page shows the score once configured.
- Maps to setup checks: S8 (confirms DLM name), S18/S19 (feeds analytics/reports).

### How to Set up the Intelligence Reports in Data360
Source: https://arthurbackouche.com/docs/data-360/data-analytics/how-to-set-up-the-intelligence-reports-in-data360/
- Purpose: install a pre-built AppExchange reporting package for MCE metrics inside Data 360.
- Prerequisites and order dependencies: requires the MCE connector configured and the Email Studio and Mobile Studio Bundle data streams already deployed.
- Steps:
  1. Setup > search **AppExchange**.
  2. Search for **"Data Cloud Report Package for Marketing Cloud Engagement"** (by Salesforce Labs), click **Get It Now**.
  3. Select **Install for Admins Only**, click **Install**.
  4. In Data 360, open the **Report** tab, folder **"Data Cloud Report Installed"** to see the reports: Email Send Report, Email Performance Report, Email Bounce Summary Report, Email Domain Performance Report, Email Spam Complaint Report.
- Limits and numbers: none given.
- Gotchas and failure modes: package requires the underlying MCE bundles to already be ingested or reports will have no data (inferred).
- Automation route: AppExchange package install is UI-only in this article (no CLI package-install command given, though `sf package install` generally exists for this purpose outside this article's scope — not confirmed here).
- Verification: reports appear and populate in the Data Cloud Report Installed folder.
- Maps to setup checks: S18, S19.

### How to configure the Amazon S3 Connector in Data 360?
Source: https://arthurbackouche.com/docs/data-360/data-ingestion/how-to-configure-the-amazon-s3-connector-in-data-360/
- Purpose: ingest a CSV file from an S3 bucket into a new DLO.
- Prerequisites and order dependencies: AWS account, S3 bucket, IAM user with policy. Not part of the CRM/MCE chain; independent connector type.
- Steps:
  1. Create an S3 bucket and a folder inside it.
  2. AWS IAM > create user, name it, choose "Attach policies directly", create a custom policy (deny non-SSL access; allow GetBucketLocation/ListBucket/GetObject/PutObject/GetObjectTagging/DeleteObject scoped to the bucket ARN).
  3. Create an Access Key for the IAM user (choose "Other" use case).
  4. Data Cloud Setup > **Other Connectors** > New > select **Amazon S3** > Next.
  5. Enter Access Key and Bucket Name, **Test Connection**, Save. Status starts Processing then becomes Active.
  6. Data 360 app > Data Streams > New > select Amazon S3 > Next.
  7. Specify the S3 folder, file type, file name, Next.
  8. Create a new **Data Lake Object** for the target: define DLO name, **Data Lake Object Type** (Profile, Engagement, Other) and **Primary Key**.
  9. Define refresh type: **Upsert** (adds on top per schedule) or **Full Refresh** (erase and reload). Click Deploy.
- Limits and numbers: example ingested 5,379 records in one run (illustrative, not a cap).
- Gotchas and failure modes: none explicit.
- Automation route: UI-only per this article for both AWS IAM setup and the Data 360 connector/stream steps.
- Verification: Data Stream list shows Total Record count; Data Explorer can preview the new DLO.
- Maps to setup checks: S4 (general DLO-creation pattern: Data Lake Object Type + Primary Key selection applies to any custom-object stream, useful analog for client custom objects).

### How to Ingest Data from Snowflake Into Data 360
Source: https://arthurbackouche.com/docs/data-360/data-ingestion/how-to-ingest-data-from-snowflake-into-data-360/
- Purpose: connect Snowflake and ingest tables, then map a DLO to a custom DMO.
- Prerequisites and order dependencies: a Snowflake account/warehouse with tables to ingest. Independent of CRM/MCE chain but is the clearest example in this batch of DLO-to-custom-DMO mapping.
- Steps:
  1. Setup > search **Snowflake** > New > select **Snowflake Connection** > Next.
  2. Enter Connection Name, Connection API Name, Account URL, Username, Private Key. Next.
  3. Select Warehouse and Region (region auto-populated from Account URL). Save. Connector becomes Active.
  4. Data 360 app > Data Streams tab > select the Snowflake connector > Next.
  5. Select the database and objects to ingest (example: ANIMAL, CONTACT tables). Next.
  6. Per object: select fields to ingest, set Category type (**Profile, Engagement, Other**), and Primary Key. Next.
  7. Review objects, select Data Space (Default) and ingestion **Frequency** (options from **15 minutes to Weekly**). Click Deploy.
  8. Map the new DLO to a DMO: on the Data Stream's related list, click **Start** under the **Data Mapping** section. Example: created a custom DMO "Animal" and automatically mapped all Animal DLO fields to it.
- Limits and numbers: ingestion frequency options range **15 minutes to Weekly**.
- Gotchas and failure modes: none explicit.
- Automation route: UI-only per this article, including the DLO-to-DMO mapping step ("Start" button on the Data Stream related list). No API given for creating a custom DMO or its field mappings.
- Verification: Data Streams tab shows the 2 new streams; the Data Mapping section on the stream shows the DLO mapped to the DMO with fields matched.
- Maps to setup checks: S4, S21 (this is the best available answer to open item (3): DLO-to-DMO mapping is done via the "Data Mapping" section on the Data Stream record, click Start, map fields to a new or existing custom DMO). Directly informs S21 (custom DMO mappings for custom objects (e.g. subscription or credit records)).

### How to ingest Google Analytics into Data 360
Source: https://arthurbackouche.com/docs/data-360/data-ingestion/how-to-ingest-google-analytics-into-data-360/
- Purpose: connect GA4 and ingest web engagement data.
- Prerequisites and order dependencies: a GA4 property and Google account with access. Independent of CRM/MCE.
- Steps:
  1. Data Cloud Setup > **Other Connectors** > New > search **"Google Analytics for MI"** > Next.
  2. Name the connector, select External Auth Identity Provider "Google Analytics for MI", click **Authenticate**, sign in with Google, click Continue.
  3. In GA4, find the website's Property ID; paste it into the connector, **Test the Connection**, confirm "Connection was established", Save. Connector becomes Active.
  4. Data 360 app > Data Streams > New > select the Google Analytics MI connector > Next.
  5. Select all 4 objects: Web Analytics Pages View, Web Analytics Events View, Web Analytics View, Google Website Analytics.
  6. Define the DLO for each object with Category **Engagement** and select fields. Deploy.
  7. Preview via **Data Explorer**, selecting the relevant DLO.
- Limits and numbers: none given.
- Gotchas and failure modes: none explicit.
- Automation route: UI-only per this article (OAuth sign-in step cannot be scripted).
- Verification: Data Explorer preview of the DLO shows ingested rows.
- Maps to setup checks: S4 (general connector pattern; not CRM-specific).

### How to ingest Wordpress into Data 360
Source: https://arthurbackouche.com/docs/data-360/data-ingestion/how-to-ingest-wordpress-into-data-360/
- Purpose: connect a WordPress site and batch-ingest content objects.
- Prerequisites and order dependencies: a WordPress admin user for the integration. Independent of CRM/MCE.
- Steps:
  1. In WordPress, create an admin-level integration user, e.g. `data360-connector`.
  2. Data Cloud Setup > Other Connectors > New > select **WordPress** > **Basic Auth** > enter username, password, site URL, **Test**, Save.
  3. Data 360 app > Data Streams > New > select the WordPress connector > **Batch** mode.
  4. Select objects: Categories, Docs, Media, Pages, Posts, Tags.
  5. For each object: Category = **Other**, Primary Key = **Id**, Data Model Object category = **Other**, select all fields.
  6. Set schedule to **Daily**, Deploy.
  7. Preview via Data Explorer, selecting a WordPress DLO (example: WordPress Pages).
- Limits and numbers: schedule set to Daily in the example (not stated as a hard limit); "under 10 minutes" claimed for the whole setup (article's own estimate, not a platform limit).
- Gotchas and failure modes: none explicit.
- Automation route: UI-only per this article.
- Verification: Data Explorer preview of the WordPress DLO shows ingested content.
- Maps to setup checks: S4 (general connector/DLO pattern; not CRM-specific).

### How to connect Claude to Data 360 via MCP Servers
Source: https://arthurbackouche.com/docs/data-360/mcp/how-to-connect-claude-to-data-360-via-mcp-servers/
- Purpose: set up an External Client App and MCP server config so Claude can query Data 360 directly.
- Prerequisites and order dependencies: Data 360 already enabled. Independent of the CRM/MCE ingestion chain; this is tooling/access setup, not data setup.
- Steps:
  1. Setup > **External Client App Manager** > New External Client App.
  2. Name `ClaudeMcpConnector`, Contact Email, Distribution State Local, Enable OAuth True, Callback URL `https://claude.ai/api/mcp/auth_callback`.
  3. Select scopes: `refresh_token`/`offline_access`, `mcp_api` (Access Salesforce hosted MCP servers), `data_cloud_user_claims`, `cdp_api`, `interaction_api`, `sfap_api`, `cdp_calculated_insight_api`, `cdp_identityresolution_api`, `cdp_segment_api`, `cdp_profile_api`, `cdp_ingest_api`, `api`.
  4. Security: enable **PKCE**, and **Issue JWT-based access tokens for named users**. Click Create.
  5. Settings tab > Consumer Key and Secret. Also enable **Client Credentials Flow** for the named user.
  6. Setup > **MCP Servers** > **Salesforce Servers** tab > enable **data-cloud-queries** (article also enabled `sobject-all`).
  7. Setup > **OAuth and OpenID Connect Settings** > enable "Require PKCE Extension for Supported Authorization Flows".
  8. In Claude Console, Credential vaults > Add credential: Name, MCP Server URL `https://api.salesforce.com/platform/mcp/v1/data/data-cloud-queries`, Client ID, Client Secret, Connect.
- Limits and numbers: none given.
- Gotchas and failure modes: matches this project's own platform-behaviour note: "Connector tool lists bind at session start. After fixing auth, restart the session."
- Automation route: External Client App creation is Setup UI; the MCP server enablement is Setup UI ("MCP Servers" tab); Claude-side credential registration is via Claude Console UI. No CLI route given.
- Verification: Claude Console shows the connector as connected; d360 tool calls succeed.
- Maps to setup checks: S3 (confirms Data 360 accessible), tooling/agent-access setup rather than a numbered S-check directly.

## Batch C cross-cutting findings

Canonical Data 360 order, reconstructed from this batch:
1. Assign **Data Cloud Architect** permission set to the running user (S2/S5/S6), refresh browser to reveal Data Cloud Set-up.
2. Enable Data 360 / Data Cloud Set-up (S3).
3. Create the **Salesforce CRM connector** and its Data Stream (Sales Bundle, or individual objects for custom objects) (S4).
4. Run **Identity Resolution** (create ruleset, e.g. Fuzzy Name + Normalized Email match rule, on Individual DMO) (S10).
5. Connect **Marketing Cloud Engagement**: create integration user in MCE first, then in Data Cloud Setup MCE tab: Enter Credentials -> Data Source Set-up (bundles: Email/MobileConnect/MobilePush) -> Select Business Units to Activate; then separately create MCE Data Streams (bundle or individual DE) (S12).
6. For MCE-sourced individuals to unify correctly, either rely on the auto-created "SFMC Ent Profile Attribute" stream, or, for custom Subscriber DEs, add formula fields (Party Identification Type/Name/Id) on the DLO and map them to Individual + Party Identification DMOs, then add a custom identity-resolution match rule on Subscriber Key (S10/S12/S21).
7. For any custom object/DLO (Snowflake, S3, WordPress, GA4, Ingestion API), map the DLO to a DMO via the **Data Mapping** section ("Start" button) on the Data Stream record; create a custom DMO if none exists (S4/S21).
8. Build Calculated Insights (e.g. `ssot__EmailEngagement__dlm`-based scoring) once source DLMs exist (S8/S18).
9. Install the AppExchange "Data Cloud Report Package for Marketing Cloud Engagement" for pre-built reports, once MCE bundles are ingested (S18/S19).
10. Build Segments, Activation Targets, and Activations to push Data 360 segments back into MCE (downstream of S12).

Answers to the special-focus open items:
1. (S12, MCE connection) After OAuth/credential entry, the wizard has two more explicit stages: **Data Source Set-up** (pick MCE business units to ingest from + bundle categories Email/MobileConnect/MobilePush) and **Select Business Units to Activate** (pick BUs allowed to receive activation data). Data Streams (bundle or individual DE) are created as a separate step afterward, not part of the connector wizard itself.
2. (S4, custom objects) The Salesforce CRM Connector article confirms bundles are optional: "there is also the possibility to select Objects individually" — this is the route for client custom objects not in the Sales Bundle.
3. (DLO-to-DMO mapping for custom objects) Confirmed only via the Snowflake article: on the Data Stream record, a "Data Mapping" related section has a **Start** button; from there a new or existing custom DMO can be selected/created and fields mapped (example: custom DMO "Animal"). No article gives an API for this mapping step.
4. (API/CLI route avoiding the UI wizard) Two REST routes exist: (a) the generic Data 360 Connector REST API (`/services/data/v66.0/ssot/connections`) for GET/POST of "Other Connector" types once a UI-built example exists to copy its schema from — demonstrated for AWS RDS MySQL, not confirmed for Salesforce CRM or native MCE connector types; (b) the Ingestion API Data Stream, which is UI-created once but then accepts data pushes via plain REST POST (`/api/v1/ingest/sources/<name>/<object>`), useful for custom objects that have no native connector. No article shows creating a Salesforce CRM data stream, an MCE connector, an identity resolution ruleset, or a DLO-to-DMO mapping via API — all of those remain UI-only in this batch.

Contradictions between articles:
- Segment activation into MCE timing: the Party Identification article states activation "can take up to 30 min"; the dedicated Activation article states "it can take up to 24 Hours when initiating the process." Treat 24 hours as the safer planning number since it comes from the article dedicated to that exact procedure; flag the 30-minute figure as unreliable.
- No other direct contradictions found between the 14 articles in this batch; ingestion-frequency figures (15 min to Weekly for Snowflake, Daily for WordPress, 24 hours for the Calculated Insight refresh) are per-source examples, not conflicting platform limits.
