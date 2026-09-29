---
name: mce-to-data360-mapper
description: Inventory a Data 360 (Data Cloud) tenant's DMOs and a Marketing Cloud Engagement tenant's data extensions, then produce a tiered MCE-to-Data 360 ingestion and mapping plan for a Marketing Cloud Next migration. Use whenever the user asks to pull, list, audit, visualise or map DMOs, data model objects, data extensions, DEs, fields or attributes across Data 360 / Data Cloud / MCE / SFMC, asks "what should we ingest into Data Cloud", "map our data extensions to the Customer 360 model", "standard vs custom DMO", or wants a migration data plan for MC Next / Growth / Advanced. Trigger even if only one side (D360 or MCE) is mentioned; the inventory steps run independently. Requires the Data 360 Connect API connector (d360_* tools via execute/search) and the Marketing Cloud Engagement connector (sfmc_soap_retrieve).
---

# MCE to Data 360 mapper

Three stages, each producing a file the client keeps. Run all three for a migration plan; run only the
first or second when the user just wants an inventory. Every stage ends with an inline layer diagram.

Outputs, always, with the client name as prefix:
- `<Client>_D360_DMO_summary.csv`, `<Client>_D360_DMO_field_inventory.csv`
- `<Client>_SFMC_DE_summary.csv`, `<Client>_SFMC_DE_field_inventory.csv`
- `<Client>_MCE_to_Data360_Mapping.xlsx` (five tabs: strategy, DE mapping, field mapping, custom DMO spec, gaps)
- One Visualizer diagram per stage (see `references/diagram_template.md`)

Work in `out/data/work/` inside the engagement folder. Final deliverables go to `out/data/`.

## Stage 1: Data 360 DMO inventory

Connector reality check first. The Data 360 Connect API connector (tools reached through `execute`,
`search`, `payload_examples`) has no SOQL and no `getUserInfo`. `MktDataModelObject` is a Tooling API
entity and returns `INVALID_TYPE` through any sObject endpoint. Do not try. The full DMO catalogue with
fields, types, categories and primary keys comes from one call:

```
execute(toolName="d360_metadata", paramsJson="{}")
```

The result is large. Save the tool result to `out/data/work/` and parse it, never read it inline:

```
python3 scripts/parse_d360_metadata.py <tool_result.json> out/data/work --prefix <Client>
```

The script writes both CSVs and prints a JSON summary. Read the summary for findings worth surfacing:
`no_pk`, `zero_fields`, `duplicate_env_twins` (e.g. `_UAT2` copies), `demo_rulesets` (`Unified*Demo__dlm`
means two identity rulesets are live), `typing_flags` (booleans as TEXT, DOB as NUMBER). Lead the
reply with three or four of these. Counts alone are not an insight.

If the user also asks for identity (`getUserInfo`) use the *platform* sObject connector for the same org
(the one whose URL ends `/platform/sobject-all`), not the Data 360 connector.

## Stage 2: MCE data extension inventory

Three SOAP retrieves through the Marketing Cloud Engagement connector. If a second connector for the
same tenant appears with an `/oauth/callback` URL, it has no tools; use the one whose tools resolve.

1. All DEs: `sfmc_soap_retrieve(object_type="DataExtension", properties=[ObjectID, CustomerKey, Name, CategoryID, IsSendable, CreatedDate, ModifiedDate])`
2. Folder tree: `sfmc_soap_retrieve(object_type="DataFolder", properties=[ID, Name, "ParentFolder.ID", ContentType], filter={property: ContentType, operator: equals, value: dataextension})`
3. Fields for the shortlist only, in batches of about 40 customer keys:
   `sfmc_soap_retrieve(object_type="DataExtensionField", properties=[Name, FieldType, MaxLength, IsPrimaryKey, IsRequired, Ordinal, "DataExtension.CustomerKey"], filter={property: "DataExtension.CustomerKey", operator: IN, values: [...]})`

Batch size matters. Under about 30 keys the result returns inline and floods context with SOAP XML.
Over 40 it is stored to a file, which is what you want. Check `OverallStatus` is `OK` and watch for
`MoreDataAvailable`; the DE list in a mature tenant runs to 800+ rows and can page.

