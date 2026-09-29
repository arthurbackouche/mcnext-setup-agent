/goal Autonomous session @@N@@ of run @@RUN_ID@@. Nobody is watching. Work alone, one unit, then hand off.

## Start (in this order)
1. Read your memory index and the memory files that matter for the next unit.
2. Read `STATUS.md`. It is the handoff from the previous session. Trust it as the plan, not as proof.
3. Run `python3 scripts/manifest.py status`. Read only the manifest sections the unit needs, with `python3 -c` or grep. Never cat the whole manifest (it is over 100 KB).
@@PREV_FAIL@@
@@FOCUS@@

## Pick one unit
Take the first unchecked item under "Next units" in STATUS.md that does not need the user. If the list is empty or stale, derive the next unit from the phase order and gates in your instructions.
A unit is one narrow delegation (one specialist, one to two concrete steps, 15 to 45 minutes) or one gate check. Chrome work goes to one agent at a time only.
If the unit is bigger, split it: do the first slice now and write the rest back into "Next units".

## Do the unit
- Delegate with the full context block: client, target org alias, edition, journey ids in scope, manifest path, output folder. Tell the specialist: "Autonomous run. Follow the Context budget rules in CLAUDE.md. Log progress to <output folder>/progress.log after each action. Return a five-line summary plus the manifest keys changed."
- After it returns, check the artefacts exist and recount from them. Never pass a gate on the specialist's word.
- If a gate's criteria are met with evidence, record it: `python3 scripts/manifest.py phase <name> passed --evidence <path>`.
- Validate: `python3 scripts/manifest.py validate`.

## Blocks
- Guard block or a need for login, OAuth consent, MFA or approval: stop that unit. Do not retry it and do not try another route. Add it under "Waiting on user" with the exact command or action, then pick the next independent unit if time allows.
- Anything else broken or missing: skip it, log it in the manifest decisions_log, and continue (user rule).
- Auto-mode classifier "no verdict" errors are transient. Retry once, then move on.
- Never touch `approvals/`. Never target a production alias. Never activate a flow.

## Context budget (hard rules)
- Redirect command output to a file under `out/logs/`, then `tail -20` it. Never let raw API or CLI output into the conversation.
- Do not re-read files already read this session. Use grep or `python3 -c` for lookups.
- MCP payloads come back inline: use the smallest page size and slim fields, save to disk, and summarise.

## Finish (always, even if the unit failed)
1. Update `STATUS.md`:
   - `State:` RUNNING if any unit can still proceed without the user. WAITING_ON_USER only if every remaining unit needs the user. DONE only if every phase that can run in the sandbox is passed.
   - `Updated:` today's date, run @@RUN_ID@@, session @@N@@.
   - Tick the finished unit, rewrite "Next units" so the next session can start cold, and update "Waiting on user".
   - Add one line under "Session log": `@@RUN_ID@@-s@@N@@: <unit> -> <result, with numbers> (<artefact path>)`.
2. Save any new platform behaviour to memory, one line each.
3. Run `python3 scripts/manifest.py validate` as the last command.
4. End with three lines: unit done, result, next unit.

Goal: STATUS.md contains a Session log line starting with "@@RUN_ID@@-s@@N@@:", its State line is one of RUNNING, WAITING_ON_USER or DONE, and the last manifest validate in this session printed "manifest valid".
