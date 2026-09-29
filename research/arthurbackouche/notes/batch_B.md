# Batch B — Email channel configuration, consent management, email templates

Source folder: `out/kb/arthurbackouche/raw/`. 8 articles.

### How to setup the Domain Authentication in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/email-channel-configuration/how-to-setup-the-domain-authentication-in-marketing-cloud-next/
- Purpose: authenticate a sending subdomain (e.g. `e.example.com`) so email sends carry the brand domain and reach the inbox rather than spam.
- Prerequisites and order dependencies: needs a domain registrar account (DNS access). This is the first step of the email channel setup chain: it unblocks "From Addresses" (next article explicitly says so) and Reply Mail Management (RMM), both of which live inside the same Authenticated Domain record.
- Steps:
  1. Salesforce Setup > "Set-up Email".
  2. On the Email page click "Go to Authenticated Domains".
  3. On the Authenticated Domains page click "+ Add a Domain".
  4. Enter a subdomain (convention: `e.` or `email.` prefix, e.g. `e.example.com`). Click "Submit".
  5. Create an email address for that domain (e.g. `marketing@e.example.com`), click "Create Now".
  6. Back in Salesforce, click "Manual DNS Record Information" under "Update the DNS Records".
  7. Copy the listed DNS records into the domain registrar's DNS tab (GoDaddy in the example).
  8. Back in Salesforce click "Apply Change" to validate.
- Limits and numbers: DNS validation can take up to 72 hours.
- Gotchas and failure modes: uses a subdomain deliberately so web-traffic reputation does not affect email domain reputation. Validation is asynchronous (up to 72h) — do not expect immediate success after "Apply Change".
- Automation route: UI-only. DNS record creation at the registrar is also UI/external, not scriptable from this project. No API mentioned.
- Verification: Authenticated Domains page shows the domain as validated after DNS propagates (UI indicator). No SOQL object given in the article.
- Maps to setup checks: S13 (default email channel/sending domain), S16 (Set Up Email umbrella).

### How to configure From Addresses in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/email-channel-configuration/how-to-configure-from-addresses-in-marketing-cloud-next/
- Purpose: add one or more sending addresses (display name + username) under an already authenticated domain, for open-rate and trust reasons.
- Prerequisites and order dependencies: explicitly "the next step of How to setup the Domain Authentication in Marketing Cloud Next". Requires the Authenticated Domain to exist first. The initial Email Sending Set-up already creates one From Address as part of domain authentication.
- Steps:
  1. On the Authenticated Domains list, click "show details" on the target domain.
  2. Inside the domain detail page, click "From Addresses".
  3. Click "+ Add From Addresses".
  4. Enter Display Name and Username (the app builds the full address from domain + username, e.g. `arthur@e.example.com`, `support@e.example.com`).
  5. Repeat to add more addresses; each shows in the From Addresses list once saved.
- Limits and numbers: none stated (example org ends with 3 addresses; no cap given).
- Gotchas and failure modes: avoid free webmail domains (Gmail/Hotmail) as From Address — flagged as spammy. Avoid no-reply addresses — hurts customer experience. Recommends per-purpose addresses (sales@, marketing@, support@, events@) for personalised sender identity.
- Automation route: UI-only.
- Verification: From Addresses list under the domain's detail page shows the configured addresses (UI indicator).
- Maps to setup checks: S13, S16.

### How to Configure Reply Mail Management In Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/email-channel-configuration/how-to-configure-reply-mail-management-in-marketing-cloud-next/
- Purpose: let recipients reply to marketing sends and route/auto-respond to those replies (RMM).
- Prerequisites and order dependencies: "After you configured your Authenticated Sender Domain" — depends on domain authentication being done first. Sits alongside From Addresses under the same domain detail page.
- Steps:
  1. On the Authenticated Domain, click "show details".
  2. Go to the "Reply Mail Management" tab.
  3. Reply Filters: set "Delete Auto replies and Out-of-Office message" to Yes (recommended) to avoid inbox flooding from bulk sends.
  4. Responses: enter an auto-response text that is sent immediately when someone replies (example text given in article).
  5. Routing: configure routing rules for incoming replies (article does not give detailed routing steps, calls it the "key feature").
  6. Click "Save".
