# CRM connector, streams, and DLO-to-DMO mapping

Covers checks S4 (Salesforce CRM connector + bundles) and S21 (custom DMO mappings, e.g. custom objects (e.g. subscription or credit records)).

## Steps

### Standard CRM connector (Sales Bundle)

1. Data 360 app > **Data Streams** tab > New > select **Salesforce CRM** as the Connected Source > Next. [AB:crm-connector-d360] [AB:setup-datacloud-mcn]
2. Select the **Sales Bundle**: Account, User, OpportunityContactRole, Opportunity, Contact, Lead — 6 objects exactly. [AB:setup-datacloud-mcn] [AB:setup-d360]
3. Review objects and fields: standard fields pre-selected by default; custom fields and formula fields must be added manually. Click Next. [AB:setup-datacloud-mcn] [AB:crm-connector-d360]
4. Select the Data Space the stream deploys into. Optionally add filters to scope which records import. Click **Deploy**. [AB:crm-connector-d360]
5. Resulting streams are named with a `_Home` suffix: `User_Home`, `Lead_Home`, `OpportunityContactRole_Home`, `Opportunity_Home`, `Contact_Home`, `Account_Home`, plus `CurrencyType_Home` (auto-added for multicurrency orgs). [AB:setup-datacloud-mcn]

### Custom objects (not in a bundle)

6. Instead of a bundle, select **Objects individually** during Data Stream creation — this is the documented route for custom objects like the org's own objects. [AB:crm-connector-d360]
7. Any field needed for segmentation in MC Next must be explicitly mapped to a DMO field — existing on the Salesforce object is not enough. Example given: only 39 of 71 fields on Contact were mapped by default; the rest needed manual mapping via **Add Source Fields** on the Data Stream, then **Review** to map each field to an existing or new DMO field. [AB:import-customers-mcn]

### DLO-to-DMO mapping (the mechanism behind S21)

8. **A Salesforce CRM stream lands as a DLO only.** A custom object needs an explicit DLO-to-DMO mapping before a graph or segment can use it. This is confirmed in this KB only via the Snowflake ingestion article, not any CRM-specific article: on the Data Stream record, a related list section called **Data Mapping** has a **Start** button. From there, map fields to a new or existing custom DMO (example: custom DMO "Animal", all Animal DLO fields auto-mapped). [AB:snowflake-d360]
9. No article shows this Data Mapping step done via API — UI-only, confirmed across every connector type in this KB (Snowflake, S3, WordPress, GA4, CRM).
10. [FIELD] in a live org, custom DMOs such as `<Custom>__dlm` were created and mapped this way, from CRM streams.

### Alternate ingestion for objects with no native connector

11. **Ingestion API Data Stream**: Data Cloud Setup > Ingestion API tab > New > upload an OpenAPI (OAS) 3.0.1 schema describing the object. Data 360 app > Data Stream > New > Ingestion API Source > select connector + object > select Category (Profile/Engagement/Other) and Primary Key > ingestion mode Upsert (default) > Deploy. Deploying auto-creates the DLO. [AB:ingestion-api-d360]
12. Once created, this is a genuine REST push route: get a Salesforce token, exchange for a Data 360 token, then `POST <host>/api/v1/ingest/sources/<ConnectorName>/<ObjectName>` with `{"data": [...]}`. [AB:ingestion-api-d360]
13. **Generic Data 360 Connector REST API** exists for "Other Connector" types (demonstrated for AWS RDS MySQL): `GET/POST /services/data/v66.0/ssot/connections`. Requires an External Client App with Data 360 scopes (`cdp_api`, `cdp_query_api`, `cdp_profile_api`, `cdp_ingest_api`) and a UI-built connector of the same type first, to copy its schema (matches this project's own platform note: GET a UI-built object first, use it as the template). **Not confirmed for the Salesforce CRM connector or the native MCE connector type** — only for "Other Connectors". [AB:rest-connector-d360]

## Limits

- Sales Bundle = exactly 6 objects (7 streams with CurrencyType_Home).
- Ingestion frequency options for non-CRM connectors range **15 minutes to Weekly** (Snowflake example). [AB:snowflake-d360]
- No numeric field-count limit stated for a Data Stream or a DLO.
- [FIELD] Data Graph limits (not Data Stream limits): 50 fields per object, 200 per graph — see `16_data_graph.md`.

## Gotchas

- Permission set name varies by org vintage (Data Cloud Admin vs Data Cloud Architect) — check both when searching. [AB:setup-datacloud-mcn]
- Custom fields on Sales Cloud objects are NOT ingested unless manually selected during stream setup, even inside a bundle. [AB:setup-datacloud-mcn]
- **No article in this KB shows creating a Salesforce CRM data stream, an MCE connector, an identity resolution ruleset, or a DLO-to-DMO mapping via API** — all confirmed UI-only across the whole corpus. [AB:rest-connector-d360] (cross-cutting, batch C)

## Automation route

- CRM connector creation, bundle/object selection, field review, deploy: **UI-only**.
- DLO-to-DMO mapping (Data Mapping > Start): **UI-only**.
- Ingestion API Data Stream: setup is UI-only, but data push after setup is REST (`/api/v1/ingest/sources/...`).
- Generic "Other Connector" REST API (`ssot/connections`): usable for non-native connector types once a UI-built example exists; not confirmed for CRM/MCE.

## Verification

- Data Streams list view: Data Connector Type = "Salesforce CRM"; presence of `_Home` streams; per stream shows Streaming Type (Ingest), Last Refresh Status, Data Stream Status, Last Processed Record, Total Record, Last Refreshed. [AB:crm-connector-d360]
- Readable via `d360_datastream_list`.
- Data Stream's Data Mapping related list shows the DLO mapped to a DMO with fields matched.
- [FIELD] custom DMOs such as `<Custom>__dlm` exist and are mapped in a live org — confirms this route works end-to-end in this org.

## Sources

[AB:crm-connector-d360] How to configure the Salesforce CRM Connector in Data 360
[AB:setup-datacloud-mcn] How to set-up Data Cloud for Marketing Cloud Next
[AB:setup-d360] How to set-up Data 360
[AB:import-customers-mcn] How to Import Customers into Marketing Cloud Next
[AB:snowflake-d360] How to Ingest Data from Snowflake Into Data 360
[AB:ingestion-api-d360] How to use the Ingestion API Data Stream in Data 360
[AB:rest-connector-d360] How to create a Data 360 Connector with the REST API
[FIELD] observed directly in a live implementation
