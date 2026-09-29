# Architecture

## Team

| Agent | Model | Skill | Touches | Phase |
|---|---|---|---|---|
| `migration-orchestrator` | opus | none (plans, delegates, gates) | `manifest.json`, `STATUS.md` | all |
| `mcnext-setup` | sonnet | `mcnext-setup` | Salesforce + Data 360 (sandbox), Chrome | 0 Setup |
| `journey-translator` | sonnet | `journey-to-flow-translator` (steps 0-8, 12) | MCE read-only | 1 Discovery, 4 Translate, 6 Cutover |
| `content-auditor` | sonnet | `ampscript-mcnext-audit` | MCE read-only | 2 Content |
| `data-mapper` | sonnet | `mce-to-data360-mapper` | MCE + Data 360 read-only | 3 Data |
| `flow-deployer` | sonnet | `journey-to-flow-translator` (steps 9-11) | `sf` CLI, sandbox Draft only | 5 Build |

The orchestrator is the main session (`"agent": "migration-orchestrator"` in `.claude/settings.json`). Specialists start with no context, so every delegation carries client, org alias, edition, journey ids, manifest path and output folder.

## Phases and gates

| # | Phase | Gate (checked from the artefact, never on an agent's word) |
|---|---|---|
| 0 | Setup | `out/setup/verdict.md` says READY, or the user accepts the listed gaps |
| 1 | Discovery | journey register exists and the user reviewed the retire list |
| 2 | Content | every email used by a Migrate or Consolidate journey has a verdict |
| 3 | Data | every attribute in the journey specs has a mapping or an explicit gap |
| 4 | Translate | Migrate set plus one representative per consolidation family translated |
| 5 | Build | Draft flows deployed to the sandbox and parity verified from the org |
| 6 | Cutover | runbooks; production steps one at a time on explicit user instruction |

Content and Data can run in parallel. Different journeys can sit in different phases.

## State

- `manifest.json` (engagement): single source of truth for phase and journey status. Schema in `schema/manifest.schema.json`. Helper: `scripts/manifest.py validate | status | merge | phase`. Merges never move a journey backwards; a phase cannot pass without evidence; a blocked journey carries a reason.
- `STATUS.md` (engagement): human-readable handoff: plan, next units, what waits on the user, session log. Read first in every session.
- `out/` (engagement): every artefact, per phase folder.

## Framework vs engagement

The framework (this repo) is client-agnostic. `scripts/new_engagement.py` creates an engagement folder outside the repo, symlinks the shared parts (`.claude/`, `scripts/`, `schema/`, `scaffold/`, `CLAUDE.md`, `README.md`) and renders the client-specific files from `scaffold/`. A framework fix reaches every engagement. `scripts/check_generic.py` fails if client data leaks into the framework.

```
mcnext-engagements/acme/          <- one per client, never committed here
├── manifest.json  STATUS.md  .mcp.json
├── out/  templates/  approvals/
└── .claude -> framework/.claude   (and scripts, schema, scaffold, CLAUDE.md, README.md)
```

## Extending

Add a specialist: a skill in `.claude/skills/`, an agent in `.claude/agents/`, its name in the orchestrator's `Agent(...)` tool list, and its phase in `scaffold/manifest.template.json` and the schema. Candidates: consent-migrator, deliverability-cutover, audience parity-validator.

Packaging as a Claude Code plugin: plugin subagents ignore `hooks`, `mcpServers` and `permissionMode`. Keep the guard in project settings.