- Limits and numbers: none stated.
- Gotchas and failure modes: without auto-reply deletion, high-volume sends to lists with many Out-of-Office responders can flood the reply inbox.
- Automation route: UI-only. Resource link given: https://help.salesforce.com/s/articleView?id=002192963&type=1 (Salesforce help, not an API).
- Verification: Reply Mail Management tab shows saved filter/response/routing config (UI indicator).
- Maps to setup checks: S13, S16.

### How to configure the Tracking Domain in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/email-channel-configuration/how-to-configure-the-tracking-domain-in-marketing-cloud-next/
- Purpose: custom-brand the click/tracking links in emails (deliverability, trust, control over link analytics) instead of a generic Salesforce tracking domain.
- Prerequisites and order dependencies: independent of consent, but logically follows domain authentication (same email-channel family). Requires a domain registrar and an external CA/SSL step (ZeroSSL) before Salesforce Links activation.
- Steps:
  1. Salesforce Setup > Certificate and Key Management > "Create CA-Signed Certificate". Fill Label, Unique Name, Common Name (subdomain, e.g. `www2.arthurbackouche.com`), Company, City, Country Code, Key Size (2048), Email Address, Department, State/Province.
  2. Click Save, then "Download Certificate Signing Request" (.csr file).
  3. Go to ZeroSSL (external, free service), create an account, submit the CSR-based request for a 90-day SSL certificate.
  4. Validate domain ownership with ZeroSSL by updating DNS records at the registrar.
  5. Download the resulting certificate/key file from ZeroSSL.
  6. Upload that file back into Salesforce Certificate and Key Management.
  7. Salesforce Setup > "Links" > "Create New". Select the custom tracking domain and click Activate.
- Limits and numbers: Key Size 2048. ZeroSSL certificate validity: 90 days (recurring renewal implied, not stated explicitly).
- Gotchas and failure modes: this is a manual multi-system workflow (Salesforce cert request -> external CA -> DNS -> back to Salesforce). 90-day cert expiry means a recurring renewal task (inferred (inferred): needs a renewal reminder since article does not mention auto-renewal).
- Automation route: UI-only inside Salesforce; ZeroSSL steps are external web UI, not API-driven per this article.
- Verification: Links page shows the custom tracking domain as Active (UI indicator).
- Maps to setup checks: S13, S16.

### How to ensure Compliance with Consent Settings in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/email-channel-configuration/how-to-ensure-compliance-with-consent-settings-in-marketing-cloud-next/
- Purpose: complete the "Set Up Email" compliance requirements — physical address, opt-in rules, Subscriptions, and initial consent import — needed before commercial sends are compliant and deliverable.
- Prerequisites and order dependencies: sits under Setup > Assistant Home > Set-up Email, alongside Authenticated Domains/From Addresses/RMM. States directly: **Marketing Cloud Next initially sets all individuals as "Opted out"**, so a consent import is required before promotional/commercial sends will reach anyone. This is the direct source for the "consent import required" special focus.
- Steps:
  1. Physical address: Setup > Assistant Home > Set-up Email > "Add or Update Physical Address" section > click "Go to Company Information".
  2. In Company Information, click Edit, enter the org address (this address appears in the footer of every email — CAN-SPAM/compliance requirement).
  3. Consent validation: in Set-up Email, review "Manage Consent Validation" — decide whether Promotional and Commercial emails require opt-in (article keeps recommended default settings; does not enumerate the toggle labels beyond "By Default options").
  4. Create Subscriptions: click "Go to Subscriptions" in the "Create Subscriptions" section. A default "Marketing" subscription exists already. Click "+ New Subscription", give it a Name (e.g. "Newsletter") and a Channel (e.g. "Email"), click Save.
  5. Consent import: click "Go to Consent Imports" in "Add or Update Consent Records". Select a Channel (e.g. Email) and a Subscription (e.g. Marketing), then upload a CSV file of individuals' email addresses. Uploaded individuals are opted-in to that channel/subscription automatically.
- Limits and numbers: none numeric stated beyond "2 types" of email (Commercial/Promotional vs Transactional).
- Gotchas and failure modes: Promotional/Commercial emails require consent (opt-in); Transactional emails do not. New Leads/Contacts default to Opted-out (confirmed again in the sibling consent-management article) — sends will silently fail to reach anyone until a consent import or an opt-in flow runs. Small marketing teams: article recommends sticking to a single Subscription to reduce complexity.
- Automation route: Address/Company Information — UI-only. Consent Validation toggles — UI-only. Subscriptions — UI-only (article gives no API). Consent Imports — CSV upload via the "Consent Imports" UI tool; article does not mention a REST/Bulk API path, so treat as UI-only for this batch. (inferred: MC Next likely also accepts consent creation via the MessagingConsent object per the sibling consent-management article, which does show a programmatic action — see below.)
- Verification: Company Information shows the address (UI). Subscriptions list shows Marketing + any new subscription (UI). Consent Imports history / resulting opted-in status on individual records (UI; article does not give a query object name for CommSubscriptionConsent-style verification in this article specifically).
- Maps to setup checks: S15 (Add Data Protection Details to Records — physical address maps here), S16 (Set Up Email: physical address, consent validation, subscriptions — this article is the primary source for S16), also feeds S13.

