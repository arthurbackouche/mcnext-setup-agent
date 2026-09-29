---
name: journey-to-flow-translator
description: >
  Migrate Marketing Cloud Engagement Journey Builder journeys to Marketing Cloud Next Flows end to end:
  triage the estate (retire / consolidate / migrate), translate each journey into a build spec, generate
  Flow metadata from org-captured templates, deploy as Draft via the Salesforce CLI, verify parity against
  the source journey, and produce a human-gated cutover runbook (drain window, re-entry guard seeding,
  MC Connect JBSystem flow decommission). Falls back to a Claude in Chrome build prompt.
  Use this skill whenever the user asks to migrate, rebuild, convert, map, assess or scope journeys,
  Journey Builder, JB, multi-step journeys or customer journeys for MC Next / Marketing Cloud Next /
  Growth or Advanced edition / Flow Builder, including phrasings like "which journeys can we move",
  "rebuild this journey in Next", "journey inventory", "journey migration plan", or "translate the
  welcome journey". Trigger even for a single named journey. Requires the Marketing Cloud Engagement
  MCP connector (sfmc_* tools).
---

# Journey Builder → MC Next Flow translator

Read-only against MCE. Deploys flows to MC Next as **Draft only**. Never publishes, pauses or stops an MCE journey or automation, and never activates a flow, unless the user explicitly instructs that specific action in the conversation.

Two modes:
- **Translate** (Steps 0 to 8): specs, prompts, register. No org writes.
- **Migrate** (Steps 9 to 12): build, deploy Draft, verify parity, cutover runbook.

## Outputs

| File | Audience | Purpose |
|---|---|---|
| `register.csv` | Delivery lead | One row per journey: disposition, verdict, target flow type, re-entry, idle days, family |
| `estate_summary.md` | Client / SA | Retire, consolidate, migrate story plus systemic flags |
| `specs/<journey>.md` | Builder | Entry, re-entry pattern, Mermaid target flow, element table, Data Graph attributes, dependencies, flags |
| `prompts/<journey>.md` | Claude in Chrome | Step-by-step Flow Builder build prompt with validation checks |
| `manifest_fragment.json` | Migration agent | `journeys` block for the shared migration manifest |
| `force-app/.../<Flow>.flow-meta.xml` | Salesforce CLI | Generated Draft flow per journey |
| `build_report.json`, parity reports | Delivery lead | What generated, what blocked and why, parity result from the org |
| `cutover/<journey>.md`, `cutover/jbsystem_decommission.md` | Go-live | Gates, guard seeding, sequence, rollback, JBSystem flow retirement |

Verdicts: **A** direct rebuild, **B** adapt, **C** re-architect. Dispositions: **Retire**, **Consolidate**, **Migrate**.

## Step 0: Inputs

Confirm, without over-asking:
- Client name (printed in headers).
- Edition: Growth or Advanced. Path Experiment is Advanced only.
- Dormancy window. Default 180 days since `lastContactProcessed`.
- Scope: whole estate, a folder, or named journeys. A single named journey skips to Step 3.

## Step 1: Refresh the platform baseline

Read `references/mcnext_flow_constraints.md`. Anything tagged **[verify]** stays a flag in outputs, never a stated fact. If the file is older than one release, web-search "Marketing Cloud Next Flow" release notes and update `scripts/mapping_rules.json` (entry, activities, flags) before running.

## Step 2: Tier 1 triage (whole estate)

Page the list endpoint:

```
sfmc_rest_get  path=/interaction/v1/interactions  query_params={"$pageSize": 50, "$page": N, "status": "Published"}
```

Rules learned on live tenants:
- Page size 50 max. First page returns `count`.
- Published ≠ active. `activity.lastContactProcessed` is the truth. Missing = never ran.
- Also pull `status=Paused` if the client wants paused journeys assessed.
- Responses usually come back inline. Save each page to `<workdir>/list_pN.json`. If a page is too large to save verbatim, save only: `id, key, name, version, status, entryMode, defaults.email, exits[].metaData.criteriaDescription, goals, activity.lastContactProcessed`. The entry source is inferred from `defaults.email`.

