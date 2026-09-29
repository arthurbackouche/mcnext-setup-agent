# MC Next Migration Agents

A team of [Claude Code](https://docs.claude.com/en/docs/claude-code) agents that migrates a Salesforce **Marketing Cloud Engagement (MCE)** estate to **Marketing Cloud Next** (Data 360 + MC Growth / Advanced). It sets up MC Next in a sandbox, triages and translates Journey Builder journeys into MC Next flows, audits AMPscript content, maps data extensions to Data 360, deploys Draft flows and verifies parity, and writes the cutover runbooks.

It is client-agnostic: each client lives in its own engagement folder, and a code-level guard keeps every production write behind a human approval.

```
migration-orchestrator (main session, opus)
├── mcnext-setup         builds MC Next / Data 360 in the sandbox (sf CLI + Chrome)
├── journey-translator   journey triage, flow specs, cutover runbooks       · MCE read-only
├── content-auditor      AMPscript compatibility audit                      · MCE read-only
├── data-mapper          MCE data extensions → Data 360 DMOs and Data Graph · read-only
└── flow-deployer        Draft flow deploys and parity checks               · sandbox only
```

## Quick start

**Prerequisites:** Claude Code, Python 3.9+, the Salesforce CLI (`sf`), a Salesforce sandbox with MC Next and Data 360 licences, and an MCE tenant. Optional: `pip install jsonschema` for full manifest validation, and the Claude in Chrome extension for the setup agent.

```bash
git clone <this repo> mcnext-migration
cd mcnext-migration
python3 scripts/new_engagement.py acme --client "Acme Retail" \
  --sandbox-alias acme-uat --prod-alias acme-prod --mce-eid <EID> --edition advanced
cd ~/Documents/Claude/mcnext-engagements/acme      # or your --root
sf org login web -a acme-uat -r https://test.salesforce.com
# fill .mcp.json (MCE MCP URL, connected-app client id), then:
claude
```

In Claude Code: trust the folder (hooks only run in trusted folders), run `/mcp` and authenticate `sfmc`, `salesforce` and `d360`, restart the session, then ask:

> Run the setup loop and discovery. Stop at the retire-list gate.

## How it works

| Phase | Owner | Gate |
|---|---|---|
| 0 Setup | mcnext-setup | verdict READY, or gaps accepted |
| 1 Discovery | journey-translator | register exists, retire list reviewed by you |
| 2 Content | content-auditor | every in-scope email has a verdict |
| 3 Data | data-mapper | every journey attribute mapped or an explicit gap |
| 4 Translate | journey-translator | Migrate set and consolidation representatives translated |
| 5 Build | flow-deployer | Draft flows deployed, parity verified from the org |
| 6 Cutover | journey-translator | runbooks; production steps one at a time, on your instruction |

State lives in the engagement's `manifest.json` (source of truth) and `STATUS.md` (handoff). Gates are checked against artefacts, never against an agent's word.

## Safety

`.claude/hooks/guard.py` runs before every MCP and Bash call. Reads pass. MCP writes, `sf` changes against production aliases, flow activation, and browser actions on production or MCE pages are blocked until you grant a one-shot approval from your own terminal:

```bash
python3 scripts/approve.py "<key from the block message>" --reason "why"
```

Details and known limits: [docs/safety-model.md](docs/safety-model.md).

## Repository layout

```
.claude/
  agents/        six agent definitions
  skills/        four skills (setup, journey translation, AMPscript audit, data mapping) with scripts and references
  hooks/guard.py the approval guard
  settings.json  main agent, hooks, deny rules
docs/            architecture, safety model, autonomous runs, knowledge base, platform notes
scaffold/        templates rendered into each engagement (manifest, STATUS.md, .mcp.json)
schema/          manifest JSON schema
scripts/         engagement tooling: new_engagement, manifest, approve, run_autonomous, check_generic
tools/kb/        rebuild the setup knowledge base from public sources
research/        article indexes and analysis notes behind the knowledge base
```

## Documentation

- [Architecture](docs/architecture.md): agents, phases, state, framework vs engagement, extending.
- [Safety model](docs/safety-model.md): the guard, approvals, known limits.
- [Autonomous runs](docs/autonomous-runs.md): multi-hour unattended runs with fresh sessions and `/goal`.
- [Setup knowledge base](docs/knowledge-base.md): what `mcnext-setup` knows and where it came from.
- [Platform notes](docs/platform-notes.md): MCE, Data 360 and Claude Code behaviours learned in the field.

## Keeping the framework generic

Client data never belongs in this repo. Before committing:

```bash
python3 scripts/check_generic.py --engagement <engagement dir> [--denylist ~/.mcnext-denylist]
```

It fails on org hosts, tenant URLs, connected-app ids, record ids, phone numbers, emails and the engagement's client terms. CI runs it on every push.

## Credits

Setup knowledge draws on [arthurbackouche.com](https://arthurbackouche.com/docs/) MC Next documentation and the "SFMC Tips" series by Nobuyuki Watanabe ([@marketingcloudtips](https://medium.com/@marketingcloudtips)). The autonomous-run design follows Eva Khmelinskaya's "Running Claude Code Autonomously Overnight".

## License

[MIT](LICENSE). Not affiliated with or endorsed by Salesforce. Use against production orgs at your own risk; the guard reduces risk but does not remove it.