### How to manage consent in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/consent-management/how-to-manage-consent-in-marketing-cloud-next/
- Purpose: explains the MC Next consent data model (Channel, Communication Subscription, Consent Status, Consent Date, Communication Subscription Consent Id) and how to build an automated opt-in Flow using the MessagingConsent action, as an alternative/complement to CSV import.
- Prerequisites and order dependencies: assumes Subscriptions already exist (created in the compliance-settings article above) and that Communication Subscription / Communication Subscription Channel Type Id values are known (obtained from the Subscription records, not shown how to look up in this article). This is the direct, most detailed source on why sends fail without consent: "When a new Lead or Contact enter the Salesforce system it will be automatically set as opted-out and an action will need to be made in order to opt-in the record. This Option can be either manual or automated."
- Steps (automated opt-in via Record-Triggered Flow):
  1. Add the Consent Status widget to the Lead/Contact Page Layout for manual opt-in (UI-only manual path).
  2. For automated opt-in, build a Record-Triggered Flow:
     - Start Element: Object = Lead, Trigger = "When a record is created", Entry Conditions = exclude leads from form submissions (Marketing Cloud on Core forms already handle consent), Optimization = "Fast Field Updates".
     - Add a Scheduled Path with a 1-minute delay (required because record-triggered flows cannot run external callout actions in the immediate/fast path).
     - Optional Decision Element: route leads from double opt-in jurisdictions (example: Germany, Canada, California, Virginia) to a separate path, e.g. to send a transactional confirmation email.
     - Formula Resource: build `{!$Record.Email} & "#" & "<CommunicationSubscriptionChannelTypeId>"` — one formula per subscription/channel combination, to generate the Communication Subscription Consent Id.
     - Action Element: use the built-in `MessagingConsent.MessagingConsent` flow action. Inputs: CommunicationSubscriptionChannelType (recommended, e.g. `<CommSubscriptionChannelType Id, prefix 0eB>`), ConsentCapturedDateTime (`{!$Flow.CurrentDateTime}` or lead creation date), ConsentId (the formula resource output), ConsentStatus (`OPT_IN` or `OPT_OUT`), ContactPointValue (`{!$Record.Email}`), Name (recommended — the Communication Subscription Id, channel-agnostic, e.g. `<ContactPointTypeConsent-related Id, prefix 0Xl>`).
     - Create one Action Element per subscription/channel combination needed.
  3. Connect: Start > Scheduled Path (1-min delay) > Decision (optional) > Action Elements.
