## Batch A: Foundation setup, User access management, Brand customization

Source series: arthurbackouche.com, Marketing Cloud Next docs. 9 articles.

---

### How to set-up Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/foundation-setup/how-to-set-up-marketing-cloud-next/
- Purpose: Top-level walkthrough of the Basic Settings, Required Set-up and Additional Features screens used to turn on MC Next.
- Prerequisites and order dependencies: Data Cloud must already be enabled before Basic Settings appears in Assistant Home. Basic Settings (3 steps: Enable Data Cloud, Install Marketing Data Kits, Configure Identity Resolution Rulesets) must complete before Required Set-up (Email, Marketing Performance). Marketing Performance requires Marketing Data Kits already installed. Additional Features (Agentforce/Einstein, Customer Engagement, Sites and Forms, User Access, Brand, Page Customization) come after Required Set-up.
- Steps:
  1. Setup > Assistant Home > Basic Settings.
  2. Under "Enable Data Cloud": Create a Salesforce CRM Connector, Add a Default Email Channel, Add Data Protection Details to Records, Select a Data Space, Enable Marketing Cloud. Each is a click-to-Enable action.
  3. Under "Install the Marketing Kits": deploy Sales Data Kit, Marketing Setup Objects Data Kit, Consent Objects Data Kit, Flows Integration Data Kit, Email Channel Data Kit.
  4. Under "Configure Identity Resolution Rulesets": generate/run the ruleset that produces the Unified Individual object.
  5. Required Set-up > Email: Configure Email Delivery (sending domain), Add or Update Physical Address, Manage Consent Validation, Add Contacts, Create Subscriptions, Add or Update Consent Records.
  6. Required Set-up > Marketing Performance: install Marketing Data Kits (already done), optionally Set Up Salesforce Personalization and Configure Web Tracking. Associate "Tableau Next Included App Business User" permission set to view Marketing Performance dashboard.
  7. Additional Features: Agentforce and Einstein toggles (Get Started with Einstein Generative AI, Activate Agentforce, Activate Einstein Segment Creation); Customer Engagement (Scoring Rules, Salesforce Personalization, Data Graph); Sites and Forms (Web Tracking integrations, Third-Party Domain to CORS allow-list, Allow Scripts on External Sites); User Access (invite users, assign Marketing Cloud Admin/Manager, grant CMS access); Brand (custom domain for landing pages); Page Customization (add LWC widgets to Contact/Lead/Prospect/Campaign layouts: Privacy Consent Status, Data 360 Profile Engagement, Data 360 Profile Insights).
- Limits and numbers: none given (no timings in this article).
- Gotchas and failure modes: "If the Select Data Space drop down bar is greyed out make sure you have the relevant Marketing Cloud Growth Permission set 'Marketing Cloud Admin'." This is the single most-cited failure mode across the series.
- Automation route: UI-only. No API mentioned for any of these steps.
- Verification: Visual confirmation of "Marketing Performance feature enabled" after install; no object/query given. (inferred) Presence of the LWC widgets on page layouts is a UI-visible indicator that Page Customization is done.
- Maps to setup checks: S5, S6, S7, S8, S9, S10, S13, S15, S16, S17, S18, S19, S20.

---

