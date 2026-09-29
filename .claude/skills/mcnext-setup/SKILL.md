---
name: mcnext-setup
description: Sets up Marketing Cloud Next (Data 360 + Marketing Cloud Growth/Advanced) end to end in a Salesforce sandbox, autonomously. Detects each foundation step, performs it through the sf CLI or the Setup UI with Claude in Chrome, verifies it, and resumes from a step state file across runs. Only logins, MFA, MCE consent, DNS records and production approvals go to the user. Use before Data, Build or Translate work, or when MC Next objects, Data Graphs, consent or the MCE connector seem missing.
---

# MC Next autonomous setup (sandbox)

Knowledge base: `references/kb/` (index `00_index.md`, order `01_setup_order.md`, conflicts `91_contradictions.md`, topic files `10_` to `23_`). Chrome method: `references/chrome_playbook.md`. Original sources: `references/sources/`. Read the KB topic file for a step before doing it. Facts tagged [FIELD] were observed in live implementations and beat article facts, unless the target org shows otherwise. Org-specific findings (names, counts, open items) go only to the engagement's `out/setup/open_items.md`, never into this skill.

## Principles
- **Build, don't just probe.** The job is to reach a working setup. Detect a step, and if it is missing, do it in the same run.
- **Detect, do, verify.** A step is `done` only when a read-only check proves it (SOQL, d360 read, or saved state after a reload). Never on a click alone.
- **Sandbox only.** Changes only on `orgs.sandbox_alias`. Production is blocked by the guard; if blocked, record the key and move on.
- **Licences can't be installed.** Missing entitlement (S2) is a provisioning request. Stop the run with verdict `NOT_PROVISIONED`.
- **Climb the ladder, then hand back.** For a stubborn UI control, follow the interaction ladder in the playbook (rungs 1 to 6) before handing back. Hand back only logins, MFA, MCE consent, DNS changes, production approvals and genuine business decisions.
- **Small runs, resumable state.** Each run does at most two steps, writes state, and returns. The next run picks up from `out/setup/steps.json`.
- **Long jobs don't block.** Data kit deploy, Data 360 enablement, identity resolution runs, graph builds and DNS validation: start, record `running` with `started_at`, return. The next run polls.

## State file: `out/setup/steps.json`
Create it from the catalogue below if missing. One entry per step:
`{"S11": {"status": "pending|running|done|handback|failed|skipped", "attempts": 0, "rungs_tried": [], "started_at": null, "evidence": "", "handback": "", "updated": ""}}`
- `failed` means rungs 1 to 6 all failed this run; retry in a later run at most twice more, then `handback`.
- `handback` entries carry the exact user action. They also go in `out/setup/runbook.md`.
- Keep `out/setup/checks.json` and `verdict.md` in sync after each run.

## Run loop (each run)
1. Read `steps.json`, the manifest `orgs` block, and `references/kb/00_index.md`.
2. Poll every `running` step. Mark `done` when its check passes.
3. Pick the next step: status `pending` or retryable `failed`, all dependencies `done`, no user action needed. Follow catalogue order.
4. Detect (Part 1 check). If already done, record evidence and pick the next step.
5. Do it: CLI first when a CLI route exists, else Chrome per the playbook. Log every action to `out/setup/actions.log` and one line to `out/setup/progress.log`.
6. Verify with the Part 1 check. Update `steps.json`, `checks.json`, `verdict.md`.
7. Stop after two steps, or earlier if Chrome concurrency or a login appears. Return what is next.

## Step catalogue (order and dependencies)
Owner: CLI, UI (Chrome), USER (hand back only). KB = topic file to read first.

