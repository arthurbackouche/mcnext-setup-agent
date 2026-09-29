# Data 360 enablement and Basic Settings

Covers checks S3 (Data 360 instance enabled), S7 (Marketing Cloud enabled via Basic Settings), S9 (data space selected).

## Steps

1. Setup > Data Cloud Setup > click **Get Started**. Automatic sub-steps: creating the Data Cloud instance, setting up metadata, initialising the Customer 360 Data Model, readiness check. This is the true first step of the whole MC Next journey — before Basic Settings, Data Kits, Identity Resolution. [AB:setup-datacloud-mcn] [AB:setup-d360]
2. Assign Data Cloud Architect/Admin permission set (see `10_permissions_users.md`) before or immediately after this — some articles assign first, some enable first. Refresh the browser after assigning; the gear-icon menu will not show Data Cloud Setup until refreshed. [AB:setup-d360]
3. Setup > Assistant Home > **Basic Settings** has 3 steps in this order: Enable Data Cloud (6-item checklist), Install the Marketing Data Kits, Configure Identity Resolution Rulesets. [AB:setup-mcn]
4. The "Enable Data Cloud" checklist inside Basic Settings has 6 click-to-Enable items: Create a Salesforce CRM Connector, Add a Default Email Channel, Add Data Protection Details to Records, Select a Data Space, Enable Marketing Cloud. (Article text lists 5 named items plus the connector = 6 total; treat "Create Salesforce CRM Connector" as item 1.) [AB:setup-mcn] [AB:configure-mcn]
5. Select a Data Space — "Default" is used in every worked example in this KB. [AB:configure-mcn] [AB:setup-d360]
6. Click **Enable Marketing Cloud** last in the checklist, once the connector, email channel, data protection details, and data space are done.
7. Basic Settings only appears in Assistant Home once Data Cloud (Data 360) is already enabled — it is gated on step 1. [AB:setup-mcn]

## Data space guidance (S9)

- One article gives concrete planning guidance not found elsewhere in this KB: recommend **1:1 mapping of each MCE Business Unit to one Data Space**, starting with just one or two BUs tied to the first use case. [AB:worth-migrating-mcn]
- **Business Unit to Data Space mapping is effectively permanent.** You cannot uninstall the Marketing app from a Data Space once installed. Mapping several MCE BUs into one Data Space and later removing one deletes all historical data for that BU in the Data Space, breaking every dependent report/segment/Flow. Start narrow; adding mappings later is easy, removing is not. [AB:worth-migrating-mcn]
- Install the Marketing app into a production-grade BU, not a test BU. Use sandbox orgs for testing instead. [AB:worth-migrating-mcn]

## Limits

- No numeric limit given for Data 360 instance enablement time (the enablement wizard itself is described as largely automatic).
- No article states which data space a fresh org defaults to, or how many data spaces can exist.

## Gotchas

- **If the Select Data Space drop-down is greyed out, the user lacks the Marketing Cloud Admin permission set.** Single most-cited failure mode across the whole series. [AB:setup-mcn]
- Basic Settings' Data Kits list (5 items: Sales, Marketing Setup Objects, Consent Objects, Flows Integration, Email Channel) is narrower than the full data-kit catalogue (7+ items including SMS/WhatsApp Channel kits, see `12_data_kits.md`). Not a contradiction — Basic Settings covers only what is inside that wizard.
- "Add Data Protection Details to Records" is named as a Basic Settings checklist item in every source but **no article walks through what clicking it actually configures.** This is a documentation gap in the KB, not confirmed to be the same thing as the "physical address" step under Set Up Email (see `18_consent.md`). Flag as open item for a live org S15.

## Automation route

- UI-only for instance enablement, Basic Settings checklist items, and data space selection. No API given anywhere in this KB for any of these.
- Permission set assignment (prerequisite) is CLI-doable, see `10_permissions_users.md`.

## Verification

- Any d360 read tool returning data (e.g. `d360_datastream_list`) confirms S3. Error "not enabled" = missing.
- Basic Settings page shows each of the 6 checklist items as completed/checked.
- [FIELD] A ruleset was generated via Basic Settings "Generate Ruleset" button in a live org, confirming this org's Basic Settings flow offers auto-generation (contrast with `15_identity_resolution.md` gotcha where one arthurbackouche.com implementation had no auto-generate option).
- [FIELD] Basic Settings has one "Update" button covering all data kits at once in a live org, not a per-kit install button as described by the articles (see `12_data_kits.md`).

## Sources

[AB:setup-datacloud-mcn] How to set-up Data Cloud for Marketing Cloud Next
[AB:setup-d360] How to set-up Data 360
[AB:setup-mcn] How to set-up Marketing Cloud Next
[AB:configure-mcn] How to configure Marketing Cloud Next
[AB:worth-migrating-mcn] Is it worth migrating to Marketing Cloud Next now
[FIELD] observed directly in a live implementation
