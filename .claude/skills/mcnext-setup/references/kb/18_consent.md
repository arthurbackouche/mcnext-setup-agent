# Consent, physical address, subscriptions

Covers checks S15 (Add Data Protection Details to Records) and S16 (Set Up Email compliance: physical address, consent validation, subscriptions, consent import).

## Steps

### Physical address (S15/S16 overlap — see gotcha)

1. Setup > Assistant Home > Set-up Email > "Add or Update Physical Address" > "Go to Company Information" > Edit > enter the org address. This appears in the footer of every email (CAN-SPAM/compliance requirement). [AB:consent-compliance-mcn]

### Consent validation and subscriptions

2. Review "Manage Consent Validation" in Set-up Email — decide whether Promotional and Commercial emails require opt-in. Default settings are usually fine if only commercial-communication consent matters (transactional consent not required). [AB:consent-compliance-mcn] [AB:configure-mcn]
3. There are 2 categories of email: **Commercial/Promotional** (requires opt-in consent) and **Transactional** (does not). [AB:consent-compliance-mcn]
4. Create Subscriptions: "Go to Subscriptions" > a default "Marketing" subscription already exists > "+ New Subscription" > Name (e.g. "Newsletter") + Channel (e.g. Email) > Save. Small marketing teams: stick to a single Subscription to reduce complexity. [AB:consent-compliance-mcn]

### Consent import (mandatory before any commercial send reaches anyone)

5. **Marketing Cloud Next initially sets every Individual to "Opted out".** [AB:consent-compliance-mcn] [AB:consent-manage-mcn]
6. "Go to Consent Imports" > select Channel (e.g. Email) and Subscription (e.g. Marketing) > upload a CSV of individuals' email addresses. Uploaded individuals are opted-in to that channel/subscription automatically. [AB:consent-compliance-mcn]
7. **Two seeding routes exist**: (a) CSV Consent Import (UI, one-time bulk, by Channel + Subscription); (b) `MessagingConsent` Flow action (automated, per-record, ongoing — see below). No article shows a direct Apex/REST/SOQL write path for consent outside these two.

### Automated opt-in via Flow (ongoing, for records created after the initial import)

8. Add the Consent Status widget to the Lead/Contact Page Layout for a manual opt-in path (UI-only). [AB:consent-manage-mcn]
9. **Record-Triggered Flow**: Object = Lead, Trigger = "When a record is created", entry conditions exclude leads from form submissions (Marketing Cloud on Core forms already handle consent), Optimization = "Fast Field Updates". Add a **Scheduled Path with a 1-minute delay** — mandatory, because record-triggered flows cannot run external callout actions in the immediate/fast path. Optional Decision Element routes double-opt-in jurisdictions (Germany, Canada, California, Virginia) to a separate confirmation path. [AB:consent-manage-mcn]
10. Formula Resource: `{!$Record.Email} & "#" & "<CommunicationSubscriptionChannelTypeId>"` — one formula per subscription/channel combination — produces the Communication Subscription Consent Id. [AB:consent-manage-mcn]
11. Action Element: built-in `MessagingConsent.MessagingConsent` flow action. Inputs: CommunicationSubscriptionChannelType (e.g. `<CommSubscriptionChannelType Id, prefix 0eB>`), ConsentCapturedDateTime (`{!$Flow.CurrentDateTime}` or lead creation date), ConsentId (the formula output), ConsentStatus (`OPT_IN` or `OPT_OUT`), ContactPointValue (`{!$Record.Email}`), Name (recommended — the Communication Subscription Id, e.g. `<ContactPointTypeConsent-related Id, prefix 0Xl>`). One Action Element per subscription/channel combination needed. Populate all fields, even "optional" ones, so Flow-created consent records match CSV-imported ones. [AB:consent-manage-mcn]
12. Connect: Start > Scheduled Path (1-min delay) > Decision (optional) > Action Elements. [AB:consent-manage-mcn]

### MCE-to-MC-Next consent bridge (migration-specific — full detail in `14_mce_connector.md`)

13. One-time or repeatable manual bridge: MCE DE + Automation Studio SQL export > SFTP CSV > same Consent Imports UI tool used in step 6. No live sync. [AB:consent-mce-bridge-mcn]

## Limits

- 1-minute scheduled-path delay is mandatory, not just recommended, due to the callout restriction on immediate paths. [AB:consent-manage-mcn]
- No article states field caps, timings beyond the above, row counts, or refresh schedules for consent import batch sizes — **unknown**, not covered by this KB.
- Consent semantics differ between MCE and MC Next: **Engagement checks consent at the subscriber level; Next checks consent at the Contact Point (email/phone) plus Communication Subscription level.** If two subscriber records share one email and that address opts out, both are suppressed in Next (only the opted-out record is suppressed in Engagement). Households sharing an email are the classic edge case — test it. A global opt-out at the Contact Point level is planned for Winter '27, not yet available. [AB:worth-migrating-mcn]

## Gotchas

- **"Add Data Protection Details to Records" (S15, a Basic Settings checklist item) is not the same thing as "physical address" (a Set Up Email item)** in the articles' own structure — one notes file cross-references them as related, but no article walks through what clicking the Basic Settings S15 item itself configures. Flag as an open item (see `90_open_items_a live org.md`).
- Communication Subscription Consent Id format is `<email>#<CommunicationSubscriptionChannelTypeId>` — get this wrong and the consent record will not match. Communication Subscription (channel-agnostic, e.g. `0XlHs...`) and Communication Subscription Channel Type Id (channel-specific, e.g. `0eBHs...`) are easy to confuse. [AB:consent-manage-mcn]
- No article names the underlying DMO/object for MC Next consent storage directly (inferred: likely a CommSubscriptionConsent-style object, not confirmed).
- "Marketing Cloud Growth" vs "Marketing Cloud Next" vs "Marketing Cloud Advanced" — terminology inconsistency across articles referring to the same product, not a functional difference. See `91_contradictions.md`.

## Automation route

- Physical address, Consent Validation toggles, Subscriptions: **UI-only**.
- Consent Imports: CSV upload via the Consent Imports UI tool — **UI-only** per this KB; no REST/Bulk API path mentioned.
- **Automated opt-in IS achievable via Salesforce Flow** using the standard `MessagingConsent.MessagingConsent` action element — UI-configured (Flow Builder) but the underlying action is a documented Salesforce automation action, not a hand-rolled API call.

## Verification

- Company Information shows the address (UI).
- Subscriptions list shows Marketing + any new subscription (UI).
- Consent Imports history / resulting opted-in status on individual records (UI; no query object name confirmed by any article for direct SOQL verification of consent state).
- (inferred) Check the Consent Status widget on the Lead/Contact record as the most direct per-record verification available from this KB.

## Sources

[AB:consent-compliance-mcn] How to ensure Compliance with Consent Settings in Marketing Cloud Next
[AB:consent-manage-mcn] How to manage consent in Marketing Cloud Next
[AB:consent-mce-bridge-mcn] How to manage Consent between Marketing Cloud Engagement and Marketing Cloud Next
[AB:configure-mcn] How to configure Marketing Cloud Next
[AB:worth-migrating-mcn] Is it worth migrating to Marketing Cloud Next now
