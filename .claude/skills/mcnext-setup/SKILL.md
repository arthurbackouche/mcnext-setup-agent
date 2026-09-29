---
name: mcnext-setup
description: Sets up Marketing Cloud Next (Data 360 + Marketing Cloud Growth/Advanced) end to end in a Salesforce sandbox or user-trusted demo/trial org. Collects every input up front, then builds each foundation step through the sf CLI and Claude in Chrome, verifies it with the org's own data, resumes across runs from a step file, and finishes with a PDF handover. Use before Data, Translate or Build work, or when MC Next, Data Graphs, consent or the MCE connector need setting up.
---

# MC Next setup: intake, build, verify, hand over

References:
- `references/intake.md`: questions to ask before starting (template `scaffold/setup_intake.template.json`).
- `references/setup_routes.md`: the proven route, verification and gotchas per step. **Read the row before each step.**
- `references/chrome_playbook.md`: browser technique, interaction ladder, known controls.
- `references/kb/`: background knowledge base (sources, limits, contradictions). Tags: `[AB:]`, `[MCT:]` articles, `[FIELD]` observed live.
- Scripts: `scripts/intake.py` (init, check, plan), `scripts/handover_pdf.py` (PDF).

## Principles
- **Inputs first.** No change in the org until `intake.py check` passes. The setup then runs without questions; a missing answer means skip or hand back, never guess.
- **Build, don't just probe.** Detect a step; if missing, do it in the same run.
- **Verify with the org's own data.** A step is `done` only when SOQL through `sf data query -o <alias>` or the saved page state proves it. MCP connectors can stay bound to the org they authenticated to at session start: do not trust an MCP read unless you proved it reads this org (compare with SOQL).
- **Sandbox or trusted demo only.** Changes only on the intake's `sf_alias`. A demo/trial org (IsSandbox=false) needs the user's `trust:org:<mydomain>` grant. Production is blocked by the guard; never route around a block.
- **CLI first, Chrome second.** Licences, permission sets and Data 360 enablement have CLI routes. Basic Settings, identity resolution, Data Graphs, domains and analytics are Chrome-only.
- **Small runs, resumable state.** At most two changing steps per run, then write state and return. Long jobs (Data 360 provisioning, kits, identity resolution, graph builds, installs, DNS) are started, recorded `running` with `started_at`, and polled next run.
- **Generic framework, private engagement.** Names, addresses, hosts, record ids and counts go only to the engagement's `out/setup/`. Lessons for the framework are written in generic form, or to `out/setup/lessons.md` when the run may not edit the framework.

## Phase A: intake (before any change)
1. `python3 .claude/skills/mcnext-setup/scripts/intake.py init <engagement>` if `out/setup/intake.json` is missing.
2. Ask the user every question in `references/intake.md` in one message. Write the answers to `intake.json`.
3. `intake.py check` must print `intake complete`. `intake.py plan` lists the steps the answers skip: record them as `skipped` with the reason.
4. Confirm the prerequisites: `sf` login for the alias, Chrome logged in, trust grant for a demo/trial org.
Subagents cannot ask the user: when delegated without a complete intake, stop and return the missing answers.

## Phase B: preflight (read-only)
Run S1, S2, S5 and a quick read of S3, S4, S7 state with SOQL. Write `out/setup/steps.json` from the catalogue with statuses. Stop with verdict `NOT_PROVISIONED` if S2 or S5 fail: licences need a provisioning request, not setup.

## Phase C: build loop (each run)
1. Read `steps.json`, `intake.json` and the tail of `actions.log`.
2. Poll every `running` step; mark `done` when its check passes.
3. Pick the next step whose dependencies are `done`, in catalogue order, not skipped by the intake.
4. Follow its row in `setup_routes.md`: CLI route first, else Chrome per the playbook. Log each action to `out/setup/actions.log` and one line to `out/setup/progress.log`.
5. Verify, then update the step: `status`, `evidence` (technical: query, value, page), and **`summary` (one client-facing sentence for the handover, no run chatter)**.
6. Stop after two changing steps, or on Chrome concurrency, a login page or a guard block.

`steps.json` entry: `{"status": "pending|running|done|handback|failed|skipped", "attempts": 0, "rungs_tried": [], "started_at": null, "evidence": "", "summary": "", "handback": "", "updated": ""}`. `failed` = ladder rungs 1 to 6 failed this run; retry at most twice more in later runs, then `handback` with exact user steps in `out/setup/runbook.md`.

## Step catalogue (order and dependencies)
| id | Step | Needs | Route |
|---|---|---|---|
| S1 | Org reachable and identified | intake | CLI |
| S2 | MC Next and Data 360 licences | S1 | CLI |
| S5 | Permission sets exist | S2 | CLI |
| S6 | Licences and permission sets assigned to the setup user | S5 | CLI |
| S3 | Data 360 enabled (long) | S6 | CLI metadata, or UI |
| S4 | CRM connector streams (Sales bundle) | S3 | UI (often pre-existing) |
| S21 | Custom-object DLO to DMO mapping | S4 | UI; skip if none |
| S7 | Basic Settings checklist | S4 | UI |
| S15 | Data protection details | S7 | UI |
| S9 | Data space selected (permanent), then Enable Marketing Cloud (long) | S3, S7 | UI + per-permission-set data space grant |
| S8 | Marketing data kits (long) | S9 | UI |
| S10 | Identity resolution: generate, then **run** the ruleset (long) | S4, S8 | UI |
| S11 | Data Graph + Configure Basic Personalization (long build) | S10 | UI |
| S16 | Company address + security contact, consent validation, subscriptions | S7 | UI (classic iframe) |
| S13 | Sending domain + From address + DNS records (activate only if the intake says so) | S7 | UI + user DNS |
| S22 | Consent for the test recipient | S16 | UI; intake-dependent |
| S17 | Einstein features + their DMOs in the graph | S10, S11 | UI |
| S18 | Analytics apps (long) | S8 | UI |
| S19 | Analytics access | S18 | CLI/UI |
| S20 | Record page components on a cloned page | S11 | UI |
| S14 | Flow types available | S7 | UI read |
| S12 | MCE connector (user login) | S3 | UI + user |
| S23 | First test send | S13 active, S22 | UI; intake-dependent |

While S3, S8, S10 or S18 run, continue with independent steps: S16, S13, S14, S17 toggles.

## Phase D: handover
When every step is `done` or `skipped` (or only user hand-backs remain):
1. Update `out/setup/verdict.md` (final state) and the manifest `setup` block: `verdict` = `READY` when all steps are done or skipped by intake/user decision, else `ENABLED_INCOMPLETE`.
2. Generate the PDF: `python3 .claude/skills/mcnext-setup/scripts/handover_pdf.py <engagement>` (needs `reportlab`). Output: `out/setup/<Client>_MC_Next_Setup_Handover.pdf`. It uses each step's `summary`, the intake, `dns_records.md`, and lists skipped steps, customer actions and re-verification queries.
3. Return the PDF path and the open customer actions.

## Verdicts
`NOT_PROVISIONED` (S2 or S5 fail), `PROVISIONED_NOT_ENABLED` (S3, S7 or S8 not done), `ENABLED_INCOMPLETE` (later steps open), `READY` (all steps done or skipped by decision).

## Outputs (engagement folder only)
`out/setup/intake.json`, `steps.json`, `checks.json`, `verdict.md`, `runbook.md`, `actions.log`, `progress.log`, `dns_records.md`, `lessons.md`, the handover PDF, and `out/logs/` query evidence. Manifest: update the `setup` block and validate.
