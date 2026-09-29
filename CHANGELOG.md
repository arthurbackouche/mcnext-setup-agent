# Changelog

## 0.2.0 (2026-09-29)

MC Next setup skill rebuilt from a full live setup on a demo org.

- Setup intake: every input is asked once, up front (`references/intake.md`, `scaffold/setup_intake.template.json`, `scripts/intake.py init|check|plan`). No change in the org before the intake passes.
- Proven route per step (`references/setup_routes.md`): CLI routes for licences, permission sets and Data 360 enablement; Chrome routes with URLs, verification queries and gotchas for every other step.
- Chrome playbook rewritten: technique only, classic iframe pages, concurrency signals, generic known-controls table.
- PDF handover (`scripts/handover_pdf.py`, reportlab): steps with client-facing summaries, configuration, decisions, customer actions, DNS records, re-verification queries.
- Demo and trial orgs: time-limited org trust grant in the guard (`trust:org:<mydomain>`).
- Verification through the org's own data: MCP connectors can stay bound to another org from session start.

## 0.1.0 (2026-09-28)

First public release.

- Six agents: orchestrator, mcnext-setup, journey-translator, content-auditor, data-mapper, flow-deployer.
- Four skills: mcnext-setup (autonomous sandbox setup with a resumable step file and a Chrome playbook), journey-to-flow-translator, ampscript-mcnext-audit, mce-to-data360-mapper.
- Approval guard for MCP, `sf` CLI and Chrome actions, with one-shot expiring approvals and an audit log.
- Engagement model: client-agnostic framework plus per-client folders (`scripts/new_engagement.py`), and a genericity check (`scripts/check_generic.py`).
- Autonomous runner: fresh `claude -p` sessions with `/goal`, STATUS.md handoff, budget and time caps, retrospective.
- Setup knowledge base built from 58 arthurbackouche.com articles, with field-verified lessons.

## Roadmap

- Merge the Medium "SFMC Tips" series (213 setup-relevant posts) into the setup knowledge base with `[MCT]` tags.
- Metadata route for Data Graph edits (retrieve, edit, deploy to sandbox) as an alternative to the UI.
- New specialists: consent-migrator, deliverability-cutover, audience parity-validator.
