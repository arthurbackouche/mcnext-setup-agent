# Autonomous runs

One long chat fills its context window and stops silently; compaction also dilutes instructions. Long unattended runs therefore use many fresh sessions that hand off through files, following the pattern described in Eva Khmelinskaya's "Running Claude Code Autonomously Overnight" (Medium, May 2026).

```bash
nohup scripts/run_autonomous.sh --hours 10 > /dev/null 2>&1 &   # start (from the engagement folder)
tail -f out/runs/<RUN_ID>/runner.log                             # watch
touch out/runs/STOP                                              # stop after the current session
scripts/run_autonomous.sh --dry-run                              # preflight only
```

## How it works

- Each session is `claude -p --agent migration-orchestrator --permission-mode auto` with a `/goal` condition (`scripts/autorun/session_prompt.md`). It reads `STATUS.md`, does one narrow unit, updates `STATUS.md` and the manifest, and exits.
- The runner checks the session actually wrote its session-log line and that the manifest validates. A failed session makes the next one diagnose the log first. Three failures in a row stop the run.
- The run stops when `STATUS.md` says `WAITING_ON_USER` or `DONE`, at the time or session cap, or on `out/runs/STOP`. A retrospective session writes `out/runs/<RUN_ID>/retro.md`.
- `< /dev/null` is required: without it `claude -p` waits for stdin under `nohup` and exits empty.

## Options

| Flag | Default | Meaning |
|---|---|---|
| `--hours` | 10 | wall-clock cap for the run |
| `--sessions` | 20 | max sessions |
| `--budget` | 8 | USD cap per session (`--max-budget-usd`) |
| `--session-minutes` | 75 | kill a session that runs longer |
| `--focus "..."` | none | extra instruction for every session |
| `--chrome` | off | enable Claude in Chrome (setup steps). One Chrome agent at a time. |
| `--resume RUN_ID` | new | continue in the same run folder |
| `--no-retro` | off | skip the retrospective |

## Before starting

- Clear logins and consents: `sf org login` for the sandbox alias, MCE connector consent, Chrome logged in to the sandbox.
- Preflight aborts if `python3` is broken or the guard does not block.
- macOS: keep the machine on power. The runner wraps itself in `caffeinate`.

## Context budget rules (in CLAUDE.md and every agent)

Redirect command output to `out/logs/` and read the tail. Never paste raw API output. Don't re-read files. Save MCP payloads to disk. Specialists log one line per action to `progress.log` and stop after two steps, returning the rest as "remaining".