### How to configure Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/foundation-setup/how-to-configure-marketing-cloud-next/
- Purpose: End-to-end configuration log (Basic Settings, Email Settings, Analytics Settings, Additional Features) from an actual implementation, with more granular ordering than the general "how to set-up" article.
- Prerequisites and order dependencies: Explicit order given: (1) Activate Data Cloud instance, (2) select the Data Space ("Default") in Assistant Home > Basic Settings, (3) install Marketing Data Kits, (4) generate the Identity Resolution ruleset. Email Settings section follows Basic Settings. Analytics Settings (package installs) is separate and not gated on Email. Additional Features are last and optional.
- Steps:
  1. Data Cloud Setup > activate "Set Up Your Data Cloud Instance".
  2. Setup > Assistant Home > Go to Basic Setting > select Data Space "Default".
  3. Same Basic Setting page > Install the Marketing Data Kits (Data Model Objects and field/attribute mappings install automatically).
  4. Same Basic Setting page > Identity Resolution Rulesets > click "Generate Ruleset" for the default (email address matching only) ruleset.
  5. Assistant Home > Set up Email > Go to Authenticated Domains > Add Domain. Recommend a dedicated subdomain (e.g. email.example.com), not the root domain. Add the DNS records shown to the domain registrar (e.g. GoDaddy), then validate.
  6. Add or Update Physical Address (appears at bottom of email templates).
  7. Manage Consent Validation: default setup is fine if only commercial-communication consent matters (transactional consent not required).
  8. Add Contacts, Create Subscriptions, Add or Update Consent Records: this implementation skipped these because Contacts/Leads are ingested from Salesforce CRM via Data Cloud Data Streams instead.
  9. Toggle on: Einstein Metrics Guard, Einstein Send Time Optimisation, Einstein Engagement Frequency, Einstein Engagement Scoring.
  10. Analytics Settings: Install Marketing Engagement Analytics Package, Landing Pages and Forms Analytics Package, Flow Reports Analytics Package; then Share Access to Analytics Folders.
  11. Additional Features (optional): Einstein explanations (see limits below), Customer Engagement scoring set-up, User Access (assign Marketing Cloud Admin/Manager), Brand (custom URL/domain for landing pages), Page Customization (add LWC widgets to Contact/Lead layouts).
- Limits and numbers: Einstein Send Time Optimization requires opting in to the "Global Data Model for Einstein" in Growth Edition; in Advanced Edition you can enable or disable global models. Einstein Engagement Scoring and Einstein Engagement Frequency are stated as "available only in Marketing Cloud Next Advanced Edition" (the client is on Advanced per manifest, so both are available).
- Gotchas and failure modes: Using the root domain instead of a dedicated subdomain for email sending is discouraged ("recommended... to not mess with the current set-up of your root domain"). Skipping Add Contacts/Create Subscriptions/Consent Records only works if CRM data streams are the actual ingestion path — otherwise those steps are required.
- Automation route: UI-only throughout. DNS record creation happens outside Salesforce (at the domain registrar) — not automatable via any Salesforce tool.
- Verification: (inferred) Authenticated Domains list shows a validated status once DNS records are confirmed. No object/query for the other steps.
- Maps to setup checks: S3, S5, S7, S8, S9, S10, S13, S16, S17, S18, S19.

---

### How to set-up Data Cloud for Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/foundation-setup/how-to-set-up-data-cloud-for-marketing-cloud-next/
- Purpose: Detailed steps for enabling the Data 360 instance and standing up the first Salesforce CRM connector, framed as the true first step of any MC Next build ("If Data Cloud is your iPhone, Marketing Cloud Next would be an App installed on it").
- Prerequisites and order dependencies: This is the very first step in the whole MC Next journey — must happen before Basic Settings / Data Kits / Identity Resolution. Within this article: enable Data 360 instance first, then assign permission sets, then create the CRM connector/data stream.
- Steps:
  1. Setup > Data Cloud Setup > click "Get Started" at the bottom of the page. Automatic sub-steps: creating the Data Cloud instance, setting up metadata, initialising the Customer 360 Data Model, readiness check.
  2. Assign the "Data Cloud Architect" permission set (formerly "Data Cloud Admin" — name depends on org age/release) to the implementer. Grants full Data 360 access: Data Cloud Setup, data model mapping, data streams, identity resolution rulesets, insights.
  3. Data Cloud App > Data Streams tab > New > select "Salesforce CRM" connector > Next.
  4. Bundles tab > select "Sales Bundle" (Account, User, OpportunityContactRole, Opportunity, Contact, Lead) > Next.
  5. Review/select Attribute Fields per object (standard fields default-selected; custom fields and formula fields must be added manually) > Deploy.
  6. Confirm the deployed streams in the Data Streams list.
