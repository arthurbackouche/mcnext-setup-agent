# Contradictions

Every contradiction found between arthurbackouche.com articles, and between articles and [FIELD] facts observed in a live org. **[FIELD] wins unless the target org shows otherwise** in every case below.

## 1. Data Graph refresh cadence

- **Article A** ("How to use Data Graph in Marketing Cloud Next", "Understanding Data Graph in Marketing Cloud Next"): the Save-and-Build refresh schedule is user-selectable, **30 minutes to once a month**; more frequent refresh consumes more Data Cloud credits (tracked via Digital Wallet). [AB:data-graph-use-mcn] [AB:data-graph-understand-mcn]
- **Article B** ("Understanding Data Graphs in Agentforce Marketing"): the Standard Data Graph refreshes automatically "every few seconds" (near-real-time), with a separate Real-Time Data Graph at "every few milliseconds" — no user-configured schedule mentioned. [AB:data-graphs-agentforce]
- **Resolution:** treat the 30-minute-to-1-month schedule as operative for the graph editor UI (matches direct how-to steps with screenshots); treat "every few seconds" as a higher-level marketing description, possibly describing a different/newer refresh mode not yet seen in this org. Confirm directly in a live org's Data Graph editor what refresh options are actually offered before reporting a number to the client.

## 2. Segment activation-to-MCE timing

- **Party Identification article**: activating a Data 360 segment into MCE "can take up to 30 min". [AB:party-id-d360]
- **Dedicated Activation article**: "it can take up to 24 Hours when initiating the process." [AB:activate-segment-d360]
- **Resolution:** treat 24 hours as the safer planning number, since it comes from the article dedicated to that exact procedure; flag the 30-minute figure as unreliable.

## 3. Unified Individual DMO naming

- **Setup skill's own S10 check text** (pre-existing in this project, not from these notes) implicitly assumes a name like `ssot__UnifiedIndividual__dlm`.
- **Identity Resolution article**: one implementation produced `UnifiedssotIndividual888__dlm` — a generated, org-specific, non-standard name. [AB:identity-resolution-mcn]
- **[FIELD] a live org**: the DMO is `UnifiedssotIndividual<ruleset id>__dlm`, hidden in the DMO catalogue UI, confirming the pattern `UnifiedssotIndividual<ruleset id>__dlm`.
- **Resolution: [FIELD] wins.** Never hardcode a DMO name for Unified Individual. Always read it from Basic Settings or the ruleset's own output.

## 4. Identity Resolution ruleset auto-generation availability

- **Configure MC Next article**: implies Basic Settings simply has a "Generate Ruleset" button producing a default email-match ruleset. [AB:configure-mcn]
- **Identity Resolution article**: states auto-generation was **not available** in that org — the ruleset had to be built manually end-to-end, including a Lead-to-Contact match rule. [AB:identity-resolution-mcn]
- **[FIELD] a live org**: Basic Settings **did** offer "Generate Ruleset" and it was used successfully.
- **Resolution: [FIELD] wins unless the target org shows otherwise** — auto-generation was available in this org. Do not assume either path in general; check what the specific org's Basic Settings page offers before planning.

## 5. Marketing Data Kits: 5-kit list vs 7+-kit list

- **"How to set-up Marketing Cloud Next"**: lists Basic Settings Data Kits as 5 (Sales, Marketing Setup Objects, Consent Objects, Flows Integration, Email Channel). [AB:setup-mcn]
- **"How to use Data Kits in Marketing Cloud Next"**: lists 7 (adds SMS Channel and WhatsApp Channel), plus a separate External Tracking Data Kit named in a different article. [AB:data-kits-mcn] [AB:external-sites-mcn]
- **Resolution:** not a true contradiction — the first article covers only what's inside the Basic Settings wizard; the second covers the full data-kit catalogue including channel-specific kits added afterward. Confirms S8 should check for SMS Channel and External Tracking kit DMOs too, given the client' stated SMS usage.
- **[FIELD] a live org**: has a single "Update" button covering all 8 data kits at once, not a per-kit install flow as the articles' step-by-step screenshots imply. **[FIELD] wins unless the target org shows otherwise's actual install mechanism.**

