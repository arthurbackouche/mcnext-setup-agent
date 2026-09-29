# Marketing Data Kits

Covers check S8 (Marketing Data Kits deployed).

## Steps

1. Prerequisite: "Marketing Cloud Admin" permission set assigned, and the Basic Settings "Enable Data Cloud" checklist completed first (connector, email channel, data protection details, data space, Enable Marketing Cloud). [AB:data-kits-mcn]
2. Setup > Assistant Home > Basic Settings > install the Marketing Cloud Next Data Kits. The full catalogue named across articles: **Sales Data Kit, Marketing Setup Objects Data Kit, Consent Objects Data Kit, Flows Integration Data Kit, Email Channel Data Kit, SMS Channel Data Kit, WhatsApp Channel Data Kit.** [AB:data-kits-mcn]
3. A narrower 5-kit list (Sales, Marketing Setup Objects, Consent Objects, Flows Integration, Email Channel) appears inside the Basic Settings wizard specifically; SMS and WhatsApp Channel kits are shown as part of the broader data-kit catalogue in a sibling article, not inside Basic Settings itself. Not a contradiction, a scope difference. [AB:setup-mcn] [AB:data-kits-mcn]
4. An additional data kit exists for web tracking, not part of the 7 above: **External Tracking Data Kit** — enables Web Engagement DMOs, required before external-website tracking can populate Data 360. [AB:external-sites-mcn]
5. For other Salesforce products (Account Engagement/Pardot, Sales Cloud, CDP CRM Loyalty, Service Cloud, etc.): Data Cloud Setup > Salesforce CRM > expand the product row > install its **Standard Data Bundle**. This is a separate mechanism from the Marketing Cloud Next Data Kits list. [AB:data-kits-mcn]
6. Confirms the DMO name `ssot__EmailEngagement__dlm` used in this skill's S8 checks is real. Also confirms fields `ssot__IndividualId__c` and `ssot__EngagementChannelActionId__c` on that DMO. [AB:calc-insight-email-d360]
7. [FIELD] The consent kit DMO in a live org is `ssot__CommunicationSubscriptionConsent__dlm`.

## Limits

- Installing the Marketing Cloud Next Data Kits: **up to 30 minutes**. [AB:data-kits-mcn]
- A Standard Data Bundle install shows both the installed version number and the latest available version — kits are versioned and can be out of date. [AB:data-kits-mcn]

## Gotchas

- [FIELD] **in a live org, Basic Settings has one "Update" button that installs/refreshes all data kits at once — there is no per-kit install button as the articles' step-by-step language implies.** This is an org/release difference from the article screenshots; do not expect a per-kit toggle in this org.
- (inferred) If SMS/WhatsApp kits are installed without a licensed channel, they may sit unused. Not stated as an error, just an unused-feature risk. [AB:data-kits-mcn]
- Custom fields on Sales Cloud objects are not ingested by a bundle unless manually selected during stream setup (kit and connector are separate concerns — see `13_crm_connector_streams_mapping.md`). [AB:setup-datacloud-mcn]

## Automation route

- UI-only. No article gives an API or CLI command for installing a data kit or a Standard Data Bundle.

## Verification

- (inferred) Version number shown against each Standard Data Bundle in Data Cloud Setup > Salesforce CRM.
- SOQL/SQL probe of the DMOs a kit creates is a readable proxy, e.g. `ssot__EmailEngagement__dlm`, `ssot__ContactPointConsent__dlm`, `ssot__PrivacyConsentLog__dlm`, `ssot__MessagingEngagement__dlm`, `ssot__CommunicationSubscriptionConsent__dlm` (consent kit, confirmed [FIELD]). Table-not-found = kit missing.
- [FIELD] Basic Settings "Update" button state and the presence of consent DMO rows both confirm kit deployment in a live org.

## Sources

[AB:data-kits-mcn] How to use Data Kits in Marketing Cloud Next
[AB:setup-mcn] How to set-up Marketing Cloud Next
[AB:setup-datacloud-mcn] How to set-up Data Cloud for Marketing Cloud Next
[AB:calc-insight-email-d360] How to create a Calculated Insight for Email Engagement in Data 360
[AB:external-sites-mcn] How to integrate External Sites in Marketing Cloud Next
[FIELD] observed directly in a live implementation
