# Migration status (handoff)

State: RUNNING
Updated: {{DATE}}, created by new_engagement.py

Read this first in every session. Update it before every session ends.
`manifest.json` stays the source of truth for statuses. This file holds the plan and the handoff.

## Snapshot
- Client {{CLIENT}}, edition {{EDITION}}, sandbox `{{SANDBOX_ALIAS}}`, production `{{PROD_ALIAS}}`, MCE EID {{MCE_EID}}.
- All phases not started.

## Waiting on user
- [ ] `sf org login web -a {{SANDBOX_ALIAS}} -r https://test.salesforce.com`
- [ ] Fill `.mcp.json` (MCE MCP URL, connected-app client id), run `/mcp`, authenticate each connector, restart the session.
- [ ] Log in to the sandbox in Chrome once (for the setup agent).
- [ ] Demo/trial org only: grant org trust from your terminal: `python3 scripts/approve.py "trust:org:<mydomain>" --reason "<why>" --ttl 720`.

## Next units (ordered, first one that does not need the user wins)
- [ ] Setup intake: ask the user every question in `.claude/skills/mcnext-setup/references/intake.md` in one message, write `out/setup/intake.json`, run `intake.py check`.
- [ ] Setup loop (runs started with --chrome): delegate "run the setup loop" to mcnext-setup until only hand-backs remain, then generate the handover PDF with `scripts/handover_pdf.py`.
- [ ] Discovery: journey-translator Tier 1 triage of the MCE estate. Stop at the retire-list gate for user review.
- [ ] Content: content-auditor AMPscript audit of emails used by Migrate or Consolidate journeys.
- [ ] Data: data-mapper maps entry DEs and Decision attributes to DMOs and the Data Graph.

## Session log
