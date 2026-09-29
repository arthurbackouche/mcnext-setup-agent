# Knowledge base index

Source: 58 arthurbackouche.com articles (research/arthurbackouche/notes/batch_A.md to batch_E.md, ~25,000 words of notes) plus [FIELD] facts observed directly in live implementations. A second source (Medium @marketingcloudtips) will be merged into these same files later — every fact below is already tagged `[AB:<slug>]` or `[FIELD]` so that merge can add `[MED:<slug>]` facts alongside without rewriting this pass.


## What each file covers

- `01_setup_order.md` — one canonical end-to-end order for MC Next foundation setup, licences to first test send, in 13 phases with dependencies and timings, plus a disagreements summary.
- `10_permissions_users.md` — S2, S5, S6. Data Cloud Architect/Admin, Marketing Cloud Admin/Manager, custom permission sets, assignment.
- `11_data360_enablement_basic_settings.md` — S3, S7, S9. Data 360 instance enablement, Basic Settings "Enable Data Cloud" 6-item checklist, data space selection guidance.
- `12_data_kits.md` — S8. Marketing Data Kits catalogue (Sales, Marketing Setup Objects, Consent Objects, Flows Integration, Email/SMS/WhatsApp Channel, External Tracking), Standard Data Bundles for other products.
- `13_crm_connector_streams_mapping.md` — S4, S21. Salesforce CRM connector, Sales Bundle vs individual objects, DLO-to-DMO mapping mechanism, Ingestion API and generic REST connector routes.
- `14_mce_connector.md` — S12. MCE connector wizard, Party Identification/Subscriber Key unification, segment activation into MCE, MCE-to-MC-Next consent bridge, MCE MCP auth traps.
- `15_identity_resolution.md` — S10. Ruleset creation, match rules, Consolidation Rate, Unified Individual DMO naming.
- `16_data_graph.md` — S11. Data Graph build/edit steps, Standard vs Real-Time, refresh/credit model, field-cap gap, personalization graph selection.
- `17_email_channel_domains.md` — S13. Authenticated Domains, From Addresses, Reply Mail Management, Tracking Domain (ZeroSSL).
- `18_consent.md` — S15, S16. Physical address, consent validation, subscriptions, consent import, MessagingConsent Flow, MCE consent bridge, MCE-vs-Next consent semantics.
- `19_einstein.md` — S17. Metrics Guard, Send Time Optimization, Engagement Frequency, Engagement Scoring — prerequisites, minimums, Advanced Edition notes.
- `20_analytics.md` — S18, S19. Analytics packages, folder sharing, report catalogue, AppExchange MCE reporting package.
- `21_flows_and_sends.md` — S14. Single Email Flow (first test send), Segment Triggered Flow, On-Demand Flow REST trigger.
- `22_personalization_segments_sites.md` — S20. Customer Engagement Scoring, Salesforce Personalization, Segments, landing pages, external site tracking, form handlers, page-customization LWC widgets.
- `23_migration_considerations.md` — cross-cutting. 60-day plan, Account Engagement (Pardot) analogy, Claude-assisted MCE-to-Data-360 mapping, AMPscript/template migration, Agentforce agents (out of scope note).
- Open items for a specific org are not kept here. They live in the engagement folder at `out/setup/open_items.md`.
- `91_contradictions.md` — every contradiction between articles, and between articles and [FIELD] facts. [FIELD] wins unless the target org shows otherwise.

## Check coverage table

