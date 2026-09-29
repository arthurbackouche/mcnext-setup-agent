# Platform notes

Generic behaviours learned on live MCE → MC Next engagements. Agents read `CLAUDE.md` (short list) and the skill references; this page is the longer record. Add lessons in generic form only: no client names, org aliases, hosts, ids or counts.

## Marketing Cloud Engagement (MCE) and discovery
- MCE MCP page size 25 to 50; larger pages cause out-of-memory errors. The interactions list returns `count` on page 1.
- Published is not active. Use `activity.lastContactProcessed`.
- Journey payloads come back inline. Save them verbatim or use the slim schema.
- Estates often clone journeys per promo code or per month (`<Stage>_<Month>_SprintN_<Year>`). Older names can alias current stages. Treat these as consolidation families.
- Classic Email Studio emails can be missing from the Content Builder API; they need a UI check.
- Content risk often sits in SMS: AttributeValue in most SMS, and LookupRows needs data prepared upstream.
- `parse_journeys.py` `entry_source()` checks the loyalty regex against the journey key, not the event source, so API-event entries can come out Unknown. Fix before deep-translating those journeys.
- Specialist counts can be off: recount from the artefact. Extrapolated consolidation families carry `read_via_get_journey: false`.
- Parallel specialists can both write the manifest. Check both sections after they return.

## Salesforce, Data 360 and MC Next
- Connect API and Metadata: GET a UI-built object first and use it as the template. Documented field names are not reliable.
- The Salesforce `sobject-all` MCP has no Tooling or Metadata API. Flows deploy through the `sf` CLI only.
- MC Connect creates `JBSystem_<Object>_RecordFlow` and `JBSystemFlow_<Object>` for Salesforce-entry journeys. Deactivate a pair only when every journey on that object is live in MC Next.
- MC Next Decisions read the Unified Individual Data Graph. Journey Data (`Event.*`) has no direct equivalent.
- The Unified Individual DMO is `UnifiedssotIndividual<ruleset id>__dlm` and is hidden in the DMO catalogue UI. Probe by pattern with `d360_query_sql`.
- No Unified Individual DMO means identity resolution hasn't run, so no Data Graph can exist yet.
- `d360_data_graph_get` needs the graph API name, not the display name.
- `d360_datakit_list` can fail with "bundle is null". Check kits by testing whether their DMOs exist.
- Data Graph limits seen live: 50 fields per object, 200 per graph. The Party join key on Individual cannot be removed.
- Data Graph edits: the page opened by clicking a graph name is read-only. Edit through the row menu > Edit, then Save and Build. The build applies on the graph's refresh schedule, so poll before calling it done.
- Basic Settings has a single "Update" button for all data kits. One CommSubscription record means Marketing Cloud was enabled.
- MC Next creates every Individual opted out. Sends need a consent import or a `MessagingConsent` flow.
- CRM streams land as DLO only. A custom object needs a DLO-to-DMO mapping before a graph can use it.
- A new sandbox often has no `sf` alias. Build deploys need `sf org login` first.

## Claude Code tooling
- Connector tool lists bind at session start. After fixing auth, restart the session.
- MCP connectors also stay bound to the org they authenticated to at session start. On a new engagement, prove which org an MCP connector reads (compare with `sf` SOQL on the target alias) before trusting it; otherwise verify with `sf data query` and Chrome only.
- `/goal` works in `claude -p`, including multi-line prompts.
- The guard fires under `--permission-mode auto` in `claude -p`.
- The auto-mode classifier can fail for minutes ("no verdict"). Retry once, then move on.
- Only one Chrome agent at a time: parallel agents share a tab group and close each other's tabs.
- Specialists stall (about 600 s without output) on long multi-step tasks. Delegate one or two steps and log after each action. Partial writes survive a stall.
- macOS has no `timeout` command.

## Research sources
- arthurbackouche.com docs fetch with plain HTTP; the sitemap index lists `docs-sitemap.xml`.
- Medium: RSS returns only the last 10 posts and the GraphQL API sits behind Cloudflare. Chrome `read_page` after a full infinite scroll captures a whole author feed; a reader proxy fetches most articles (check for Cloudflare challenge pages, not just HTTP 200).