Run triage only:

```bash
python3 scripts/parse_journeys.py --list <workdir>/list_*.json --out <outdir> --as-of YYYY-MM-DD
```

Read `summary.json`. Report retire / consolidate / migrate counts before spending effort on deep translation.

## Step 3: Pick the deep-translation set

- Skip Retire.
- For each consolidation family or series, translate **one** representative (the most recent live version). The structural signature confirms the rest are twins.
- Translate every Migrate journey, or the subset the user names.

## Step 4: Fetch full journeys

```
sfmc_get_journey  id=<id>  extras=activities
```

Save each to `<workdir>/journeys/<slug>.json`, verbatim where possible. If inline and too large, use the slim schema in `references/slim_schema.md`. Keep every activity, including trailing 1-minute waits, and keep criteria XML verbatim. The parser depends on both.

Journeys reference only Content Builder assets and one event definition. If the user wants dependency depth, resolve `emailId` with `sfmc_get_content_builder_asset` and the trigger's `eventDefinitionKey` with the event definition getter. Otherwise leave IDs as-is.

## Step 5: Translate

```bash
python3 scripts/parse_journeys.py --list <workdir>/list_*.json --workdir <workdir>/journeys --out <outdir> --as-of YYYY-MM-DD
python3 scripts/render_specs.py --out <outdir> --client "<Client>" --edition advanced|growth
```

What the parser does:
- Finds the root (the activity no outcome points to) and walks the graph. JB returns activities unordered.
- Drops trailing waits with no `next` (JB path terminators). Flags ≤5-minute mid-path waits as spacers.
- Parses decision XML into readable conditions. Separates entry data (`Event.*`) from Contact Builder attributes. Flags cross-object references, whole-word lists and hard-coded ID lists.
- Maps entry source to flow type and entry mode to a re-entry guard pattern.
- Scores verdict from the worst element. Any cross-object reference forces **C**.
- Hashes structure to find twins.

Unknown activity types map to `_default` (re-architect). Add them to `mapping_rules.json` and rerun.

## Step 6: Find the story

Pull these from `summary.json` and the specs. They generalise across tenants:
1. **Retire share.** Usually large. Dormant and test journeys cost nothing to leave behind.
2. **Consolidation.** Series and families that collapse into one parameterised flow.
3. **The Data Graph is the real work.** Collect every Decision attribute across specs. That list is the Data Graph requirement. Entry-data attributes (`Event.*`) are the ones teams forget.
4. **Re-entry guards.** Count OnceAndDone / SingleEntryAcrossAllVersions. Recommend one standard guard pattern for all of them.
5. **Named re-architects.** Every **C** gets its cause in one line.

## Step 7: QA (mandatory)

Run `python3 scripts/qa_outputs.py --out <outdir>`. Fix and rerender until it exits 0. It checks:
- For each spec, element count in the prompt's validation block equals the non-dropped elements in the IR.
- Every Decision in the IR has a default outcome in the prompt.
- Mermaid blocks: every edge references a defined node; no quotes or brackets inside labels.
Then spot-check one translated journey against its source JSON by hand: root, branch labels, wait durations, end points.

## Step 8: Deliver

In Translate mode, copy `register.csv`, `estate_summary.md`, `specs/`, `prompts/` and `manifest_fragment.json` to the outputs directory and present them. Summarise in five lines: totals, retire count, consolidation wins, the Data Graph attribute count, and the named re-architects.

If a shared migration manifest exists, merge `manifest_fragment.json` into its `journeys` key. Do not overwrite other skills' keys.

## Step 9: Preflight gates (Migrate mode)

