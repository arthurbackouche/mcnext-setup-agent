# Personalization, segments, sites, forms, page customization

Covers check S20 (Page Customization / LWC widgets) plus segments, Salesforce Personalization, landing pages, external site tracking, and form handlers (no dedicated S-check, noted as gaps below).

## Steps

### Customer Engagement Scoring Rules (feeds S11 personalisation and S20 page widgets)

1. Prerequisite: an Identity Resolution Ruleset must already exist. Setup > Assistant Home > Customer Engagement tab > "Set Up Customer Engagement Support" > "Customize Scoring Rules" > "Go to Scoring Setup" > New > name/description > select "People" > Next > select the Identity Resolution Ruleset > Create. [AB:scoring-rules-mcn]
2. Optionally "Edit Score Ratio" to change the default 50/50 Engagement Score vs Fit Score split. [AB:scoring-rules-mcn]
3. Engagement Score Rules: **up to 30 rules**; 5 ship by default (+5 subscribe, +3 click message, -5 unsubscribe message, +3 click email, -5 unsubscribe email). Fit Score Rules: **up to 30 rules**; 1 ships by default (Country = United States, +3). [AB:scoring-rules-mcn]
4. Publish and choose a refresh schedule, **1 to 24 hours**. [AB:scoring-rules-mcn]
5. **Page Customization (S20)**: add "Data Cloud Profile Insights" LWC to the Contact page: Setup > Object Manager > Contact > Lightning Record Pages > edit default page > drag component. Fields: Match On = Contact ID, Data Space = Default, Unified Individual DMO, Unified Individual Link DMO, Calculated Insight = Overall Marketing Score, Measure = People_Score. Duplicate 3x for Global/Engagement/Fit Score. [AB:scoring-rules-mcn]
6. Other named LWC widgets for Page Customization: **Privacy Consent Status**, **Data 360 Profile Engagement**, **Data 360 Profile Insights**, addable to Contact/Lead/Prospect/Campaign layouts. [AB:setup-mcn]
7. Editing a scoring rule **retroactively rescores all customers** — scores update retroactively when rules change. [AB:scoring-rules-mcn]

### Salesforce Personalization (separate product from email Data Graph merge fields)

8. Hard prerequisite: "Create a Salesforce DataGraph" first. Setup > Assistant Home > "Set Up Marketing Performance" > "Go to Personalization" inside "(Optional) Set Up Salesforce Personalization". [AB:sf-personalization-mcn]
9. "Deploy the Foundation Data": select data space (Default), Deploy. Creates 4 DMOs (Personalization Point, Personalization Decision, Personalizer, Personalization Log) and 2 Calculated Insights ("Insights Daily Personalization Requests", "Daily Personalization Uniques"). [AB:sf-personalization-mcn]
10. Assign permission set **"Personalization Intelligence User"**. Schedule both Calculated Insights daily (24h refresh) in the Data Cloud app. Install the "Personalization Pipeline Intelligence Dashboard". Verify via Personalization tab > "Personalization Intelligence" tab. [AB:sf-personalization-mcn]
11. Optional: Attribution Model (Browse Products, Add To Cart, Purchase) — installs 3 more DMOs (Product Browse Engagement, Shopping Cart Engagement, Product Order Engagement). Skip if not selling online. [AB:sf-personalization-mcn]
12. This is a distinct product from "Marketing Cloud Personalization" (separate legacy product, explicitly not enabled in the walkthrough). [AB:sf-personalization-mcn]

### Segments

13. Marketing App > "Segments" tab > New. Creation method: Visual Builder (most common), Create with Einstein Segment Creation (natural-language, verify results before trusting), or Install from Data Kits (pre-built). [AB:segment-create-mcn]
14. Segment type: Standard Segment (DMO + rule conditions), Waterfall Segment (ordered sub-segments, first match wins), Real-Time Segment (needs a **Real-Time Data Graph**, for Triggered Campaign Flows), Dynamic Segment (static + dynamic conditions at send time). [AB:segment-create-mcn]
15. Segment Properties: Data Space, Segment Name, "Segment On" DMO (e.g. Unified Individual), Description. [AB:segment-create-mcn]
16. Publish Type: Standard Publish (2 years look-back, usable in any activation target) or Rapid Publish (7 days look-back, refreshes more frequently). Publish Schedule (Hourly/Daily/Weekly/Monthly) and Lookback Window. [AB:segment-create-mcn]
17. Define Segment Criteria: Direct Attributes (fields on the selected DMO) and Related Attributes (fields on connected DMOs). Save > Done > Status becomes "Active". **Publish separately** so the segment is usable in a Campaign Flow / Activation Target — Active and Published are two distinct states. [AB:segment-create-mcn]
18. Custom DMOs like custom objects (e.g. subscription or credit records) would appear as Related Attributes here once added to Unified Individual (inferred).

### Landing pages, sites, forms

