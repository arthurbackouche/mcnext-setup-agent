# Batch D: personalization, Data Graph, Einstein, analytics, segments

Source folder: `out/kb/arthurbackouche/raw/`. 12 files, arthurbackouche.com only.

### How to set up Customer Engagement Scoring Rules in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/customer-engagement-and-personalization/how-to-set-up-customer-engagement-scoring-rules-in-marketing-cloud-next/
- Purpose: build a combined Engagement Score + Fit Score per person and surface it on Contact/Lead pages and in Flows/Segments.
- Prerequisites and order: needs an Identity Resolution Ruleset already created (selected when creating the scoring model). Unblocks: Flow Decision/Trigger elements, Segment criteria, and a Data Cloud Profile Insights component on Contact/Lead record pages.
- Steps:
  1. Setup > Assistant Home > Customer Engagement tab > "Set Up Customer Engagement Support".
  2. In "Customize Scoring Rules" click "Go to Scoring Setup".
  3. Click New, give name/description, select "People", click Next.
  4. Select an existing Identity Resolution Ruleset, click Create.
  5. Optionally click "Edit Score Ratio" to change the 50/50 Engagement Score vs Fit Score split.
  6. Engagement Score Rules: up to 30 rules, each adds or subtracts points; 5 rules ship by default (+5 subscribe, +3 click message, -5 unsubscribe message, +3 click email, -5 unsubscribe email). New Rule or pen icon to edit; a rule is a condition on a DMO field, e.g. Unified Individual > Individual > Message Engagement > Engagement Channel Action Id = SUBSCRIBE. Multiple conditions and groups supported.
  7. Fit Score Rules: up to 30 rules, 1 ships by default (Country = United States, +3). Same New/Edit flow, based on demographic/firmographic fields.
  8. Click Publish and choose a refresh schedule, 1 to 24 hours.
  9. Add "Data Cloud Profile Insights" LWC to the Contact page: Setup > Object Manager > Contact > Lightning Record Pages > edit default page > drag component. Fields: Match On = Contact ID, Data Space = Default, Unified Individual DMO = Unified Individual DMO, Unified Individual Link = Unified Individual Link DMO, Calculated Insight = Overall Marketing Score, Measure = People_Score. Duplicate the component 3x for Global/Engagement/Fit Score.
- Limits and numbers: max 30 Engagement Score Rules, max 30 Fit Score Rules, refresh 1-24 hours, default ratio 50/50.
- Gotchas: editing a rule retroactively rescoring all customers (article states scores update retroactively when rules change).
- Automation route: UI-only for scoring model creation, rule authoring, publish. The Contact page layout change (drag LWC) is also UI-only in Object Manager/Lightning App Builder. (inferred: the underlying scoring model and Calculated Insight objects are metadata, but the article gives no API/CLI route, so treat as UI-only.)
- Verification: Contact/Lead record page shows the Data Cloud Profile Insights component with a People_Score value; Flow Decision/Trigger elements list the scoring model as an option; Segment builder lists scoring fields as criteria.
- Maps to setup checks: S11 (feeds Data Graph personalization via Unified Individual), S20 (record page component), S14 (scoring usable in segment-triggered flows), S6/S5 (permission needed to configure, inferred).

### How to Setup Salesforce Personalization for Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/customer-engagement-and-personalization/how-to-setup-salesforce-personalization-for-marketing-cloud-next/
- Purpose: enable Salesforce Personalization (web/product personalization) fed by Data Cloud, separate from email Data Graph merge fields.
- Prerequisites and order dependencies: explicit prerequisite stated: "Create a Salesforce DataGraph" before starting this setup. Unblocks: web personalization decisions, Personalization Pipeline Intelligence dashboard, optional Attribution Model (revenue tracking).
- Steps:
  1. Setup > Assistant Home > "Set Up Marketing Performance".
  2. Click "Go to Personalization" inside "(Optional) Set Up Salesforce Personalization".
  3. "Deploy the Foundation Data": select data space (Default), click Deploy. This creates 4 DMOs: Personalization Point, Personalization Decision, Personalizer, Personalization Log. Also creates 2 Calculated Insights: "Insights Daily Personalization Requests", "Daily Personalization Uniques".
  4. Assign permission set "Personalization Intelligence User" to the running user.
  5. In the Data Cloud app, Calculated Insights tab, edit both Calculated Insights above and schedule them daily (24-hour refresh).
  6. Back in Salesforce Personalization Setup, "Install the Personalization Pipeline Intelligence Dashboard" section, click Install.
  7. Verify access via Personalization tab > "Personalization Intelligence" tab (dashboard on pipeline health/attribution).
  8. Optional: activate the Attribution Model to track revenue (Browse Products, Add To Cart, Purchase). Installs 3 more DMOs: Product Browse Engagement, Shopping Cart Engagement, Product Order Engagement. Skip if not selling online.
  9. A further optional feature is only needed if using Marketing Cloud Personalization alongside Salesforce Personalization; article does not enable it.