| Check | KB file#section | One-line answer | Confidence |
|---|---|---|---|
| S1 | (not covered — generic org/sandbox check) | Use skill Part 1 CLI check (`sf org display`, `Organization` SOQL); not in this KB corpus | unknown |
| S2 | 10#Steps | Look for Data Cloud Architect/Admin and Marketing Cloud Admin/Manager PermissionSetLicense rows; exact licence labels not enumerated by any article | inferred |
| S3 | 11#Steps | Setup > Data Cloud Setup > Get Started enables the instance; automatic sub-steps, no fixed timing given | documented |
| S4 | 13#Steps | Salesforce CRM connector via Sales Bundle or "Objects individually" for custom objects; stream lands as DLO, needs a DLO-to-DMO mapping step | documented |
| S5 | 10#Steps | Data Cloud Architect/Admin + Marketing Cloud Admin/Manager permission sets; naming varies by org vintage, search both families | documented |
| S6 | 10#Verification | `PermissionSetAssignment` query for the running user against both permission set families | documented |
| S7 | 11#Steps | Basic Settings 6-item "Enable Data Cloud" checklist, ending in "Enable Marketing Cloud" | documented |
| S8 | 12#Steps | Marketing Data Kits catalogue confirmed (Sales, Marketing Setup Objects, Consent Objects, Flows Integration, Email/SMS/WhatsApp Channel, External Tracking); [FIELD] a live org installs all via one "Update" button, not per-kit | documented |
| S9 | 11#Data space guidance | Recommend 1:1 Data Space per MCE Business Unit, start narrow — mapping is effectively permanent | documented |
| S10 | 15#Steps | Ruleset on Individual DMO (Normalised Email / Fuzzy Name / Lead-to-Contact / MC Subscriber Key rules); Unified Individual DMO name is org-specific, never hardcode | documented |
| S11 | 16#Steps, #Limits | Data Graph on Unified Individual, editable to add DMOs; field-count cap NOT documented by any article — [FIELD] a live org: 50/object, 200/graph | inferred (field cap: unknown in public KB, documented via [FIELD]) |
| S12 | 14#Steps | 4-stage wizard (Enter Credentials > Data Source Set-up > Allow Profile BU Mapping > Select BUs to Activate), then separate Data Stream creation; login window is always a stop-and-handback point | documented |
| S13 | 17#Steps | Authenticated Domain (subdomain, up to 72h DNS validation) > From Addresses > Reply Mail Management > optional Tracking Domain | documented |
| S14 | 21#Steps | Segment Triggered Flow and On-Demand Flow both confirmed as selectable flow types; minimum first-send path needs no Data Graph/identity resolution | documented |
| S15 | 18#Gotchas, 90#S15 | "Add Data Protection Details to Records" named as a Basic Settings checklist item; **no article explains what it actually configures** | unknown |
| S16 | 18#Steps | Physical address, consent validation, subscriptions, consent import (mandatory — all Individuals start Opted Out) | documented |
| S17 | 19#Steps | 4 Einstein toggles; Metrics Guard standalone, Frequency/Scoring need an existing Data Graph, STO needs identity resolution + Data Graph | documented |
| S18 | 20#Steps, 91#8 | 4 named analytics packages (Marketing Engagement, SMS, Landing Pages and Forms, Flow Reports); "CRM Analytics"/"Marketing Performance Intelligence" naming unresolved | inferred (package list documented; naming question unknown) |
| S19 | 20#Steps | "Share Access to Analytics Folders" is a distinct required step after package install; needs Marketing Cloud Manager to manage | documented |
| S20 | 22#Steps | 3 named LWC widgets (Privacy Consent Status, Data 360 Profile Engagement, Data 360 Profile Insights) for Contact/Lead/Prospect/Campaign layouts | documented |
| S21 | 13#Steps (DLO-to-DMO mapping) | Only one article (Snowflake, not CRM-specific) confirms the Data Mapping > Start mechanism for mapping a custom DLO to a DMO; [FIELD] confirms custom-object DMOs mapped this way in a live org | documented (via analogy) |

Confidence key: **documented** = a KB article or [FIELD] fact states this directly. **inferred** = KB gives strong supporting evidence but not a direct statement, or [FIELD] fills a gap the public KB leaves open. **unknown** = no article and no [FIELD] fact addresses it; flagged for direct investigation.

## Coverage summary

- Documented: 16 of 21 checks (S2–S14, S16, S17, S19, S20, S21 — several with an "inferred" qualifier noted above).
- Inferred (partial gap, filled by [FIELD] or strong indirect evidence): S2, S11, S18, S21.
- Unknown: S1 (out of KB scope by design), S15 (genuine documentation gap across the whole 58-article corpus).
