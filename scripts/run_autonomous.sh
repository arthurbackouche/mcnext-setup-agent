#!/bin/bash
# Phased autonomous runner for the MCE -> MC Next migration.
#
# Each session is a fresh `claude -p` run of the migration-orchestrator with a
# /goal condition. Sessions hand off through STATUS.md and manifest.json, never
# through conversation context. Run it yourself from a terminal:
#
#   nohup scripts/run_autonomous.sh --hours 10 > /dev/null 2>&1 &
#
# Options
#   --sessions N          max sessions this run (default 20)
#   --hours H             wall-clock cap for the whole run (default 10)
#   --budget USD          max spend per session, passed to --max-budget-usd (default 8)
#   --session-minutes M   kill a session that runs longer than this (default 75)
#   --focus "text"        extra instruction added to every session prompt
#   --chrome              enable Claude in Chrome (Chrome must be open, one agent at a time)
#   --resume RUN_ID       continue an earlier run in the same out/runs/<RUN_ID> folder
#   --no-retro            skip the retrospective session at the end
#   --dry-run             preflight and render the first prompt, launch nothing
#
# Stop a run cleanly:  touch out/runs/STOP   (checked between sessions)
# Watch it:            tail -f out/runs/<RUN_ID>/runner.log
#
# Safety: never add --bare (it skips hooks, so the guard would not run) and never
# use bypassPermissions. The guard hook stays the only way production writes pass.

set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
export DEVELOPER_DIR=/Library/Developer/CommandLineTools

MAX_SESSIONS=20; MAX_HOURS=10; BUDGET=8; SESSION_MIN=75; FOCUS=""; CHROME=0
RUN_ID=""; RETRO=1; DRY=0; MAX_FAILS=3
ORIG_ARGS=("$@")

while [ $# -gt 0 ]; do
  case "$1" in
    --sessions) MAX_SESSIONS="$2"; shift 2 ;;
    --hours) MAX_HOURS="$2"; shift 2 ;;
    --budget) BUDGET="$2"; shift 2 ;;
    --session-minutes) SESSION_MIN="$2"; shift 2 ;;
    --focus) FOCUS="$2"; shift 2 ;;
    --chrome) CHROME=1; shift ;;
    --resume) RUN_ID="$2"; shift 2 ;;
    --no-retro) RETRO=0; shift ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) sed -n '2,26p' "$0"; exit 0 ;;
    *) echo "unknown option: $1"; exit 1 ;;
  esac
done

# Keep the Mac awake for the whole run (on battery with the lid closed it still sleeps).
if [ "$DRY" = 0 ] && [ -z "${AUTORUN_CAFFEINATED:-}" ] && command -v caffeinate >/dev/null; then
  export AUTORUN_CAFFEINATED=1
  exec caffeinate -i -s "$0" "${ORIG_ARGS[@]}"
fi

[ -z "$RUN_ID" ] && RUN_ID="$(date +%Y%m%d-%H%M)"
RUN_DIR="out/runs/$RUN_ID"
mkdir -p "$RUN_DIR" out/logs
LOG="$RUN_DIR/runner.log"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG"; }
notify() { osascript -e "display notification \"$1\" with title \"MC Next migration\"" >/dev/null 2>&1 || true; }
state() { grep -m1 '^State:' STATUS.md 2>/dev/null | awk '{print $2}'; }
hash_status() { shasum STATUS.md 2>/dev/null | awk '{print $1}'; }

render() { # $1 template, $2 session number, $3 prev-fail note
  local t; t="$(cat "$1")"
  local focus_line=""; [ -n "$FOCUS" ] && focus_line="4. Focus for this run, from the user: $FOCUS"
  t="${t//@@RUN_ID@@/$RUN_ID}"; t="${t//@@N@@/$2}"
  t="${t//@@PREV_FAIL@@/$3}"; t="${t//@@FOCUS@@/$focus_line}"
  printf '%s' "$t"
}

# ---- Preflight: stop rather than run unguarded -------------------------------
python3 -c 'print(1)' >/dev/null 2>&1 || { log "ABORT: python3 fails (Xcode shim?). The guard hook would fail open."; exit 1; }
printf '%s' '{"tool_name":"Bash","tool_input":{"command":"sf project deploy start # autorun guard self-test"}}' \
  | CLAUDE_PROJECT_DIR="$ROOT" python3 .claude/hooks/guard.py >/dev/null 2>&1
[ $? -eq 2 ] || { log "ABORT: guard self-test did not block. Fix the guard before running unattended."; exit 1; }
python3 scripts/manifest.py validate > out/logs/autorun_validate.log 2>&1 || { log "ABORT: manifest invalid. See out/logs/autorun_validate.log"; exit 1; }
[ -f STATUS.md ] || { log "ABORT: STATUS.md missing"; exit 1; }
command -v claude >/dev/null || { log "ABORT: claude not on PATH"; exit 1; }
rm -f out/runs/STOP