| id | Step | Needs | Owner | KB | Verify |
|---|---|---|---|---|---|
| S1 | Org reachable, is sandbox | none | CLI | none | `sf org display`; `SELECT IsSandbox FROM Organization` |
| S2 | MC Next and Data 360 entitlement | S1 | CLI | 10 | PermissionSetLicense / UserLicense rows with Marketing, Data Cloud, CDP, Data 360 |
| S5 | Permission sets exist | S2 | CLI | 10 | `PermissionSet` labels: Marketing Cloud Admin/Manager, Data Cloud Architect **or** Data Cloud Admin |
| S6 | Assign Data Cloud Architect/Admin + Marketing Cloud Admin to the running user | S5 | CLI | 10 | `PermissionSetAssignment` for the user. `sf org assign permsetlicense` first if required |
| S3 | Data 360 enabled (Data Cloud Setup > Get Started) | S6 | UI, long | 11 | any d360 read returns data |
| S4 | CRM connector streams: Sales bundle + custom objects individually + field review | S3 | UI | 13 | `d360_datastream_list`, `_Home` streams per object |
| S21 | DLO to DMO mapping for custom objects (Data Stream > Data Mapping > Start) | S4 | UI | 13 | DMO exists with rows via `d360_query_sql` |
| S7 | Basic Settings checklist incl. Enable Marketing Cloud (last) | S4 | UI | 11 | `SELECT COUNT() FROM CommSubscription` and Basic Settings shows complete |
| S15 | Add Data Protection Details to Records | S7 | UI | 11, 90 | Basic Settings item shows complete. Undocumented: explore per playbook section 5 |
| S9 | Data space selected (Default) | S7 | UI | 11 | Basic Settings shows the data space. Greyed picker = missing Marketing Cloud Admin (S6) |
| S8 | Marketing Data Kits (one "Update" button) | S7 | UI, long | 12 | kit DMOs exist: `ssot__CommunicationSubscriptionConsent__dlm`, email and messaging engagement DMOs |
| S10 | Identity resolution: Generate Ruleset, or build manually; run | S4, S8 | UI, long | 15 | `UnifiedssotIndividual<ruleset id>__dlm` has rows. Never hardcode the name |
| S12 | MCE connector: open wizard to credentials (USER logs in), then BUs, bundles, activation BUs, DE streams | S3 | UI + USER | 14 | MCE streams in `d360_datastream_list` |
| S11 | Data Graph on Unified Individual; related DMOs; select in Configure Basic Personalization | S10, S21 | UI | 16 | `d360_data_graph_get` by API name; field count within 50 per object, 200 per graph [FIELD] |
| S13 | Email: authenticated domain (USER adds DNS), From addresses, reply mail | S7 | UI + USER | 17 | domain status Verified in Setup |
| S16 | Set Up Email: physical address, consent validation, subscriptions | S7 | UI | 17, 18 | Setup pages show saved values; `CommSubscription` rows |
| S22 | Consent seeding for test contacts (Consent Import CSV, or MessagingConsent flow as Draft) | S16 | UI | 18 | test contacts show Opted In on the consent widget |
| S17 | Einstein: Metrics Guard, STO, Engagement Frequency and Scoring (add their DMOs to the graph) | S10, S11 | UI | 19 | toggles on; DMOs present in graph |
| S18 | Analytics packages: Marketing Engagement, SMS, Landing Pages and Forms, Flow Reports | S8 | UI | 20 | Setup > Analytics shows installed |
| S19 | Share access to analytics folders | S18 | UI | 20 | folder sharing saved |
| S20 | Record page components: Privacy Consent Status, Data 360 Profile Engagement, Profile Insights | S11 | UI | 22 | Lightning page shows components (save a new page version, do not overwrite a customised one) |
| S14 | Segment-triggered and on-demand flow types available | S7 | CLI | 21 | `FlowDefinitionView` ProcessType values; flow creation list |
| S23 | First test send: Single Email flow to one opted-in test contact | S13, S16, S22 | UI | 21 | send record status; sandbox send safeguard allows only test addresses |

Parallel tracks when blocked: S12 and S13 wait on the user, so continue with S10, S11, S16, S17, S18 meanwhile.

## Part 1: detection queries
Run SOQL as `sf data query -o <alias> --json -q "<soql>" > out/logs/<name>.json` and summarise with `python3 -c`. Use d360 read tools for Data 360 (`d360_query_sql`, `d360_datastream_list`, `d360_data_graph_get`). The guard blocks `d360_metadata` and `d360_datagraph_metadata` because of their names, not the org: don't call them, probe DMOs by name with `d360_query_sql` instead.

Verdicts in `out/setup/verdict.md`: `NOT_PROVISIONED` (S2 or S5 fails), `PROVISIONED_NOT_ENABLED` (S3, S7 or S8 not done), `ENABLED_INCOMPLETE` (any of S10, S11, S12, S13, S16, S22 not done), `READY` (all steps done or accepted by the user).

## Hand-back format
In `out/setup/runbook.md`, one numbered item per hand-back: what the user does, where (URL), how long, and how the agent will verify. No UI click lists unless the ladder failed.

## Outputs
`out/setup/steps.json`, `checks.json`, `verdict.md`, `runbook.md`, `actions.log`, `progress.log`, GIFs per step. Manifest: update the `setup` block (see agent file) and validate.
After each run, update the "Known controls" table in `references/chrome_playbook.md` with generic control behaviour only (page, control, rung that worked). No org names, hosts, record names or counts.