Parse and shortlist:

```
python3 scripts/parse_sfmc_soap.py des     <de_result.json>     > work/de_list.json
python3 scripts/parse_sfmc_soap.py folders <folder_result.json> > work/folders.json
python3 scripts/shortlist_des.py work/de_list.json work/folders.json > work/shortlist.json
python3 scripts/parse_sfmc_soap.py fields <batch1.json> <batch2.json> ... > work/fields.json
```

`shortlist_des.py` is where "useful and main" is decided. Defaults keep `_Master`, System, Journeys,
Transactional, Reporting and a whitelist of root-level platform DEs (Personalization `IGO_`/`PI_`,
Einstein scores, `_Mobile*`/`_Push*`/`_WhatsApp*` channel tables). Defaults drop dated campaign
folders, Test, Archive, IP warming, QueryStudio results, `_DeleteTracking_*`, `APIEvent*`, triggered-send
DEs with timestamp suffixes, `_TEMP`, `_Backup`, migration result tables and `_stg` twins. Print the
per-folder counts to the user before fetching fields and ask if the cut looks right when the taxonomy
differs from the defaults. Pass a config JSON to override `include_top`, `root_keep`, `exclude_name`,
`exclude_path`.

Findings that recur in SFMC estates and are worth checking every time: DEs with no primary key (cannot
be streamed or upserted), key spelling variants (`PetID`/`PetId`/`PETID`), booleans and dates typed Text,
`Has_passed_away` or similar sensitive flags typed Text, email and phone fields typed Text.

## Stage 3: Mapping plan

```
python3 scripts/build_mapping.py work/shortlist.json work/fields.json out/data/work --prefix <Client>
```

This writes the SFMC CSVs and the mapping workbook using `scripts/mapping_rules.json`. The rules encode
the strategy; read them before running so you can explain and adjust them:

**System of record first.** SFMC copies of CRM or source-system master data are tier A, reconcile only.
Re-ingesting them makes identity resolution reconcile SFMC against itself.

**Ingest what SFMC owns.** Consent and subscription state, bounces, journey entry and send history,
Einstein scores, marketing-acquired leads, Personalization behaviour. Email and SMS tracking events are
already flowing through the MCE starter bundle; never add DE streams for them.

**Standard DMO by default, four custom DMOs at most.** `Journey_Entry__dlm` and `Journey_Send_Log__dlm`
(Engagement), `Einstein_Engagement_Score__dlm` (Profile), `Marketing_Exclusion__dlm` (Other). Dozens of
journey DEs collapse into these two engagement DMOs via one SFMC SQL union each, which also fixes the
missing-primary-key problem and avoids one data stream per journey.

**Reporting DEs are not ingested.** Rebuild as Calculated Insights.

Tier rules match in order on DE name and folder path; the first hit wins. Field rules match on field name
and point at standard `ssot__` fields (see `references/c360_targets.md`). Anything on a custom-DMO DE
becomes a `snake_case__c` custom attribute; anything unmatched on a standard-DMO DE is flagged
"custom attribute or drop". Tune the tier and field regexes to the client's naming conventions in `mapping_rules.json` before running; the structure stays.

Validate target field names against the Stage 1 inventory. Clients extend standard DMOs, and a field that
exists in the documentation may not exist in their tenant (`ssot__PartyIdentification__dlm` is often absent).

## Identity and the one gap to always name

The SFMC party key (`ContactID` / `SubscriberKey`) is usually the CRM Contact Id. If so, map it to the same
`ssot__Individual__dlm.ssot__Id__c` the CRM connector populates and no new match rule is needed. State
this explicitly; it removes the biggest perceived risk of the migration.

Secondary entity keys (pet, vehicle, policy, product) almost never align: SFMC holds the CRM id, Data 360
holds the source-system id. Name the crosswalk DMO that must exist before any attribute of that entity
is mapped, and which journeys are blocked until it does.

## Reply shape

Short. Lead with the number of objects and fields, then three or four findings that change a decision,
then the diagram, then the files. Offer one concrete next step (Connect API payloads for the custom DMOs
and union DEs is the natural one). No tables of every object; the CSV holds that.
