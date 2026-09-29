# Contributing

## Ground rules

1. **No client data, ever.** No client names, org aliases, EIDs, My Domain or tenant hosts, record ids, record or DE names, row counts, phone numbers or emails. Lessons go in generic form. Run the check before every commit:
   ```bash
   python3 scripts/check_generic.py --engagement <your engagement dir> --denylist ~/.mcnext-denylist
   ```
2. **Don't weaken the guard.** Changes to `.claude/hooks/guard.py` or the `permissions` block in `.claude/settings.json` need a test showing that production writes, flow activation and approval self-grants are still blocked.
3. **Short sentences, no filler, no em dashes** in agent prompts and client-facing templates.

## What goes where

| Change | Place |
|---|---|
| New platform behaviour | `docs/platform-notes.md`, and a one-liner in `CLAUDE.md` if every agent needs it |
| Setup knowledge | `.claude/skills/mcnext-setup/references/kb/` with a source tag (`[AB:]`, `[MCT:]`, `[FIELD]`) |
| A Chrome control that now works | "Known controls" table in `chrome_playbook.md`: page, control, the rung that worked |
| New specialist | skill + agent + orchestrator `Agent(...)` list + phase in `scaffold/manifest.template.json` and the schema |

## Checks

CI (`.github/workflows/ci.yml`) runs the genericity check, byte-compiles every script, validates the scaffold manifest against the schema, runs the guard self-tests and the journey translator on its fixtures. Run the same locally:

```bash
python3 scripts/check_generic.py
python3 -m compileall -q .claude scripts tools
bash tests/run.sh
```
