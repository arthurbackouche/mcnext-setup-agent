# Flows and first test send

Covers check S14 (segment-triggered flows / flow types available; also the minimum path to a first test send).

## Steps

### Minimum path to a first test send (Single Email Flow)

1. Marketing App > Campaigns tab > New. Fill Campaign Name, Status, Description. [AB:send-email-mcn]
2. Brief tab: choose existing or create new brief (Brief Name, Description, Target Audience, Key Message, Additional Information). [AB:send-email-mcn]
3. Campaign Members tab: add Leads/Contacts. [AB:send-email-mcn]
4. Create a Flow from the Campaign record. Flow types available: **Single Email, Signup Form, Blank Event, Message Series, Blank Email.** [AB:send-email-mcn]
5. Single Email Flow: set Schedule (audience entry timing; does not start until flow is activated). [AB:send-email-mcn]
6. Set Segment: options are Use Quick Filters, Send to Campaign Members, Go to Segment Builder, Select an Existing Segment. Publish the segment. [AB:send-email-mcn]
7. Select Email Message: pick or create an Email Template. [AB:send-email-mcn]
8. Configuration: select the Sender and the Communication Subscription channel. [AB:send-email-mcn]
9. Optional Next Steps: second email and/or Wait. Activate the campaign/flow. [AB:send-email-mcn]
10. **No Data Graph or identity resolution is required for this simplest path** — those only matter once personalisation from Data 360 fields is needed, or on-demand/decisioning flows are used. (batch E cross-cutting)

### Segment-triggered flows (S14, direct evidence)

11. Create flow, choose flow type = **Segment Triggered Flow** — this is direct evidence the flow type exists and is selectable at creation. [AB:ab-test-flow-mcn]
12. Configure Segment Triggered section: When (schedule) and Who (segment selection). [AB:ab-test-flow-mcn]
13. Drag Path Experiment Component onto canvas for an A/B test — splits into Path A and Path B automatically. For each path, drag an Email Templates Element, select the template, and **specify the sender for each email message** (stated failure mode if forgotten). [AB:ab-test-flow-mcn]

### On-Demand Flows (second flow type relevant to S14; enables near-real-time transactional sends)

14. Flow tab > New Flow > search "On-Demand Flow" as the type. Select a Data Graph for the flow (required — ties to S11). Add an action (e.g. email component), Save, Activate. [AB:on-demand-flow-mcn]
15. Click the Gear to edit version properties, copy the **Flow API Name**.
16. On the Flow, click Sharing, select the user that will call the API, and confirm that user is a **Flow User** — "something very important", easy to miss. [AB:on-demand-flow-mcn]
17. Salesforce Setup > External Client Apps > Settings > enable "Allow access to External Client App consumer secrets via REST API". [AB:on-demand-flow-mcn]
18. Setup > External Client App Manager > New. Enable OAuth = True; Callback URL; OAuth Scopes = "api", "refresh_token"/"offline_access"; Enable Client Credentials Flow = True; Require secret for Web Server Flow = True; Require secret for Refresh Token Flow = True; Require PKCE = True. [AB:on-demand-flow-mcn]
19. Edit Policies: enable Client Credentials Flow tickbox, enter the Salesforce username that will run it. Settings tab > Consumer Key and Secret. [AB:on-demand-flow-mcn]
20. POST `https://<MyDomain>.my.salesforce.com/services/oauth2/token` (`grant_type=client_credentials`, `client_id`, `client_secret`) → `access_token`. [AB:on-demand-flow-mcn]
21. POST `https://<MyDomain>.my.salesforce.com/services/data/v65.0/actions/custom/flow/<Flow_API_Name>` with `Authorization: Bearer <access_token>`, body `{"inputs":[{"EmailAddress": "...", "IndividualId": "..."}]}`. Success = HTTP 200 and email is sent. [AB:on-demand-flow-mcn]

## Limits

- On-Demand Flow starts **approximately 30 seconds** after the API event. [AB:on-demand-flow-mcn]
- Event latency from Engagement to Flow (during a migration): **15 minutes to 1 hour** — not suitable for real-time transactional triggers; use the On-Demand Flow REST trigger instead. [AB:worth-migrating-mcn]
- Journey Decisioning Agent suits segments **under 20,000** (consumes Flex credits). [AB:worth-migrating-mcn]
- First Flow recommended to stay under **1 million audience per hour**. [AB:worth-migrating-mcn]
- No split-percentage stated for the A/B Path Experiment component.

## Gotchas

- Forgetting the sender on one path of an A/B Path Experiment is a stated, explicit failure mode. [AB:ab-test-flow-mcn]
- Forgetting to mark the API-calling user as a Flow User, or forgetting to share the flow with them, breaks the On-Demand Flow REST trigger silently. [AB:on-demand-flow-mcn]
- Identity resolution is optional at Level 1-2 of Flow orchestration but **mandatory for Level 3 Journey Decisioning**. [AB:worth-migrating-mcn]
- Flow orchestration explicitly needs "connected data, a Data Graph to expose data to Flow, audiences and events created" — this is the direct link from S14 back to S11 and S10.

## Automation route

- **Building/activating/sharing the flow, and creating the External Client App, are UI-only in Setup.**
- **Triggering an already-built and shared On-Demand Flow IS a genuine REST API route** (`services/data/v65.0/actions/custom/flow/<name>`), including the OAuth token request. This is one of the few confirmed non-UI paths in the whole KB.
- Segment-triggered flow creation, A/B Path Experiment, and Single Email Flow are all UI-only.

## Verification

- `sf data query -q "SELECT ProcessType, COUNT(Id) FROM FlowDefinitionView GROUP BY ProcessType"` — look for marketing/segment-triggered process types (per this skill's own S14 check).
- Activate button available and clicked implies the flow is live (no explicit article-given verification step for the simplest Single Email Flow — inferred: check FlowDefinitionView or Campaign status).
- HTTP 200 response and an email received in the test inbox confirms the On-Demand Flow REST route end-to-end.
- Confirming "Segment Triggered Flow" and "On-Demand Flow" both appear as selectable flow-type options at flow creation is itself the S14 verification.

## Sources

[AB:send-email-mcn] How to send an email with Marketing Cloud Next
[AB:ab-test-flow-mcn] How to set-up an A/B Test Flow in Marketing Cloud Next
[AB:on-demand-flow-mcn] How to Trigger On-Demand Flows with REST API in Marketing Cloud Next
[AB:worth-migrating-mcn] Is it worth migrating to Marketing Cloud Next now