FLAGS=(-p --agent migration-orchestrator --permission-mode auto --max-budget-usd "$BUDGET")
[ "$CHROME" = 1 ] && FLAGS+=(--chrome)

N=$(( $(ls "$RUN_DIR"/session_*.log 2>/dev/null | wc -l) + 1 ))
if [ "$DRY" = 1 ]; then
  render scripts/autorun/session_prompt.md "$N" "" > "$RUN_DIR/session_$N.prompt.md"
  log "DRY RUN ok. State=$(state). Prompt: $RUN_DIR/session_$N.prompt.md"
  log "Would run: claude ${FLAGS[*]} \"<prompt>\" < /dev/null > $RUN_DIR/session_$N.log"
  exit 0
fi

log "Run $RUN_ID start: sessions<=$MAX_SESSIONS hours<=$MAX_HOURS budget/session=\$$BUDGET session<=${SESSION_MIN}m chrome=$CHROME"
START=$(date +%s); FAILS=0; PREV_FAIL=""; STOP_REASON="session cap reached"

while [ "$N" -le "$MAX_SESSIONS" ]; do
  [ -f out/runs/STOP ] && { STOP_REASON="STOP file"; break; }
  [ $(( $(date +%s) - START )) -ge $(( MAX_HOURS * 3600 )) ] && { STOP_REASON="time cap reached"; break; }
  S="$(state)"
  case "$S" in
    DONE) STOP_REASON="State DONE"; break ;;
    WAITING_ON_USER) STOP_REASON="State WAITING_ON_USER"; break ;;
  esac

  BEFORE="$(hash_status)"
  render scripts/autorun/session_prompt.md "$N" "$PREV_FAIL" > "$RUN_DIR/session_$N.prompt.md"
  log "session $N start (state=$S)"
  claude "${FLAGS[@]}" "$(cat "$RUN_DIR/session_$N.prompt.md")" < /dev/null > "$RUN_DIR/session_$N.log" 2>&1 &
  PID=$!
  WAITED=0; TIMED_OUT=0
  while kill -0 "$PID" 2>/dev/null; do
    sleep 15; WAITED=$((WAITED + 15))
    if [ "$WAITED" -ge $((SESSION_MIN * 60)) ]; then
      pkill -TERM -P "$PID" 2>/dev/null; kill -TERM "$PID" 2>/dev/null; TIMED_OUT=1; break
    fi
  done
  wait "$PID" 2>/dev/null; RC=$?

  OK=1; WHY=""
  [ "$TIMED_OUT" = 1 ] && { OK=0; WHY="killed after ${SESSION_MIN}m"; }
  [ "$RC" -ne 0 ] && [ "$TIMED_OUT" = 0 ] && { OK=0; WHY="exit $RC"; }
  [ "$(hash_status)" = "$BEFORE" ] && { OK=0; WHY="${WHY:+$WHY, }STATUS.md not updated"; }
  grep -q "$RUN_ID-s$N:" STATUS.md || { OK=0; WHY="${WHY:+$WHY, }no session log line"; }
  python3 scripts/manifest.py validate > out/logs/autorun_validate.log 2>&1 || { OK=0; WHY="${WHY:+$WHY, }manifest invalid"; }

  if [ "$OK" = 1 ]; then
    FAILS=0; PREV_FAIL=""
    log "session $N ok ($((WAITED / 60))m): $(grep "$RUN_ID-s$N:" STATUS.md | tail -1 | cut -c1-220)"
  else
    FAILS=$((FAILS + 1))
    log "session $N FAILED ($WHY), consecutive fails=$FAILS. Log: $RUN_DIR/session_$N.log"
    PREV_FAIL="4. The previous session ($RUN_ID-s$N) failed: $WHY. Before any new unit, read the last 40 lines of $RUN_DIR/session_$N.log, find the cause, repair STATUS.md and the manifest, and log the cause under Session log. If the cause needs the user, set State to WAITING_ON_USER."
    [ "$FAILS" -ge "$MAX_FAILS" ] && { STOP_REASON="$MAX_FAILS consecutive failed sessions"; N=$((N + 1)); break; }
  fi
  N=$((N + 1))
  sleep 5
done

log "Run $RUN_ID stopped: $STOP_REASON. Final state=$(state)."
if [ "$RETRO" = 1 ]; then
  render scripts/autorun/retro_prompt.md "0" "" > "$RUN_DIR/retro.prompt.md"
  claude -p --agent migration-orchestrator --permission-mode auto --max-budget-usd 2 \
    "$(cat "$RUN_DIR/retro.prompt.md")" < /dev/null > "$RUN_DIR/retro.log" 2>&1
  log "retro written: $RUN_DIR/retro.md"
fi
notify "Run $RUN_ID stopped: $STOP_REASON. State $(state)."