- Limits and numbers: Sales Bundle covers exactly 6 objects: Account, User, OpportunityContactRole, Opportunity, Contact, Lead. Resulting streams named with "_Home" suffix: User_Home, Lead_Home, OpportunityContactRole_Home, Opportunity_Home, Contact_Home, Account_Home, plus CurrencyType_Home (added automatically for multicurrency orgs).
- Gotchas and failure modes: Permission set name varies by org vintage ("Data Cloud Admin" vs "Data Cloud Architect") — check both when searching PermissionSet records. Custom fields on Sales Cloud objects are NOT ingested unless manually selected during stream setup.
- Automation route: UI-only for instance enablement and connector/bundle selection. Permission set assignment itself is CLI-doable (`sf org assign permset`) once the exact API name is known from a PermissionSet query.
- Verification: Data Streams list view, column "Data Connector" = "Salesforce CRM"; presence of the seven "_Home" streams. Readable via `d360_datastream_list`.
- Maps to setup checks: S2, S3, S4, S5, S6.

---

### How to use Data Kits in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/foundation-setup/how-to-use-data-kits-in-marketing-cloud-next/
- Purpose: Explains what a Data Kit is (objects/fields/connections bundled together, analogy: a box of Lego bricks) and how to install both the core MC Next kits and additional product-specific Standard Data Bundles.
- Prerequisites and order dependencies: Enable Data 360 first, then install the MC Next Data Kit. Requires the "Marketing Cloud Admin" permission set on the user before starting. Order: Setup > Assistant Home > Go to Basic Settings > complete the first Basic Settings block (Enable Data Cloud, Create Salesforce CRM Connector, Add Default Email Channel, Add Data Protection Details to Records, Select a Data Space, Enable Marketing Cloud) before installing the kits.
- Steps:
  1. Confirm "Marketing Cloud Admin" permission set is assigned.
  2. Setup > Assistant Home > Go to Basic Settings > complete the "Enable Data Cloud" checklist (6 items, same as other articles).
  3. Install the Marketing Cloud Next Data Kits: Sales Data Kit, Marketing Setup Objects Data Kit, Consent Objects Data Kit, Flows Integration Data Kit, Email Channel Data Kit, SMS Channel Data Kit, WhatsApp Channel Data Kit.
  4. For other Salesforce products (Account Engagement, Sales Cloud, CDP CRM Loyalty, Service Cloud, etc.): Data Cloud Setup > Salesforce CRM > expand the product row (e.g. click arrow next to "Service Cloud") > install its Standard Data Bundle.
