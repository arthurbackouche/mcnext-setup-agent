# Security

This project lets AI agents act on Salesforce and Marketing Cloud orgs. Treat it as privileged tooling.

- **Production writes are gated by code.** `.claude/hooks/guard.py` blocks MCP writes, `sf` changes against production aliases, flow activation and browser actions on production or MCE pages until a human grants a one-shot, expiring approval. See [docs/safety-model.md](docs/safety-model.md).
- **The guard fails open if its Python cannot run.** Keep `python3` working; `scripts/run_autonomous.sh` refuses to start if the guard self-test fails.
- **Never run with `--bare`, `--dangerously-skip-permissions` or `bypassPermissions`.** They disable hooks or permission checks.
- **Secrets stay out of the repo.** `.mcp.json`, `approvals/`, `out/` and `manifest.json` live in engagement folders and are git-ignored. OAuth tokens are held by Claude Code, not in files here.
- **Use a sandbox.** Setup and Build target the sandbox alias. Production cutover steps are runbook items a human approves one at a time.

## Reporting a vulnerability

If you find a way for an agent to bypass the guard, self-approve, or write to a production org without approval, please open a private security advisory on the repository rather than a public issue. Include the tool call that got through and the guard version.
