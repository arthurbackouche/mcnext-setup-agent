# Safety model

Agents work against live Salesforce and Marketing Cloud orgs. The design assumes an agent can be wrong, so writes are gated by code, not by prompts.

## The guard hook

`.claude/hooks/guard.py` runs as a `PreToolUse` hook before every MCP and Bash call (see `.claude/settings.json`). Exit 2 blocks the call and tells the agent the exact approval key.

| Surface | Rule |
|---|---|
| MCP tools | Tool names with a read verb pass. Everything else is blocked by default, including tools never seen before. `execute`-style tools are classified by their inner tool name. |
| `sf` CLI | Mutating commands (`project deploy`, `data create/update/delete/upsert/import`, `apex run`, `org assign`, `package install`...) must name an org with `-o`. Against a production alias (from `manifest.json` `orgs.production_aliases`) they need approval. `--dry-run` passes. |
| Flow activation | Deploying any flow file with `<status>Active</status>` needs approval on every org. |
| Chrome | Opening and reading any page passes. Clicks, typing and forms pass only on Salesforce sandbox hosts, demo/trial orgs the user trusted (below) and neutral sites; on production Salesforce and MCE hosts they need approval. Scripts (`javascript_tool`) pass only on sandbox hosts and never with network or navigation calls. A tab must navigate by URL before it can act. |
| Approvals | Agents can never touch `approvals/` or run `approve.py` (hook plus `permissions.deny`). |

## Approvals

Only a human grants one, from their own terminal, in the engagement folder:

```bash
python3 scripts/approve.py "sfmc:sfmc_pause_journey:<journey-id>" --reason "Cutover step 1, signed off by owner"
```

Approvals are one-shot, target-scoped and expire after 30 minutes (`--ttl`). Every blocked, allowed and granted decision is appended to `approvals/audit.log`.

## Demo and trial orgs

A demo or trial org is not a sandbox (no `.sandbox.` host), so the guard treats it as production. If the user wants it worked like a sandbox, they grant a time-limited trust from their own terminal, in the engagement folder:

```bash
python3 scripts/approve.py "trust:org:<mydomain>" --reason "Demo org, treat as sandbox" --ttl 720
```

Unlike other approvals it is not consumed on use: Chrome actions on that org's hosts pass until it expires. MCE hosts and every other org stay blocked. Deploying metadata to a non-sandbox org can still be stopped by Claude Code's own auto-mode classifier; the user can then run the prepared command themselves.

## Known limits

- **The guard fails open if Python breaks.** A hook that exits with a code other than 2 is a non-blocking error. On macOS the Xcode `python3` shim errors unless `DEVELOPER_DIR=/Library/Developer/CommandLineTools` is set; `.claude/settings.json` sets it (harmless elsewhere). `scripts/run_autonomous.sh` refuses to start if the guard self-test does not block.
- **Hooks only run in a trusted folder.** Trust the engagement folder when Claude Code asks.
- **`--bare` and `bypassPermissions` disable the guard.** Never use them.
- **The guard scans full Bash text.** A command that merely mentions a mutating `sf` command or the approvals folder (in an echo, a test, a heredoc) is blocked too. Put such text in a file and run the file.
- **Chrome `browser_batch` is always blocked** (it has no known host). Use single calls.
- Production changes are never automated. Cutover runbooks list them; a human approves each one.