- Limits and numbers: 1-minute scheduled-path delay (mandatory, not just recommended, due to the callout restriction on immediate paths).
- Gotchas and failure modes: Communication Subscription Consent Id format is `<email>#<CommunicationSubscriptionChannelTypeId>` — get this wrong and the consent record will not match. Communication Subscription (channel-agnostic, e.g. `0XlHs...`) and Communication Subscription Channel Type Id (channel-specific, e.g. `0eBHs...`) are easy to confuse — both are 18-char-style Ids but reference different scopes. Record-triggered flows cannot do callouts in the immediate path — must use a scheduled path, which delays opt-in by at least 1 minute after record creation. Article recommends populating all fields (even "optional" ones) so Flow-created consent records match the shape of CSV-imported consent records.
- Automation route: this IS the automation route — Salesforce Flow using the standard `MessagingConsent.MessagingConsent` action element. This is UI-configured (Flow Builder) but the underlying action is a documented Salesforce automation action, not a hand-rolled API call. No direct Apex/REST/SOQL write path is given in the article for creating consent programmatically outside Flow; CSV import (previous article) is the other route. Reading consent could reasonably use SOQL on CommSubscriptionConsent-type objects (inferred, article does not name the underlying object/table for MC Next's consent storage).
- Verification: article gives no query or object name to directly verify consent state (no DMO/object name stated). Verification is inferred (inferred): check Consent Status widget on the Lead/Contact record, or Subscription-related consent list. No SOQL object confirmed by this article.
- Maps to setup checks: S16 (consent validation, subscriptions — core content), S6/S15 indirectly (Flow uses Lead/Contact fields), also directly informs the "consent seeding" special focus.

### How to manage Consent between Marketing Cloud Engagement and Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/consent-management/how-to-manage-consent-between-marketing-cloud-engagement-and-marketing-cloud-next/
- Purpose: migrate existing opted-in subscriber consent from MCE (Engagement) into MC Next (called "Marketing Cloud Growth" in this article's wording) so migrated audiences are not all defaulted to opted-out.
- Prerequisites and order dependencies: run after MC Next Subscriptions exist (needs a target Subscription/channel to import into, per the compliance-settings article). This is a one-time bulk migration step, separate from the ongoing Flow-based automated opt-in in the sibling article. Order: (1) build the DE and automation in MCE, (2) export via SFTP, (3) import into MC Next's Consent Imports tool.
- Steps:
  1. In MCE, create a Data Extension with fields: Email (subscriber email address), Consent Date (date consent was given).
  2. In MCE Automation Studio, create an automation with a SQL Query activity using:
     `SELECT EmailAddress AS Email FROM _Subscribers WHERE Status = 'active' AND DateJoined >= DATEADD(year, -1, GETDATE())`
     — filters to active subscribers who joined within the last 12 months.
  3. Export the resulting Data Extension to CSV via Marketing Cloud SFTP (use an FTP client such as FileZilla) to a local system.
  4. In MC Next, go to the Consent system > Consent Imports, upload the CSV, and process the import to opt in the listed individuals.
- Limits and numbers: SQL filter example uses a 1-year (12-month) `DateJoined` lookback — this is an example threshold, not a platform limit.
- Gotchas and failure modes: this is a manual, one-off point-in-time snapshot — consent captured in MCE after the export will not be reflected in MC Next unless re-run. The article does not address ongoing sync between the two platforms (no mention of a live bidirectional consent sync); treat MCE consent and MC Next consent as two separate stores connected only by this manual export/import bridge (inferred: no automated sync is described, so during a migration window consent status can diverge between MCE and MC Next unless this export/import is repeated).
- Automation route: MCE side (DE creation, Automation Studio SQL query activity, SFTP export) is MCE Automation Studio / SFTP — out of scope for this agent (MCE is out of scope per task rules) but noted as the documented mechanism. Import into MC Next is via the Consent Imports UI (CSV upload) — UI-only per this article, same tool as in the compliance-settings article.
- Verification: article gives no explicit verification step beyond "ensures all active subscribers ... are properly consented in Marketing Cloud Growth" — no object/query named. Inferred (inferred): check the Consent Imports history/log in MC Next Setup, or spot-check an imported individual's Consent Status.
- Maps to setup checks: S12 (MCE connector — related context, not the same mechanism: this consent bridge is a manual SFTP/CSV flow, not the Data 360 CRM/MCE connector), S16 (consent/subscriptions), directly the primary source for "how MCE and MC Next consent coexist during a migration."

### How to Personalise Emails with Merge Fields in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/email-templates/how-to-personalise-emails-with-merge-fields-in-marketing-cloud-next/
- Purpose: insert personalisation (merge fields) into email content using Data Graph attributes, and test the personalised email before sending live.
- Prerequisites and order dependencies: requires a Data Graph already built with the attributes to merge (firstName, lastName, etc. — "Primary Objects") — depends on Data Graph setup (S11) being complete before merge fields can be selected. Testing step depends on the test recipient being an opted-in contact — ties directly back to consent (S16) — a non-opted-in test recipient may not receive the test send.
- Steps:
  1. In the email editor, click the Merge Field icon.
  2. Select "Select Data Graph Attribute".
  3. Click "Primary Objects".
  4. Choose the attribute to insert (e.g., firstName, lastName).
  5. Preview the email with a selected contact's data (example: contact "Olivia").
  6. To send a test: preview with the contact's data, enter a test recipient email address, click "Send Test".
- Limits and numbers: test email "should arrive within a few minutes" (no exact SLA given).
- Gotchas and failure modes: explicit best practice — the test recipient email address must exist as an **opted-in contact** in Marketing Cloud Advanced, otherwise the test send can fail or not mimic real-world sending conditions. If a test email is not received, check: (1) recipient is opted-in, (2) sender profile/domain is properly authenticated (ties to domain authentication article), (3) email is not filtered to spam/junk.
- Automation route: UI-only (email editor merge field picker and Send Test button). No API given.
- Verification: Preview pane shows the merged attribute resolved with the sample contact's data (UI). Test email arriving in the test inbox confirms end-to-end personalisation + deliverability (external/manual check).
- Maps to setup checks: S11 (Data Graph must exist and be selected for personalization — hard dependency for merge fields to have attributes to choose), S16 (opted-in status required for test sends to succeed), S13 (sender authentication needed for delivery).

## Batch B cross-cutting findings

Canonical order for email channel and consent setup, based on explicit dependency statements across these 8 articles:

1. Authenticated Domain (domain authentication article: "next step of" chain starts here). Add subdomain, DNS records at registrar, wait up to 72h for validation.
2. From Addresses under that domain (explicitly "the next step of" domain authentication).
3. Reply Mail Management under that domain (explicitly "after you configured your Authenticated Sender Domain").
4. Tracking Domain (independent branch, can run in parallel with 2–3; needs its own DNS + external ZeroSSL cert flow).
5. Set Up Email compliance items, in this order per the compliance article's own section order: Physical Address (Company Information) -> Consent Validation settings -> Subscriptions (create/confirm) -> Consent Imports (CSV, opt in existing individuals). Note: MC Next defaults every Individual to Opted Out, so step "Consent Imports" here is mandatory before any commercial/promotional send will reach anyone.
6. In parallel with 5, for a migration from MCE: build DE + Automation Studio SQL export in MCE, SFTP the CSV, then feed it into the same Consent Imports UI tool used in step 5. This is a manual, one-off (or repeatable) bridge — no live sync between MCE and MC Next consent is described anywhere in this batch.
7. For ongoing/automated opt-in (new Leads/Contacts created after the initial import), build a Record-Triggered Flow using the `MessagingConsent.MessagingConsent` action (1-minute minimum scheduled-path delay, one action element per subscription/channel). This covers records not captured by the one-time CSV import.
8. Data Graph (S11, covered in a different batch) must exist before merge-field personalisation (email templates article) can select attributes. Test sends of personalised emails require the test recipient to already be an opted-in individual — so step 5/6/7 must be functionally complete (at least for the test recipient) before template testing will reliably work.

Consent seeding for sends — direct textual support:
- "Marketing Cloud Next initially set-up all the individuals as 'Opted out'" (compliance-settings article).
- "When a new Lead or Contact enter the Salesforce system it will be automatically set as opted-out and an action will need to be made in order to opt-in the record. This Option can be either manual or automated." (consent-management article).
- Two seeding routes are documented: (a) CSV Consent Import (UI, one-time bulk, by Channel + Subscription), (b) MessagingConsent Flow action (automated, per-record, ongoing).
- MCE-to-MC-Next bridge is a third, migration-specific route: MCE DE + Automation Studio SQL export -> SFTP -> CSV -> MC Next Consent Imports (same UI tool as route (a), just sourced from MCE data instead of a hand-built CSV).
- No article describes consent flowing automatically from MCE to MC Next, or vice versa, in real time. Treat the two systems as separate consent stores during migration; anyone opted in only in MCE stays opted-out in MC Next until one of the above import routes runs.

Contradictions / naming inconsistencies between articles:
- "Marketing Cloud Growth" vs "Marketing Cloud Next" vs "Marketing Cloud Advanced": the consent-bridge article calls the target "Marketing Cloud Growth", the email-templates article says the test recipient must be opted-in "in Marketing Cloud Advanced", while every other article in this batch says "Marketing Cloud Next". These read as the same product referenced with different edition/marketing names by the source site; no functional difference is described. Flag as terminology inconsistency, not a functional contradiction (inferred: same underlying platform, edition name varies by article).
- The compliance-settings article treats "Consent Imports" as the way to opt in individuals via CSV; the consent-management article treats "Add or Update Consent Records" only implicitly (via CSV in the other article) and instead gives the programmatic Flow route — no contradiction, but the two are complementary paths that the articles present separately without cross-linking each other.
- No article in this batch states the field caps, timings (beyond the 72h DNS validation and 1-minute scheduled path and 90-day SSL cert), row counts, or refresh schedules requested for consent import batch sizes — these are not covered by this batch and should be marked `unknown` rather than assumed.