- Limits and numbers: Installing the Marketing Cloud Next Data Kits can take "Up to 30 min". A Standard Data Bundle install shows both the installed version number and the latest available version (i.e. kits are versioned and can be out of date).
- Gotchas and failure modes: None explicit beyond the permission-set prerequisite; (inferred) if SMS/WhatsApp kits are installed without a licensed channel, they may sit unused.
- Automation route: UI-only. Article gives no API for installing kits.
- Verification: (inferred) Version number shown against each Standard Data Bundle in Data Cloud Setup > Salesforce CRM; presence of the DMOs the kit creates is a readable proxy via SOQL/SQL on Data 360 (per skill's S8 probe list).
- Maps to setup checks: S5, S7, S8.

---

### How to Configure Identity Resolution Rulesets in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/foundation-setup/how-to-configure-identity-resolution-rulesets-in-marketing-cloud-next/
- Purpose: Explains identity resolution conceptually (merging duplicate individual records across ingested systems into one Unified Individual) and walks through manually building a ruleset step by step.
- Prerequisites and order dependencies: Comes after Data 360 is enabled and CRM/other data streams exist (there must be Individual records to resolve). This is the third and last Basic Settings step in Assistant Home. Unblocks: creation of the Unified Individual DMO that Marketing Cloud Next Decisions/personalization and Data Graphs rely on.
- Steps:
  1. Setup > Assistant Home > Go to Basic Settings > bottom of page, "Set Up Identity Resolution" — if no ruleset can be auto-generated, click "Manually Create One".
  2. Identity Resolution page > New > "Create a New Ruleset". Select Data Space "Default", Data Model Object "Individual", add a reference number.
  3. Give the ruleset a Name and Description, click Save.
  4. On the ruleset detail page, configure Match Rules:
     a. Rule 1 "Normalised Email": DMO "Contact Point Email", field "Email Address", Match Method "Exact Normalised" (case-insensitive exact match).
     b. Rule 2 "Lead to Contact": DMO "Identity Match", field "Identity Match Type", Match Method "Exact" > Advanced Settings > set Identity Match Type value to "lead-to-contact" > Back to Basic Setting.
  5. Save the Matching Rules, click Save.
  6. Click "Run the Ruleset".
  7. Review the result: a Consolidation Rate is reported (percentage of individuals unified).
  8. Back in Basic Settings, the Unified Individual DMO to be used by MC Next is now listed by name.
- Limits and numbers: Example run in the article produced a Consolidation Rate of 4%.
- Gotchas and failure modes: The Unified Individual DMO name is NOT a fixed/predictable string — in this implementation it came out as `UnifiedssotIndividual888__dlm`, not a standard `ssot__UnifiedIndividual__dlm`. Any automated check assuming a fixed DMO name should treat the name as org-specific and read it from Basic Settings or the ruleset's own output rather than hardcoding it. Auto-generation of the ruleset is not always available ("we don't have the possibility to automatically generate one" in this org) — manual creation may be required even on a fresh org.
- Automation route: UI-only for ruleset creation and running. (inferred) Once created, the resulting DMO is queryable via Data 360 SQL/REST, but the article gives no direct API for creating or running rulesets.
- Verification: The Basic Settings page lists the exact Unified Individual DMO name after a successful run — read that name, then query row counts on it. The ruleset detail page shows the Consolidation Rate as the run's success indicator.
- Maps to setup checks: S10, S11 (unblocks Data Graph and Decisions personalization), S9.

---

### How to Import Customers into Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/foundation-setup/how-to-import-customers-into-marketing-cloud-next/
- Purpose: Explains that customer import into MC Next happens entirely at the Data Cloud layer (Individuals / Unified Individuals), not in MC Next itself, and covers mapping custom fields that aren't captured by the default bundle.
- Prerequisites and order dependencies: Comes after "Data Cloud and Marketing Cloud Next pre-requisites" (i.e. after Data 360 enablement and Basic Settings). Feeds directly into segment creation in MC Next (fields must be mapped to Data Cloud before they can be used to build segments).
- Steps:
  1. Data Cloud > Data Streams tab > New > create a Salesforce CRM Data Stream.
  2. Select a Bundle (pre-grouped objects/fields for a source system, e.g. Sales Cloud).
  3. Review and select fields per object in the bundle; standard fields are selected by default, custom fields must be reviewed and selected manually.
  4. Deploy the Data Stream; confirm in the Data Streams list view (Data Connector column = "Salesforce CRM").
  5. For custom fields missed initially: go to the Data Stream, click "Add Source Fields" to pull in more fields from the source object (e.g. Contact).
  6. Click "Review" to manually map the newly added, previously-unmapped fields to Data Model Object fields — either connect to an existing DMO field or create a new custom field directly on the DMO.
- Limits and numbers: Example given: only 39 of 71 fields on the Contact object were mapped to Data Cloud DMOs by default — meaning roughly half of custom/non-standard fields require manual mapping.
- Gotchas and failure modes: Any field needed for segmentation in MC Next must be explicitly mapped — it is not enough for the field to exist on the Salesforce object; it must be mapped to a DMO field or a new DMO field created for it.
- Automation route: UI-only. No REST/metadata alternative given for adding source fields or mapping them to DMOs.
- Verification: (inferred) Data Stream field-mapping screen shows mapped vs. unmapped count (e.g. "39/71 mapped"); segments can only reference fields that show as mapped.
- Maps to setup checks: S4, S8, S21 (custom DMO mappings depend on this exact manual field-mapping process for custom objects (e.g. subscription or credit records)).

---

### Migrate Engagement Data from Account Engagement to Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/foundation-setup/migrate-engagement-data-from-account-engagement-to-marketing-cloud-next/
- Purpose: Steps to bring historical engagement data from Account Engagement (Pardot) into Data Cloud/MC Next so engagement insights aren't lost when MC Next is enabled. Not about MCE (Engagement)/ExactTarget — this is the separate Pardot ("Account Engagement") product.
- Prerequisites and order dependencies: Requires Data Cloud already set up. Independent of the MCE connector (Step F in the skill); this article is specific to orgs coming from Account Engagement/Pardot, not from Marketing Cloud Engagement.
- Steps:
  1. Data Cloud Setup > Salesforce CRM tab > install the "Marketing – Account Engagement CRM Data" Bundle (Admin only).
  2. Data Cloud > Data Streams > New > Salesforce CRM connector > select Bundle "Marketing – Account Engagement CRM" > deploy; confirm the resulting streams.
  3. Salesforce Setup > "Data Cloud Integration" > select the Account Engagement Business Unit.
  4. Create an Account Engagement Data Stream. Choose a Type: this implementation used "Email Engagement Data"; other available types are Form Engagement Data, Web Page Engagement Data, Custom URL Engagement Data. Deploy directly.
  5. In Account Engagement itself: Account Engagement Settings > Connectors > edit the Data Cloud Connector > set look-back date up to 2 years (to collect 2 years of historical email engagement) > activate the connector.
- Limits and numbers: Look-back window for Email Engagement Data can be set up to 2 years.
- Gotchas and failure modes: None stated beyond "Admin only" for the bundle install. (inferred) This is a separate connector/bundle from the MCE (Engagement)/ExactTarget connector referenced in Step F of the skill — do not conflate Account Engagement (Pardot) streams with Marketing Cloud Engagement streams. the client' migration is from MCE, not Account Engagement, so this article's specific bundle is likely not applicable, but the general "install bundle > create stream > configure look-back > activate connector" pattern is instructive for the MCE connector (S12) even though the article never mentions MCE by name.
- Automation route: UI-only. Bundle install, stream creation, and connector activation are all Setup/Data Cloud UI actions; no API given.
- Verification: (inferred) Data Streams list shows the Account Engagement-sourced streams; Account Engagement Connectors page shows connector status = active.
- Maps to setup checks: S4 (pattern analogy, not S12 directly since this is Pardot not MCE), S8.

---

### How to configure the Permission Sets in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/user-access-management/how-to-configure-the-permission-sets-in-marketing-cloud-next/
- Purpose: Describes the two out-of-the-box MC Next permission sets (Marketing Cloud Admin, Marketing Cloud Manager) and how to assign them, plus the option to build a custom, more restricted permission set.
- Prerequisites and order dependencies: Assumes MC Next is already enabled (permission sets exist once the product is provisioned). Assigning Marketing Cloud Admin to the implementer is a precondition for later Basic Settings steps (e.g. Data Space selection, Data Kits) elsewhere in this series.
- Steps:
  1. Setup > Permission Sets tab > search "Marketing Cloud Admin" or "Marketing Cloud Manager".
  2. Click the desired permission set > "Manage Assignment".
  3. Select the user to assign (example: "Alf Operator").
  4. Choose "No expiration date" for a permanent assignment, or "Specify the expiration date" for a time-boxed one.
  5. Click "Assign".
  6. (Optional, for tighter control) Build a fully custom permission set instead, scoped across these categories: CMS Content Roles, General Marketing Permissions, Consent Permissions in Marketing Cloud Next, Content and Publishing Permissions, Flow Permissions in Marketing Cloud Next. Recommended use case: restrict "Flow Permissions in Marketing Cloud Next" for marketers so they can't touch Salesforce Flows that CRM admins are worried about breaking.
- Limits and numbers: None numeric; two standard permission sets only (Admin, Manager) unless a custom one is built.
- Gotchas and failure modes: Marketing Cloud Admin grants access to Salesforce Setup and Admin Flows (flows with CRM elements) — CRM admins are commonly wary of this; recommend Marketing Cloud Manager for marketers who should not touch Setup/Flows. Marketing Cloud Manager still gets Agentforce and Prompt Template access.
- Automation route: CLI — assignment itself is straightforward via `sf org assign permset -n <PermissionSet.Name>` per the setup skill's Step A; the article's steps are UI equivalents of the same action. Building a custom permission set (choosing specific permission categories) is UI-only as described (no metadata API route given in the article).
- Verification: PermissionSetAssignment query for the target user (`SELECT PermissionSet.Label FROM PermissionSetAssignment WHERE AssigneeId = '<user id>'`); UI "Manage Assignment" list shows assigned users.
- Maps to setup checks: S5, S6.

---

### How to configure a Brand in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/brand-customization/how-to-configure-a-brand-in-marketing-cloud-next/
- Purpose: How to create a reusable Brand asset (colors, typography, buttons, spacing, borders) in the Marketing CMS so email templates and landing pages stay on-brand without manual re-styling.
- Prerequisites and order dependencies: Requires a CMS Workspace already set up for Marketing Cloud (article uses an existing "Content Workspace for Marketing Cloud"). Not gated by Data Cloud/Basic Settings — a content-layer feature, independent of S1–S14 data foundation checks. Once published, the Brand can be applied to any email or landing page.
- Steps:
  1. Marketing App > Content tab > select the CMS Workspace used for Marketing Cloud Next.
  2. Click "Add" > "Brand" > Save.
  3. Configure: Brand Details, Colors, Typography, Buttons, Margin and Padding, Borders — using the left panel; preview live in the right panel against a sample email/landing page.
  4. Click "Publish".
  5. To apply: open a new email in MC Next, click "Select Brand" on the right panel, choose the Brand from the CMS folder pop-up, click "Add". The email updates automatically with the brand's styles.
- Limits and numbers: None given.
- Gotchas and failure modes: None stated in the article.
- Automation route: UI-only. No API given for brand creation or application.
- Verification: (inferred) Brand item appears as a published asset in the CMS Workspace; applying it to a test email visibly changes colors/typography/buttons.
- Maps to setup checks: None of S1–S21 directly (brand/content feature, not a data-foundation or entitlement check). (inferred) Loosely related to S18/S19 only in that both live under Marketing Cloud content/analytics configuration, but Brand itself is out of scope for the setup verdict.

---

## Batch A cross-cutting findings

**Canonical setup order** (synthesized across all Batch A articles, most explicit in "How to set-up Data Cloud for Marketing Cloud Next" and "How to configure Marketing Cloud Next"):

1. Enable the Data 360 (Data Cloud) instance — Setup > Data Cloud Setup > Get Started. Automatic: instance, metadata, Customer 360 model.
2. Assign Data Cloud Architect/Admin permission set to the implementer (name varies by org vintage — check both labels).
3. Assign Marketing Cloud Admin permission set to the implementer (required before the Data Space picker in Basic Settings is usable; greyed-out picker is the standard symptom of a missing permission set).
4. Create the Salesforce CRM connector / data stream (Sales Bundle: Account, User, OpportunityContactRole, Opportunity, Contact, Lead), review and select fields (standard fields default; custom fields manual), deploy.
5. In Assistant Home > Basic Settings, complete the "Enable Data Cloud" checklist in full: Create Salesforce CRM Connector (done in step 4), Add a Default Email Channel, Add Data Protection Details to Records, Select a Data Space ("Default"), Enable Marketing Cloud.
6. Install the Marketing Data Kits (Sales, Marketing Setup Objects, Consent Objects, Flows Integration, Email Channel, plus SMS/WhatsApp Channel Data Kits if those channels are licensed). Up to 30 minutes.
7. Configure and run Identity Resolution Ruleset (manual creation may be required even on fresh orgs; auto-generate is not always offered). Produces the Unified Individual DMO, whose exact name is org-specific (seen as `UnifiedssotIndividual888__dlm` in one implementation, not a fixed string).
8. Import/map any additional custom fields needed for segmentation (Data Stream > Add Source Fields > Review > map to DMO or create new DMO field).
9. Required Set-up > Email: sending domain (dedicated subdomain, DNS records at registrar), physical address, consent validation, contacts/subscriptions/consent records (can be skipped if CRM data streams are the actual contact-ingestion path).
10. Required Set-up > Marketing Performance and Analytics Settings: install analytics packages (Marketing Engagement, Landing Pages and Forms, Flow Reports), share analytics folders, associate Tableau Next Included App Business User permission set.
11. Toggle Einstein features (Metrics Guard, Send Time Optimization, Engagement Frequency, Engagement Scoring) — Engagement Scoring and Engagement Frequency are Advanced-Edition-only (the client qualifies).
12. Additional Features, order-independent: Agentforce/Einstein generative AI toggles, Customer Engagement (Scoring Rules, Personalization, Data Graph), Sites and Forms (web tracking, CORS domain, iframe permissions), User Access (permission set assignment to marketers), Brand (content-layer, no data dependency), Page Customization (LWC widgets on Contact/Lead/Prospect/Campaign layouts).
13. Migrate historical engagement data (Account Engagement / Pardot pattern shown; MCE-specific connector not covered in this batch) as a parallel, non-blocking track.

**Contradictions and inconsistencies between articles:**
- Permission set naming is inconsistent across articles and even within the same series: "Data Cloud Admin" vs. "Data Cloud Architect" (explicitly flagged as depending on org age/release in "How to set-up Data Cloud for Marketing Cloud Next"), and the Basic Settings gate is attributed only to "Marketing Cloud Admin" (Marketing Cloud Growth Permission set) in two articles — no article clarifies whether both the Data Cloud and Marketing Cloud permission sets are needed simultaneously, or just one. Treat S5/S6 checks as needing to search for both permission set family names.
- The Unified Individual DMO name is presented as a fixed-sounding concept ("Unified Individual Object") in most articles, but the one article that actually walks through ruleset creation shows a generated, non-standard name (`UnifiedssotIndividual888__dlm`). This directly contradicts the setup skill's S10 assumption of `ssot__UnifiedIndividual__dlm` — the check should read the actual name from Basic Settings or the ruleset output rather than hardcoding a DMO name.
- "How to set-up Marketing Cloud Next" lists the Basic Settings Data Kits as 5 kits (Sales, Marketing Setup Objects, Consent Objects, Flows Integration, Email Channel); "How to use Data Kits in Marketing Cloud Next" lists 7 (adds SMS Channel and WhatsApp Channel). This is not a contradiction so much as scope difference — the first article covers only what's inside Basic Settings itself, the second covers the full data-kit catalogue including channel-specific kits added afterward. Confirms S8 should check for SMS Channel kit DMOs too, per the estate's stated SMS usage in the setup skill.
- Ruleset auto-generation: "How to configure Marketing Cloud Next" implies Basic Settings simply has a "Generate Ruleset" button producing a default email-match ruleset; "How to Configure Identity Resolution Rulesets" states auto-generation was not available in that org and the ruleset had to be built manually end-to-end (including a second, more complex Lead-to-Contact match rule). Do not assume the one-click path will be available — plan for the manual multi-step ruleset build as the default expectation, with one-click as a bonus if offered.
- No article in this batch mentions the MCE (Engagement)/ExactTarget connector by name (S12). The closest analogy is the Account Engagement (Pardot) migration article, which is a different Salesforce product and a different Data Cloud bundle. This confirms the setup skill's own note that the MCE integration article "was not retrievable" — Batch A gives no direct evidence for S12, S13 (partially, only the authenticated-domain half is covered), S14, S17 (partially covered — toggles are named but no cadence/limits given), S19, S20 (only that widgets exist, not how to share/verify), S21 (only the generic custom-field-mapping mechanism, not custom objects (e.g. subscription or credit records) specifics).
