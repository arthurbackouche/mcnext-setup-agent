Retrospective for autonomous run @@RUN_ID@@. Do not start any migration work and do not delegate.

Read `out/runs/@@RUN_ID@@/runner.log`, `STATUS.md`, and the last 40 lines of each `out/runs/@@RUN_ID@@/session_*.log` (use tail, never cat whole logs).

Write `out/runs/@@RUN_ID@@/retro.md` with these sections, short sentences, numbers where possible:
1. Outcome: sessions run, units done, gates passed, final State.
2. What worked.
3. What failed or stalled, with the session number and cause.
4. Waiting on user: the exact actions or commands, in order.
5. Changes for the next run: unit sizing, prompts, rules.

Save any new platform behaviour to memory, one line each. End with the path to retro.md.
