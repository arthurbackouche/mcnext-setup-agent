# Canonical end-to-end setup order

One merged order across all five notes batches, from licences to first test send. "X needs Y first" dependencies and timings are called out inline. Where sources disagree, see the "Disagreements" section at the end and `91_contradictions.md` for full detail.

This order assumes licences/entitlement already exist (S1/S2 pass). If they do not, stop per the skill's `NOT_PROVISIONED` verdict — this is a provisioning request, not a setup task.

## Phase 0: licences and permissions (needs: nothing) — see `10_permissions_users.md`

1. Confirm Data 360 / MC Next entitlement exists (S2). Out of scope for this file if missing.
2. Assign **Data Cloud Architect** (may show as "Data Cloud Admin" on older orgs) to the implementer. `sf org assign permset`.
3. Refresh the browser. Data Cloud Setup now appears in the gear-icon menu.

## Phase 1: enable Data 360 (needs: Phase 0) — see `11_data360_enablement_basic_settings.md`

4. Setup > Data Cloud Setup > **Get Started**. Automatic: instance, metadata, Customer 360 model, readiness check. No fixed timing given in the KB.
5. Assign **Marketing Cloud Admin** to the implementer. Required before the Basic Settings Data Space picker will be usable — greyed-out picker is the standard symptom of a missing assignment.

## Phase 2: CRM connector (needs: Phase 1) — see `13_crm_connector_streams_mapping.md`

6. Data 360 app > Data Streams > New > **Salesforce CRM** > **Sales Bundle** (Account, User, OpportunityContactRole, Opportunity, Contact, Lead) or **Objects individually** for custom objects.
7. Review/select fields (standard fields default-selected; custom and formula fields need manual selection). Select Data Space. Deploy.
8. For custom objects (e.g. a custom subscription object, a custom credit object): the stream lands as a DLO only. Map it to a DMO via the Data Stream's **Data Mapping > Start** button before any Data Graph or segment can use it.

## Phase 3: Basic Settings "Enable Data Cloud" checklist (needs: Phase 2 for the connector item) — see `11_data360_enablement_basic_settings.md`

9. Setup > Assistant Home > Basic Settings > complete: Create Salesforce CRM Connector (done in Phase 2) > Add a Default Email Channel > Add Data Protection Details to Records > Select a Data Space ("Default") > **Enable Marketing Cloud** (last).

## Phase 4: Marketing Data Kits (needs: Phase 3) — see `12_data_kits.md`

10. Same Basic Settings page (or, in some orgs, a single "Update" button covering all kits): install Sales, Marketing Setup Objects, Consent Objects, Flows Integration, Email Channel Data Kits, plus SMS/WhatsApp Channel kits if licensed, and External Tracking kit if web tracking is used. **Up to 30 minutes.**

## Phase 5: identity resolution (needs: Phase 2 data existing to resolve) — see `15_identity_resolution.md`

11. Basic Settings > "Set Up Identity Resolution" > **Generate Ruleset** if offered, else **Manually Create One**.
12. Create a ruleset on Data Model Object "Individual". Match rules seen in this KB: Normalised Email (Contact Point Email, exact normalised), Fuzzy Name and Normalized Email (combined), Lead to Contact (Identity Match Type = lead-to-contact), MC Subscriber Key (for MCE-sourced individuals, needs Phase 7 first).
13. Save, **Run the Ruleset**. Review the Consolidation Rate. Produces the Unified Individual DMO — read its exact, org-specific name from Basic Settings (do not hardcode).

## Phase 6: custom field mapping for segmentation (needs: Phase 2, parallel with Phase 5) — see `13_crm_connector_streams_mapping.md`

14. On the Data Stream, **Add Source Fields** to pull in fields missed by the bundle default, then **Review** to map each to an existing or new DMO field. Anything needed for segmentation must be explicitly mapped — existing on the Salesforce object is not enough.

## Phase 7: MCE (Engagement) connector (needs: Phase 1; independent of Phases 2-6 but converges with Phase 5 for Subscriber Key matching) — see `14_mce_connector.md`

15. In MCE: create an integration user with Marketing Cloud Administrator + Administrator permission sets (API user, parent BU if multi-BU).
16. Data Cloud Setup > Marketing Cloud Engagement tab > New. Wizard: Enter Credentials (login window — stop and hand back to user) > Data Source Set-up (BUs + bundle categories Email/MobileConnect/MobilePush) > Select Business Units to Activate.
17. Separately, Data 360 app > Data Streams > New > Marketing Cloud > Bundle or individual Data Extensions > Deploy.
18. For custom Subscriber DEs, add Party Identification formula fields and map to Individual + Party Identification DMOs, then add the MC Subscriber Key match rule to the Phase 5 ruleset.

## Phase 8: Data Graph (needs: Phase 5 Unified Individual to exist) — see `16_data_graph.md`

19. Marketing Setup > Customer Engagement > Data Graphs > New > start from scratch. Primary DMO = **Unified Individual**. Related DMOs: Unified Indv Contact Point Email/Phone/Address. To reach "Individual" DMO, also add "Unified Link Individual" as the join.
20. Select all fields recommended per related object. **Save and Build**, set refresh schedule (30 minutes to 1 month). [FIELD] a live org limits: 50 fields/object, 200/graph.
21. Add custom DMOs (custom objects such as subscriptions or credits, once mapped in Phase 6/Phase 2) as related objects once ingested.
22. Confirm this graph is selected at Assistant Home > Customer Engagement > **Configure Basic Personalization**.