Build nothing until these resolve. Report gaps per journey.
- **Templates**: `templates/<org>/<trigger>/` exists and was captured from the target org. If not, run the bootstrap in `references/deploy_bootstrap.md`. Never deploy with the synthetic test templates.
- **Deploy path**: Salesforce CLI authenticated to the target org (`sf org display -o <alias>`). The MCP connectors cannot create flows. No CLI → fall back to the Chrome prompts.
- **Reference map**: `map.json` covers every email, SMS and Decision attribute in the spec. Confirm attributes against the Data Graph definition, content against the content migration register.
- **Entry**: target segment exists and is published, or the trigger object exists.
- **Re-architect items**: any **C** element with no template (custom activity, Einstein split, DE write) blocks generation. Build those by hand or redesign first.

Discover MC Connect trigger flows once per org through the MCP:
```sql
SELECT ApiName, IsActive FROM FlowDefinitionView WHERE ApiName LIKE 'JBSystem%'
```

## Step 10: Build and deploy as Draft

```bash
python3 scripts/build_flow_xml.py --ir <out>/ir/<journey>.json --templates templates/<org>/<trigger> --map map.json --project <sfdx>
sf project deploy start -d <sfdx>/force-app/main/default/flows/<Flow>.flow-meta.xml -o <alias> --dry-run
sf project deploy start -d <sfdx>/force-app/main/default/flows/<Flow>.flow-meta.xml -o <alias>
```

The builder resolves connectors through dropped terminator waits, omits spacer waits (`--keep-spacers` to keep), expands whole-word lists into OR groups, and writes cross-object compares as element references. Exit code 2 = something blocked; read `build_report.json`.

For consolidation families, build the representative once, then parameterise by segment. Do not generate one flow per twin.

## Step 11: Verify parity from the org

Retrieve what was deployed and compare it with the source IR. Never verify the local file.

```bash
sf project retrieve start -m "Flow:<Flow>" -o <alias> -r /tmp/verify
python3 scripts/verify_parity.py --ir <out>/ir/<journey>.json --flow <retrieved file>
```

Parity = same decisions, waits and sends, same decision outcomes by label, everything reachable from start, no dangling connectors, no unresolved references, status Draft, source journey id in the description. Then confirm through the MCP `FlowDefinitionView` query that it exists and `IsActive = false`. Update the manifest: status `deployed_draft`.

## Step 12: Cutover runbook

```bash
python3 scripts/cutover_runbook.py --out <out> --jbsystem-flows <comma list from Step 9 query>
```

Each runbook carries go-live gates, the drain window (longest wait path), re-entry guard seeding from `_JourneyActivity` for OnceAndDone / SingleEntryAcrossAllVersions, the stop-entry step per entry type, and rollback. `jbsystem_decommission.md` lists each MC Connect trigger flow pair and every live journey still depending on it. Deactivate a pair only when all its journeys are live in MC Next.

Present the runbooks. Execute production steps only one at a time, each on explicit instruction.

## Handoffs

- `emailId` / SMS asset lists → **ampscript-mcnext-audit** (content verdicts).
- Entry sources and decision attribute sources → **mce-to-data360-mapper** (DE to DMO, Data Graph).
- `publicationListId` → consent migration.

## Failure modes (Migrate)

- **Deploy error on processType / actionName**: templates came from another org or release. Re-bootstrap.
- **Deploy error on a Decision field reference**: map value is not a valid Data Graph path. Fix `map.json`, rebuild.
- **Parity fails after a successful deploy**: the platform rewrote something (common: defaults, element renames). Read the diff in the report; if behaviour is identical, record it in `platform-learnings` and adjust the parity rule, never the IR.

## Failure modes

- **List call returns fewer journeys than the UI**: the MCP token is scoped to one BU. Report the BU from `/platform/v1/tokenContext` and ask whether to run per BU.
- **Stale token after role changes**: refresh the connector.
- **Criteria XML truncated in a slim save**: the parser marks it `unparsed`. Refetch that journey.
- **Multiple roots**: usually a disconnected draft branch. Listed as orphans in the IR. Mention it, do not build it.