- Limits and numbers: Calculated Insights refresh set to 24 hours (daily) in this walkthrough.
- Gotchas: this is a distinct product from the email Data Graph feature; it requires a Data Graph to already exist as a hard prerequisite. Confusable with "Marketing Cloud Personalization" (separate legacy product, explicitly not enabled here).
- Automation route: UI-only (Setup wizard, Deploy button, permission set assignment could be done via `sf org assign permset -n Personalization_Intelligence_User` (inferred name) but article shows UI assignment; Calculated Insight schedule editing is UI, in the Data Cloud app).
- Verification: Foundation DMOs visible in Data Cloud Data Model; Calculated Insights tab shows the two insights with 24h schedule; Personalization Intelligence tab loads a dashboard; permission set assignment visible via `PermissionSetAssignment` query (inferred).
- Maps to setup checks: S11 (hard prerequisite: Data Graph must exist first), S5/S6 (Personalization Intelligence User permission set), S9 (data space selection during Deploy), S18 (adjacent to analytics/dashboards, different install path than S18's Analytics packages).

### How to use Data Graph in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/customer-engagement-and-personalization/how-to-use-data-graph-in-marketing-cloud-next/
- Purpose: explains why Data Graph matters for email merge-field personalization and gives the basic build steps.
- Prerequisites and order dependencies: none stated explicitly beyond having DMOs available; this Data Graph is a prerequisite for Email Builder merge fields (Data Source tab in Email Builder previews the graph selected).
- Steps:
  1. Marketing Setup > "Customer Engagement" > "Go to Data Graphs".
  2. Data Graphs list view shows existing graphs.
  3. Click New > "start from scratch".
  4. Select the primary Data Model Object: recommended "Unified Individual". Give Name and Description.
  5. Select related DMOs used for email sends: recommended "Unified Indv Contact Point Address", "Unified Indv Contact Point Email", "Unified Indv Contact Point Phone".
  6. Tick checkboxes for each field to import from every selected object; article recommends selecting all fields.
  7. Click "Save and Build"; a pop-up asks for a refresh schedule.
- Limits and numbers: refresh schedule options range from every 30 minutes to once a month. No field-count cap stated in this article.
- Gotchas: none stated beyond needing the right related DMOs for the send channel in use.
- Automation route: UI-only ("Data Graphs" list view, New > start from scratch, checkboxes, Save and Build). No API mentioned.
- Verification: new graph appears in Data Graphs list view; Email Builder Data Source tab shows the graph and its fields available as merge fields.
- Maps to setup checks: S11 (core how-to for building the graph), S13 (email channel merge fields depend on it, inferred).

### Understanding Data Graph in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/customer-engagement-and-personalization/understanding-data-graph-in-marketing-cloud-next/
- Purpose: conceptual + step-by-step explanation of what a Data Graph is, why it exists, its cost model, and how to build and use one for email merge fields.
- Prerequisites and order dependencies: enabling Marketing Cloud Next itself prompts you to select a Data Graph (during MC Next enablement, not before). The graph is built from DMOs that must already exist (Unified Individual, Individual, Contact Point Email/Address, etc.), so Identity Resolution / DMO setup precedes this.
- Steps:
  1. During Marketing Cloud Next enablement you are asked to select a Data Graph.
  2. Assistant Home > "Customer Engagement" tab > "Configure Basic Personalization" section shows the currently selected Data Graph (example: "Data Graph: Unified Individual"). Click "Go to Data Graphs" to configure your own.
  3. On the Data Graphs page, click New > "Create from Scratch".
  4. In the New Data Graph pop-up: Name, Data Space (e.g. default), Primary Data Model Object = Unified Individual.
  5. Select related DMOs: common choices are Individual, Contact Point Email, Contact Point Phone, Contact Point Address, Email Engagement, Website Engagement. To reach the "Individual" DMO you must also select "Unified Link Individual" DMO, which acts as the identity-resolution link between Unified Individual and Individual.
  6. Select field attributes for each DMO, click "Save and Build", then set the Refresh Schedule.
  7. To use it: in Email Builder, the Data Source shown is the selected Data Graph (e.g. "Unified individual"). In a text/heading widget, click "Add a merge field" > "Select Data Graph Attribute" > pick a field (e.g. First Name). A pop-up lets you set a default/fallback text (e.g. "Customer") if the attribute is not found.
- Limits and numbers: no explicit field-count cap given. Cost: Data Graphs consume Data Cloud credits computed per build/refresh; track consumption via the Salesforce Digital Wallet. More frequent refresh = more credits consumed (explicitly stated trade-off).
- Gotchas: to relate the "Individual" DMO you need the "Unified Link Individual" DMO as the join, not a direct relationship; forgetting this link is a likely misconfiguration point (inferred, since the article calls it out specially). Also: a Data Graph is "always built from a single [primary] Data Model Object" — implies changing the primary DMO likely means starting a new graph rather than editing (inferred; article does not test this directly, but always describes primary as fixed at creation).
- Automation route: UI-only throughout (New > Create from Scratch, checkboxes, Save and Build, Email Builder merge-field picker). No REST/metadata alternative stated.
- Verification: Data Graph list view shows the graph; Email Builder Data Source tab references it; merge field renders with the chosen default text as fallback; Digital Wallet shows credit consumption tied to the graph.
- Maps to setup checks: S11 (primary how-to and cost/refresh rules), S10 (Unified Individual + Unified Link Individual as the identity-resolution join needed for related DMOs).

### How to setup Einstein Engagement Frequency in Marketing Cloud Next?
Source: https://arthurbackouche.com/docs/marketing-cloud-next/einstein-ai-features/how-to-setup-einstein-engagement-frequency-in-marketing-cloud-next/
- Purpose: score/classify customers by email send frequency tolerance (Saturated / AlmostSaturated / OnTarget / UnderSaturated) to reduce fatigue and unsubscribes.
- Prerequisites and order dependencies: needs an existing Data Graph to add the "Email Engagement Frequency" DMO to, so a Data Graph must exist first (built on Unified Individual per other articles). Unblocks: an Einstein Decision (Frequency) element in Flows.
- Steps:
  1. Setup > Assistant Home > "Set Up Email".
  2. Scroll to "Optional Setup" > "Go to Einstein Settings" in the "Enable Einstein Engagement Frequency" section.
  3. On the "Einstein for Marketing" page, click Enable.
  4. Edit your Data Graph and add the "Email Engagement Frequency" DMO as a related object; select field attributes "Email Engagement Classification" and "Email Engagement Frequency".
  5. In a Marketing Flow, drag the Einstein Decision element, select "Frequency". It splits into 4 sub-paths (article lists 5 in one place but enumerates 4 concretely): Saturated, AlmostSaturated, OnTarget, Undersaturated.
- Limits and numbers: minimum 10 subscribers required to model engagement frequency; minimum 5 frequency variants required (audience must receive at least 5 distinct send-interval variants over a 28-day period).
- Gotchas: modeling will not activate below the 10-subscriber / 5-variant/28-day thresholds (inferred consequence, not explicitly stated as an error message). The DMO must be manually added to an existing Data Graph — enabling the toggle alone does not wire it into flows.
- Automation route: UI-only (Assistant Home toggle, Data Graph edit, Flow Decision element). No API given.
- Verification: Data Cloud Object Explorer > "Email Engagement Frequency" DMO shows records with a populated "Email Engagement Classification" field; Flow shows the Einstein Decision element with Frequency sub-paths available.
- Maps to setup checks: S17 (Einstein toggle: Engagement Frequency), S11 (requires editing the Data Graph to add this DMO — direct evidence that editing an existing graph, not just building from scratch, is a supported and expected UI action).

### How to setup Einstein Engagement Scoring in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/einstein-ai-features/how-to-setup-einstein-engagement-scoring-in-marketing-cloud-next/
- Purpose: classify customers into personas (Loyalist, Selective Subscriber, Window Shopper, Winback/Dormant) and predict Open/Click/Subscribe likelihood, for use in Flow decisions.
- Prerequisites and order dependencies: like Engagement Frequency, requires an existing Data Graph to edit (article explicitly reuses "the 'New Data Graph' created in my article about Einstein Engagement Frequency" and adds to it). Unblocks: Einstein Decision (Scoring) element in Flows.
- Steps:
  1. Setup > Assistant Home > "Set Up Email".
  2. "Optional Setup" > "Go to Einstein Settings" in "Enable Einstein Engagement Scoring" section.
  3. On "Einstein for Marketing" page, click Enable.
  4. Edit the existing Data Graph, add "Einstein Engagement Score" DMO, select fields: Email Click Likelihood, Email Click Score, Email Subscribe Likelihood, Email Subscribe Score, Email Open Score, Email Open Likelihood, Email Engagement Persona.
  5. In a Marketing Flow, drag Einstein Decision element, select "Scoring". Sub-menu offers 4 split types: Open Likelihood, Click Likelihood, Subscribe Likelihood, Persona. Persona options: Loyalist, Selective Subscriber, Window Shopper, Winback/Dormant. Likelihood options (each of the 3 likelihood types): Most Likely, More Likely, Less Likely, Least Likely.
- Limits and numbers: none stated (no minimum volume given here, unlike Engagement Frequency).
- Gotchas: same as Frequency — must manually add DMO/fields to the Data Graph after enabling; the two Einstein features (Frequency and Scoring) can share the same Data Graph, built incrementally (confirmed by this article reusing the prior one's graph).
- Automation route: UI-only.
- Verification: Data Graph shows the added Einstein Engagement Score fields; Flow Einstein Decision element offers the Scoring sub-menu with Persona/Likelihood paths.
- Maps to setup checks: S17 (Einstein Engagement Scoring toggle), S11 (confirms incremental editing of one shared Data Graph across multiple Einstein features).

### How to setup Einstein Send Time Optimization in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/einstein-ai-features/how-to-setup-einstein-send-time-optimization-in-marketing-cloud-next/
- Purpose: predict the optimal send hour per recipient (global pooled model or org-specific model) to raise engagement.
- Prerequisites and order dependencies: explicit prerequisites for STO: (1) an Identity Resolution Ruleset created on the Individual DMO, (2) a Data Graph created so STO can be used in flows. Global model deployment takes up to 72 hours after enabling before it is usable. Org-specific model needs 90 days of the org's own send history as its data source.
- Steps:
  1. Setup > Assistant Home > "Email Channel Configuration".
  2. Click "Go to Einstein Settings" in "Activate Einstein Send Time Optimization" section.
  3. Enable "with global model (Pooled data)" — note this can take up to 72 hours to activate.
  4. (Org-specific model is a separate, later option once enough org email volume exists; article does not walk through enabling it, only describes it.)
  5. Usage: in a Campaign Flow's Email element, toggle Einstein Send Time Optimization on, and set "Send Emails Within" (a time window, e.g. next 24 hours) for the model to pick the actual send time.
  6. Monitoring: Report tab > "Data Cloud" > "Einstein Send Time Optimization" report, or "Contact Point Email with Email Send Time Optimization" report. Fields: Organization Id, Contact Point Email Id, Time of Week (0-167, Monday midnight = 0, Sunday 11pm = 167), Created Date.
- Limits and numbers: global model activation up to 72 hours; org-specific model uses trailing 90 days of send data; org-specific insights refresh weekly; Time of Week is a 0-167 integer scale.
- Gotchas: global model shares only anonymized data across orgs (no email address, company, etc., per the article), so this is not a privacy risk for enabling but also means predictions are generic until enough org-specific volume exists to switch models.
- Automation route: UI-only for enabling and flow usage. Monitoring is via a Report (readable object), not a raw SOQL-queryable custom object per this article, though the report is presumably backed by a DMO (inferred, not confirmed).
- Verification: Einstein Settings page shows the feature enabled; after 72 hours, STO toggle available inside an Email flow element; the two named reports return Time of Week data per Contact Point Email Id.
- Maps to setup checks: S10 (explicit prerequisite: Identity Resolution Ruleset on Individual DMO), S11 (explicit prerequisite: Data Graph must exist), S17 (Einstein STO toggle).

### What is Einstein Metrics Guard in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/einstein-ai-features/what-is-einstein-metrics-guard-in-marketing-cloud-next/
- Purpose: filter bot/scanner/auto-open (e.g. Apple Mail Privacy Protection) traffic out of Open/Click metrics so analytics reflect real human engagement.
- Prerequisites and order dependencies: none stated; it is a toggle independent of Data Graph or Identity Resolution.
- Steps:
  1. Setup > Assistant Home > "Set up Email" (Email section).
  2. Scroll down, click "Go to Email Feature Settings" in "Activate Einstein Metrics Guard" section.
  3. Turn on the "Einstein Metrics Guard" toggle.
- Limits and numbers: confidence score scale 0-100 (0 = bot, 100 = human). Built on two model types: time-series analysis and a predictive model. No timing/volume thresholds stated (contrast with Engagement Frequency's explicit minimums).
- Gotchas: model is trained on Salesforce's own aggregated (anonymized) customer data from MCE/Account Engagement history, not the org's own data alone — a data-provenance point worth flagging to the client, not a technical blocker.
- Automation route: UI-only (single toggle).
- Verification: toggle shows enabled state in Email Feature Settings; downstream, Open/Click reports would reflect filtered "human-confidence" engagement (article does not show a specific verifying report/field name).
- Maps to setup checks: S17 (Einstein Metrics Guard toggle — this is the only one of the 4 Einstein features listed in the setup checks that has no Data Graph or Identity Resolution prerequisite stated).

### How to install Analytics Packages in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/analytics-configuration/how-to-install-analytics-packages-in-marketing-cloud-next/
- Purpose: install the reporting/analytics packages that power Marketing Cloud Next's Campaign, Email, SMS, Landing Page/Form and Flow reports.
- Prerequisites and order dependencies: Marketing Data Kits must be deployed first (explicit "Pre-requisites" heading). Unblocks: Analytics tab reports/dashboards in the Marketing App.
- Steps:
  1. Setup > Assistant Home > "Marketing Performance" card > "Set Up Marketing Performance".
  2. On the Marketing Performance page, click "Go To Marketing Data" next to "Install Marketing Data Kits"; confirm all Marketing Data Kits are deployed.
  3. Setup > "Analytics" (located under "Reporting and Optimization", i.e. this is a separate Setup menu section, not the Marketing Performance page). Install packages there:
     - Marketing Engagement Analytics package (email interaction insights)
     - SMS Analytics package (SMS interaction insights)
     - Landing Pages and Forms Analytics Package
     - Flow Reports Analytics Package (flow action run counts/status)
  4. For each package, click "Install for Admin only" and confirm.
  5. Also required: "Share Access to Analytics Folders" so the team can see the reports.
  6. Access reports: Marketing App > Analytics tab, covering Email, SMS, Landing Pages & Forms, Flow Engagement.
- Limits and numbers: none given (no count of packages beyond the 4 named, no size/refresh numbers).
- Gotchas: the article's own package names are "Marketing Engagement Analytics", "SMS Analytics", "Landing Pages and Forms Analytics", "Flow Reports Analytics" — it does NOT use the terms "CRM Analytics" or "Marketing Performance Intelligence" anywhere. This does not resolve the CRM Analytics vs Marketing Performance Intelligence naming ambiguity; treat the 4 named packages above as the authoritative install list for S18, and flag the CRM Analytics / Marketing Performance Intelligence naming question as unresolved by this KB (see cross-cutting findings).
- Automation route: UI-only (Setup > Analytics install buttons, "Install for Admin only", folder sharing). No CLI/API route stated.
- Verification: Marketing App > Analytics tab shows Email/SMS/Landing Pages & Forms/Flow Engagement reports; each package shows an installed state in Setup > Analytics.
- Maps to setup checks: S18 (primary how-to and package list), S8 (explicit prerequisite: Marketing Data Kits deployed), S19 (Share Access to Analytics Folders is a distinct, required step named in this article), S5/S6 ("Marketing Cloud Manager" permission needed to edit/share reports and dashboards, per this article's "How to manage Analytics Access" section).

### Understanding the different type of Reports in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/analytics-configuration/understanding-the-different-type-of-reports-in-marketing-cloud-next/
- Purpose: catalog what reports/dashboards exist once Data Kits + Analytics packages are installed, and where to find them.
- Prerequisites and order dependencies: explicitly requires the Marketing Data Kits and "different Packages" (i.e. the S18 packages from the sibling article) to already be installed.
- Steps (navigation only, no configuration actions):
  1. Marketing App > Analytics tab for most dashboards/reports.
  2. Campaign-level reports live on the Campaign record itself: Marketing Performance tab > campaign record > "Campaign Performance dashboard (Insights)" (CTR, Sends, Open Rate, Delivery Rate, Click Rate, Bounce Rate, Opt-Out Rate; filterable by date range, Campaign Flow, Segment) and "Campaign Performance dashboard (Deliverability)" (Delivery Rate, Sends, Bounce Rate, Deliveries, Failed to Send, Bounces, Hard/Soft Bounced, Opt-Out Rate).
  3. Flow Builder: on a Send Email Message element, an Analytics tab shows run counts by status (Completed, Error, Waiting, Retrying) and Average Duration.
  4. Analytics tab dashboards/reports: Email Engagement (dashboard + reports), SMS Engagement (dashboard + report), Forms Engagement (report + dashboard), Landing Page Engagement (report + dashboard).
- Limits and numbers: none given.
- Gotchas: these dashboards/reports "are relying on the D360 (Data Cloud) Report feature" — i.e. Marketing Cloud Next reporting is built on Data Cloud reports, so they can be customized like any Data Cloud report (explicitly stated).
- Automation route: UI-only for viewing; article states the underlying reports can be customized (Data Cloud report builder, still UI). No SOQL/REST route given for reading these dashboards.
- Verification: presence of the named dashboards/reports under the Analytics tab and on Campaign records is itself the verification that S18 packages installed correctly.
- Maps to setup checks: S18 (confirms these reports are the payoff of package installation and are Data Cloud-report-based), S19 (folder sharing needed for team visibility into these, inferred from prior article).

### How to create a Segment in Marketing Cloud Next
Source: https://arthurbackouche.com/docs/marketing-cloud-next/segments-configuration/how-to-create-a-segment-in-marketing-cloud-next/
- Purpose: step-by-step for building and publishing a segment for use in Campaign Flows and ad activation targets.
- Prerequisites and order dependencies: article states "Marketing Cloud Next... sits on top of Data Cloud" and segmentation relies on Data Cloud segmentation; implies DMOs (Unified Individual, Contact Point Email/Address) must exist. Publishing makes the segment usable in a Campaign Flow (Email send) and/or an Activation Target (Facebook Ads, Google Ads) — i.e. this is what S14 (segment-triggered flows) depends on.
- Steps:
  1. Marketing App > "Segments" tab > New.
  2. Choose creation method: Visual Builder (most common, used in the walkthrough), Create with Einstein Segment Creation (natural-language segment creation — article warns to double-check setup and results), or Install from Data Kits (pre-built segment from a Data Kit).
  3. Choose segment type: Standard Segment (used in walkthrough — pick a DMO such as Unified Individual plus related DMOs and rule conditions), Waterfall Segment (ordered sub-segments; an individual belongs to only the first-matching sub-segment by priority), Real-Time Segment (populated from a Real-Time Data Graph, for use in Triggered Campaign Flows), Dynamic Segment (combines static conditions with dynamic conditions evaluated at send time).
  4. Segment Properties: Data Space (default), Segment Name, "Segment On" = the DMO used for segmentation (e.g. Unified Individual), Description.
  5. Choose Publish Type: Standard Publish (looks back 2 years of engagement data; usable in any activation target) or Rapid Publish (looks back only 7 days of engagement data; refreshes more frequently).
  6. Choose Publish Schedule (Hourly/Daily/Weekly/Monthly) and Lookback Window (how far back, in days/weeks/months, to pull data).
  7. Define Segment Criteria in the visual builder: left column shows Direct Attributes (fields on the selected DMO) and Related Attributes (fields on connected DMOs). Example: Unified Individual with an existing Email Address (via Contact Point Email) AND living in Sydney (via Contact Point Address).
  8. Click Save, then Done. Segment Status becomes "Active" after a few seconds.
  9. Click Publish so the segment is available to a Campaign Flow and/or Activation Target.
- Limits and numbers: Standard Publish look-back = 2 years of engagement data; Rapid Publish look-back = 7 days. Example population in the walkthrough = 5,600 people (illustrative, not a system limit).
- Gotchas: Real-Time Segments require a Real-Time Data Graph specifically (not the standard Data Graph) — relevant if the org's personalization graph is Standard only. Einstein Segment Creation (natural language) is flagged by the author as needing extra verification of results. A segment must be both Saved/Active and separately Published before it can be used downstream — two distinct states.
- Automation route: UI-only throughout (Segments tab, New wizard, visual criteria builder, Publish). No REST/SOQL alternative given ("Install from Data Kits" is the closest to an automatable/packaged route, but it is still a UI action).
- Verification: Segment Status shows "Active" after save; Population count displays in the builder; after Publish, the segment appears as selectable in Campaign Flow entry criteria and in Activation Target configuration.
- Maps to setup checks: S14 (segment-triggered flow process type — this is the segment side of that pairing), S11 (Real-Time Segment type explicitly requires a Real-Time Data Graph, distinct from the Standard graph used for personalization/email merge fields), S9 (Data Space selection during segment creation), S21 (custom DMOs like custom objects (e.g. subscription or credit records) would appear as Related Attributes here once added to Unified Individual, inferred).

### Understanding Data Graphs in Agentforce Marketing
Source: https://arthurbackouche.com/understanding-data-graphs-in-agentforce-marketing/
- Purpose: conceptual deep-dive on why Data Graphs enable real-time personalization, and the difference between Standard and Real-Time Data Graphs.
- Prerequisites and order dependencies: conceptual article; no step-by-step setup, but confirms Data Graphs underpin Merge Fields, Real-Time Segments, and Identity Resolution use cases across Agentforce Marketing (= Marketing Cloud Next).
- Steps: none (conceptual/explainer article), but it does describe the "Anatomy of a Data Graph Configuration": a Data Graph = one Primary DMO from the Customer 360 Data Model (usually Unified Individual) + Related DMOs (e.g. email, phone, contact info) + selected fields on each.
- Limits and numbers / refresh:
  - Standard Data Graph: refreshed "every few seconds" — described as "near-real-time"; used for Marketing Journeys and analytics.
  - Real-Time Data Graph: refreshed "every few milliseconds"; reserved for real-time experiences such as an AI agent voice conversation.
  - No field-count cap or per-graph object limit stated anywhere in this article.
- Gotchas / contradiction to flag: this article's refresh cadence for the Standard Data Graph ("every few seconds") does not match the "How to use Data Graph" and "Understanding Data Graph" articles, which describe a configurable Save-and-Build refresh schedule from every 30 minutes to once a month. See cross-cutting findings below.
- Automation route: UI-only implied (no APIs mentioned); article is purely explanatory, no clickpath given for building a Real-Time Data Graph specifically.
- Verification: not applicable (no build steps given); conceptually, real-time personalization use cases only work correctly if the Real-Time Data Graph variant is selected, not the Standard one.
- Maps to setup checks: S11 (Standard vs Real-Time Data Graph distinction, and confirmation that Merge Fields, Real-Time Segments and Identity Resolution all read from Data Graphs).

## Batch D cross-cutting findings

1. **Data Graph field-count cap: not found in this batch.** None of the 12 articles states a numeric field limit (e.g. 200 fields) for a Data Graph, nor a documented process for removing duplicate fields between Unified Individual and Individual. The the target org constraint (the org's Unified Individual graph near the 200-field cap, 32 duplicated fields to remove) is not addressed by any arthurbackouche.com article in batch D. This must be sourced elsewhere (Salesforce Help "Data Graph limits" pages linked as resources, not fetched here) or confirmed directly in the org. Flag as **unknown / needs Salesforce Help lookup**, not inferred from KB.
2. **Editing an existing Data Graph vs rebuilding is confirmed as supported and the normal path.** Both Einstein Engagement Frequency and Einstein Engagement Scoring articles explicitly edit a previously-built Data Graph to add a new related DMO and fields, rather than rebuilding from scratch. This directly supports the the target org plan of editing the org's Unified Individual graph (add a custom subscription object, a custom credit object; remove 32 duplicate fields) rather than rebuilding it. No article describes a field-removal flow specifically, only field-addition; removing fields from an existing graph is not documented here (unknown from this batch).
3. **Refresh schedule: contradiction between articles.** "How to use Data Graph" and "Understanding Data Graph in Marketing Cloud Next" both say the Save-and-Build refresh schedule is user-selectable from every 30 minutes up to once a month, and that more frequent refresh consumes more Data Cloud credits (tracked via Digital Wallet). "Understanding Data Graphs in Agentforce Marketing" instead describes the Standard Data Graph as refreshing automatically "every few seconds" (near-real-time) with no user schedule, and a separate Real-Time Data Graph refreshing "every few milliseconds". These two descriptions of "Standard" refresh behavior do not reconcile: one implies a manually configured batch schedule (30 min-1 month), the other implies continuous near-real-time refresh. Recommend treating the 30-min-to-1-month schedule as the operative one for the graph editor UI in this org (matches direct how-to steps with a UI screenshot reference), and the "few seconds" claim as a higher-level marketing description possibly referring to a different/newer graph refresh mode. Mark this contradiction explicitly to the client rather than picking one silently.
4. **Which Data Graph personalization uses:** Salesforce Personalization (web/product personalization) states as a hard prerequisite "Create a Salesforce DataGraph" but does not name which one to select at setup time — it is deployed against whichever data space's Foundation Data you deploy. Email/Flow personalization (merge fields, Einstein Decision elements) explicitly uses the graph selected in Assistant Home > Customer Engagement > "Configure Basic Personalization" (example given: "Data Graph: Unified Individual"), built with Primary DMO = Unified Individual. Real-Time Segments require a distinct Real-Time Data Graph, not the Standard one used for email personalization. For the target org, this means: the org's Unified Individual graph (Standard graph, Primary = Unified Individual) is very likely the one selected in "Configure Basic Personalization" and used by email merge fields and Einstein Decision elements; confirm this selection directly in Setup rather than assuming (inferred).
5. **Non-UI route for Data Graphs: none found.** All four Data Graph-related articles (How to use, Understanding, Agentforce blog, and the two Einstein articles that edit a graph) describe only UI steps (Setup > Data Graphs list view > New/Edit > Save and Build). No REST, Metadata API, or Tooling API path is mentioned anywhere in this batch. This is consistent with the skill's own note that `d360_metadata` is guard-blocked; treat Data Graph editing as **UI-only** per this KB, with no invented API route.
6. **S18 package naming ambiguity: not resolved by this batch.** "How to install Analytics Packages" names exactly four packages to install under Setup > Analytics (Reporting and Optimization): Marketing Engagement Analytics, SMS Analytics, Landing Pages and Forms Analytics, and Flow Reports Analytics. Neither this article nor "Understanding the different type of Reports" uses the terms "CRM Analytics" or "Marketing Performance Intelligence" anywhere. The reports themselves are stated to run "on the D360 (Data Cloud) Report feature." This batch does not confirm whether "CRM Analytics" and "Marketing Performance Intelligence" are alternate/legacy names for these same four packages, a superset, or a different product entirely — flag as **unknown**, needs a direct check in the a live org Setup > Analytics page or a Salesforce Help lookup, not an assumption.
7. **Consistent identity-resolution dependency across Einstein features.** Einstein STO explicitly requires an Identity Resolution Ruleset on the Individual DMO plus an existing Data Graph before enabling. Einstein Engagement Frequency and Scoring require an existing Data Graph to add their DMOs to (no explicit Identity Resolution requirement stated, but implied via the DMO's origin). Einstein Metrics Guard has no stated prerequisite at all — it is a standalone toggle. This means S10 (identity resolution) and S11 (Data Graph) block S17's STO sub-feature specifically, while Metrics Guard can be enabled independently of S10/S11.
8. **Analytics install path is two-stage and spans two different Setup areas.** Marketing Data Kits (S8) are installed via Assistant Home > "Set Up Marketing Performance" > "Go To Marketing Data", but the actual analytics packages (S18) are installed from a separate Setup menu item, "Analytics" under "Reporting and Optimization" — not from the Marketing Performance page itself. Folder sharing (S19, "Share Access to Analytics Folders") is called out as a separate required step, not automatic after package install.

## Files not readable in this batch
None. All 12 target files were read successfully.