## Phase 9: Set Up Email — domains, consent, compliance (needs: Phase 3 email channel item; independent of Phases 5-8) — see `17_email_channel_domains.md`, `18_consent.md`

23. Authenticated Domains > Add a Domain (dedicated subdomain) > DNS records at registrar > **up to 72 hours** to validate.
24. From Addresses (per-purpose senders) and Reply Mail Management, both under the validated domain.
25. Physical address (Company Information), Consent Validation settings, Subscriptions (default "Marketing" exists).
26. **Consent Import (mandatory)**: every Individual starts Opted Out in MC Next. CSV import via Consent Imports tool (Channel + Subscription), or build a Record-Triggered Flow using `MessagingConsent.MessagingConsent` (1-minute scheduled-path delay, mandatory) for ongoing automated opt-in.
27. If migrating from MCE: bridge existing consent via MCE DE + Automation Studio SQL export > SFTP CSV > same Consent Imports tool. One-time/repeatable, not a live sync.

## Phase 10: Einstein toggles (needs: Phase 8 Data Graph for 3 of 4 features; Phase 5 identity resolution for STO) — see `19_einstein.md`

28. Einstein Metrics Guard: no prerequisite, toggle only.
29. Einstein Engagement Frequency / Scoring: enable toggle, then manually add the relevant DMO to the Phase 8 Data Graph (enabling alone does not wire it in). Frequency needs 10 subscribers / 5 variants over 28 days minimum to activate modeling.
30. Einstein Send Time Optimization: needs Phase 5 (Identity Resolution Ruleset on Individual) and Phase 8 (Data Graph) done first. Global model takes up to 72 hours to activate.

## Phase 11: Analytics packages (needs: Phase 4 data kits) — see `20_analytics.md`

31. Setup > Analytics (under Reporting and Optimization, a different menu than Marketing Performance): install Marketing Engagement Analytics, SMS Analytics, Landing Pages and Forms Analytics, Flow Reports Analytics. Then **Share Access to Analytics Folders** (separate required step).

## Phase 12: page customization, scoring, segments, personalization, sites (needs: Phase 5 for scoring rules; Phase 8 for merge fields and Salesforce Personalization) — see `22_personalization_segments_sites.md`

32. Customer Engagement Scoring Rules (Engagement + Fit Score), publish, add Data Cloud Profile Insights LWC to Contact/Lead pages.
33. Salesforce Personalization: needs a Data Graph to already exist; Deploy Foundation Data; assign Personalization Intelligence User permission set.
34. Segments: build in Visual Builder, choose type (Standard/Waterfall/Real-Time/Dynamic — Real-Time needs a Real-Time Data Graph), Save, then **Publish separately**.
35. Landing pages, external site tracking (needs External Tracking Data Kit), form handlers (needs CORS domain) as optional, parallel work.

## Phase 13: first test send (needs: Phase 3 Marketing app enabled, Phase 9 sender + at least one opted-in test contact, one email template) — see `21_flows_and_sends.md`

36. Marketing App > Campaigns > New > Brief > Campaign Members > create a Flow (Single Email) > Segment (Quick Filters/Campaign Members/Segment Builder/Existing Segment) > Email Message > Configuration (Sender + Communication Subscription channel) > Activate.
37. This minimum path needs **no Data Graph and no identity resolution** — those only matter once personalisation or decisioning flows are used.
38. Merge-field personalisation in the email requires Phase 8 (Data Graph) and a test recipient who is opted-in (Phase 9).
39. Segment-triggered and On-Demand flow types are confirmed available at flow creation (S14) once the Marketing app is enabled; On-Demand additionally needs a Data Graph selection, Flow Sharing to the API user (Flow User), and an External Client App with OAuth for the REST trigger.

## Disagreements between sources on this order

- **Ruleset auto-generation availability**: one arthurbackouche.com implementation had no "Generate Ruleset" button and had to build manually; [FIELD] a live org did have one and used it. Do not assume either path — check what the org offers.
- **Data Kits list length**: 5 kits inside the Basic Settings wizard vs 7+ in the full catalogue (SMS/WhatsApp Channel added) — not a contradiction, a scope difference. [FIELD] a live org has a single "Update" button for all data kits, not per-kit installs.
- **Segment activation-to-MCE timing**: 30 minutes vs 24 hours stated in two different articles — treat 24 hours as the safer planning number (see `91_contradictions.md`).
- **Data Graph refresh cadence**: "every few seconds" (Standard, one article) vs a user-configurable 30-minutes-to-1-month schedule (two other articles) — treat the configurable schedule as operative for the UI in this KB; see `91_contradictions.md`.
- **Unified Individual DMO naming**: not a fixed string in either the arthurbackouche.com corpus or a live org — always read the actual name from Basic Settings or the ruleset output.

## Sources

Synthesized from batch A (foundation setup, permissions, brand), batch B (email channel, consent), batch C (Data 360 ingestion, MCE connector, mapping), batch D (personalization, Data Graph, Einstein, analytics, segments), batch E (flows, sites, agents, migration), plus [FIELD] a live org facts. Full per-topic sources are listed in files `10_` through `23_`.
