# MCE → MC Next migration

This agent team is client-agnostic. It runs inside an engagement folder created by `scripts/new_engagement.py`. Client and org details live in that folder's `manifest.json`. Read it first. It is the only source of truth for status.

## Framework vs engagement
- Shared (symlinked into every engagement, must stay generic): `.claude/` (agents, skills, hooks, memory), `scripts/`, `schema/`, `scaffold/`, `CLAUDE.md`, `README.md`.
- Engagement only: `manifest.json`, `STATUS.md`, `.mcp.json`, `out/`, `templates/`, `approvals/`.
- Never write a client name, org alias, EID, host, record id, record name, DE name, DMO suffix or row count into a shared file. Write platform lessons in generic form (e.g. "the Unified Individual DMO name ends with the ruleset id"). Org-specific findings go to the engagement's `out/`.
- Before finishing framework changes, run `python3 scripts/check_generic.py --engagement <engagement dir>`. It must report 0 findings.

## Rules
- MCE is read-only unless an approval exists. The guard hook enforces this. If a call is blocked, tell the user the approve command and stop.
- Flows deploy as Draft to the sandbox alias. Activation and production deploys need approval.
- Never write in `approvals/`. Only the user grants approvals, from their own terminal.
- Validate the manifest after every change: `python3 scripts/manifest.py validate`.
- Short sentences. No filler. No em dashes in client-facing text.

## Context budget (critical for long and autonomous runs)
Every tool output stays in context until the session ends. Keep it small.
1. Redirect command output to a file, then read the end: `cmd > out/logs/<name>.log 2>&1; tail -20 out/logs/<name>.log`.
2. Never let raw API, CLI or HTTP output into the conversation. Summarise with `python3 -c`, grep or `jq`.
3. Do not re-read a file already read in this session. Use grep for lookups. Never cat `manifest.json` whole (over 100 KB).
4. MCP payloads come back inline. Use the smallest page size and slim fields, save them to disk, and work from the file.
5. Specialists: append one line to `<output folder>/progress.log` after each action, so a stalled run leaves a trail.

## Session handoff
- `STATUS.md` at the repo root is the handoff. The orchestrator reads it at session start and updates it before the session ends.
- Statuses live in `manifest.json`. STATUS.md holds the plan, the next units, what waits on the user and the session log.
- Unattended runs go through `scripts/run_autonomous.sh`. Never run them with `--bare` or `bypassPermissions`: both disable the guard.

## Platform behaviours already learned
Short list below. The full record is `docs/platform-notes.md`; add new lessons there in generic form.
- MCE MCP: page size 25 to 50. Larger pages cause OOM.
- Published is not active. Use `activity.lastContactProcessed`.
- Journey payloads come back inline, not as files. Save them verbatim or use the slim schema.
- Connect API and Metadata: GET a UI-built object first and use it as the template. Documented field names are not reliable.
- The Salesforce `sobject-all` MCP has no Tooling or Metadata API. Flows deploy through the `sf` CLI only.
- MC Connect creates `JBSystem_<Object>_RecordFlow` and `JBSystemFlow_<Object>` for Salesforce-entry journeys. Deactivate a pair only when every journey on that object is live in MC Next.
- MC Next Decisions read the Unified Individual Data Graph. Journey Data (`Event.*`) has no direct equivalent.
- Connector tool lists bind at session start. After fixing auth, restart the session.