19. Content tab > Content Workspace for Marketing Cloud > Add > Landing page > "use Components" to build from scratch. Settings: Title, API Name, Content Slug, Favicon, Head Tags, indexing toggle. Style: background image. Data Sources: optionally select a Data Graph for merge-field personalisation. Components: Button, Divider, Heading, HTML, List, Paragraph, Form, Section, Image. [AB:landing-page-mcn]
20. Builder is explicitly not comparable to Wix/Elementor/Framer — set expectations. [AB:landing-page-mcn]
21. **External site tracking**: Setup > Web Tracking > External Websites > set "Require Consent to Track"; install the **External Tracking Data Kit** (not in the standard S8 list, enables Web Engagement DMOs); create a Website Connector; Data 360 > Data Streams > New > Installed Data Kits & Packages > "External Tracking" bundle > select connector > Deploy (2 streams: identity, Behavioral Events). Also create a second CRM stream for bundle "MarketingStreamingAppConfig" to link tracking to a Campaign. Manage Website Connectors > select connector > Related Campaign > Save > copy tracking script > add to site header > Publish/Activate. [AB:external-sites-mcn]
22. **Landing page activity tracking** (MC Next-hosted pages, different from external site tracking above): Setup > All Site > Builder on the site > Settings > Security & Privacy > "Relaxed CSP: Permit Access to inline Scripts and Allowed Hosts" > Integration tab > add Data Cloud to Site > Advanced > Edit Head Markup > add script dispatching `experience_interaction` event `{name: 'set-consent', value: true}`. [AB:track-landing-mcn]
23. **Form Handlers** (ingest an existing external form without rebuilding it): Content tab > Workspace > Add > Content > Form Handler > select Data Source object (Contact/Lead/Prospect/Account) > drag & drop fields to map > reference field attribute IDs from the actual website form > Details (Title, API Name, Description) > Submission redirect URL (required to save) > Save > create/confirm auto-populated Flow that creates the record > Publish > copy generated scripts into the website > Setup > CORS > Add domain. [AB:form-handlers-mcn]

## Limits

- Engagement/Fit Score Rules: max 30 each; refresh 1-24 hours; default ratio 50/50. [AB:scoring-rules-mcn]
- Segment Standard Publish look-back = 2 years; Rapid Publish = 7 days. Example population 5,600 (illustrative). [AB:segment-create-mcn]
- Calculated Insights for Personalization scheduled daily (24h) in the walkthrough. [AB:sf-personalization-mcn]

## Gotchas

- Real-Time Segments require a **Real-Time Data Graph specifically**, not the Standard one used for email personalisation — relevant if the org's personalization graph is Standard only. [AB:segment-create-mcn]
- Einstein Segment Creation (natural language) is flagged by the author as needing extra verification of results. [AB:segment-create-mcn]
- A segment must be both Saved/Active and separately Published before it can be used downstream — two distinct states, easy to miss. [AB:segment-create-mcn]
- Without the Relaxed CSP setting, inline scripts (like the consent script) may be blocked on a Marketing Landing Page site. [AB:track-landing-mcn]
- Submission redirect URL is required to save a Form Handler — cannot skip. CORS must include the domain or cross-domain submissions fail. [AB:form-handlers-mcn]
- **No S-check in the skill's current list directly covers CORS or Form Handlers** — noted as a gap. [AB:form-handlers-mcn]

## Automation route

- **UI-only** for every step in this file — scoring rules, Salesforce Personalization deploy, segment creation/publish, landing pages, web tracking, form handlers, page customization LWC widgets. No REST/SOQL/Metadata alternative given anywhere in this KB for these features.
- Permission set assignment (Personalization Intelligence User) could plausibly be done via `sf org assign permset` once the exact API name is confirmed (inferred; article shows UI assignment only).

## Verification

- Contact/Lead record page shows the Data Cloud Profile Insights component with a People_Score value.
- Foundation DMOs visible in Data Cloud Data Model; Calculated Insights tab shows the two Personalization insights with 24h schedule; Personalization Intelligence tab loads a dashboard.
- Segment Status shows "Active"; Population count displays; after Publish, segment is selectable in Campaign Flow entry criteria and Activation Target configuration.
- Landing page: preview/publish and confirm public URL resolves (inferred).
- External tracking: the two data streams show status Active/Deployed; Website Engagement DMO populates after the script goes live (inferred).
- Form Handler: submit a test form and confirm a Contact record is created via the auto-generated Flow (inferred).

## Sources

[AB:scoring-rules-mcn] How to set up Customer Engagement Scoring Rules in Marketing Cloud Next
[AB:sf-personalization-mcn] How to Setup Salesforce Personalization for Marketing Cloud Next
[AB:segment-create-mcn] How to create a Segment in Marketing Cloud Next
[AB:landing-page-mcn] How to create a Landing Page in Marketing Cloud Next
[AB:external-sites-mcn] How to integrate External Sites in Marketing Cloud Next
[AB:track-landing-mcn] How to Track Activity on Landing Pages in Marketing Cloud Next
[AB:form-handlers-mcn] How to use Form Handlers in Agentforce Marketing
[AB:setup-mcn] How to set-up Marketing Cloud Next