## 6. Permission set naming: Data Cloud Admin vs Data Cloud Architect

- **"How to set-up Data Cloud for Marketing Cloud Next"**: explicitly states the name depends on org age/release — "Data Cloud Admin" (older) vs "Data Cloud Architect" (current/Salesforce-recommended name). [AB:setup-datacloud-mcn]
- **Resolution:** not a contradiction between articles (both describe the same rename), but a real risk for any automated PermissionSet search — always search both labels. No article resolves whether both the Data Cloud family and the Marketing Cloud family (Admin/Manager) are needed simultaneously for a given task, or just one.

## 7. Terminology: "Marketing Cloud Growth" vs "Marketing Cloud Next" vs "Marketing Cloud Advanced"

- The consent-bridge article calls the target platform "Marketing Cloud Growth" [AB:consent-mce-bridge-mcn]; the email-templates/merge-fields article says the test recipient must be opted-in "in Marketing Cloud Advanced" [AB:merge-fields-mcn]; every other article in the corpus says "Marketing Cloud Next".
- **Resolution:** read as the same underlying platform referenced with different edition/marketing names by the source site across its publishing history; no functional difference described anywhere. Flag as terminology drift, not a functional contradiction.

## 8. Analytics package naming: 4 named packages vs "CRM Analytics" / "Marketing Performance Intelligence"

- **"How to install Analytics Packages" and "Understanding the different type of Reports"**: name exactly 4 packages (Marketing Engagement Analytics, SMS Analytics, Landing Pages and Forms Analytics, Flow Reports Analytics) and never use the terms "CRM Analytics" or "Marketing Performance Intelligence". [AB:analytics-packages-mcn] [AB:reports-types-mcn]
- **Resolution: unresolved by this KB.** Not confirmed as a contradiction (could be a superset or a different product) — flagged as **unknown**, needs a direct check in a live org Setup > Analytics or a Salesforce Help lookup. See `90_open_items_a live org.md` S18.

## 9. Cause of the `d360_metadata` / `d360_datagraph_metadata` guard block

- **Two independent arthurbackouche.com articles** (multi-agent orchestration blog, MCE-to-Data-360 Claude mapping article) both suggest that a Salesforce Setup > MCP Servers > Salesforce Servers > **`data-cloud-queries`** toggle must be enabled for `d360_metadata`-style calls made via a Salesforce-hosted MCP server to work — implying an org-side cause for any block on these calls. [AB:multi-agent-orchestration] [AB:claude-mapping-mcn]
- **[FIELD] fact**: the block on `d360_metadata` and `d360_datagraph_metadata` in this project is caused by **this project's own guard hook** (tool name has no read verb), **not** by any org toggle.
- **Resolution: [FIELD] wins as the actual cause for this project.** The `data-cloud-queries` MCP Servers toggle is recorded as a **separate, unverified org-side prerequisite for hosted MCP access generally** — not as an alternative explanation for our specific guard block. Do not conflate the two when reporting to the client or updating the skill.

## 10. Batch A cross-cutting note on missing S12/S13/S14 coverage

- Batch A itself flags that none of its 9 articles mention the MCE (Engagement)/ExactTarget connector by name, and that its closest analogy (Account Engagement/Pardot migration) is a different product and a different Data Cloud bundle. This is a scope gap the batch calls out, not a contradiction between sources — resolved by batch C's dedicated MCE connector article, which does cover S12 directly. Included here for completeness since batch A explicitly flags it as unresolved within its own scope.

## Not contradictions (checked, found consistent)

- Batch E states explicitly: "Contradictions between articles: none found" for its own 15 flows/sites/agents/migration articles — the sequencing (Data 360 → identity resolution → Data Graph → Flow/personalisation) is consistent across all of them and with the 60-day plan article.
- Ingestion-frequency figures across different connector types (15 min to Weekly for Snowflake, Daily for WordPress, 24 hours for Calculated Insight refresh) are per-source examples, not conflicting platform limits.
