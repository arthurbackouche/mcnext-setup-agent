#!/bin/bash
# Framework self-tests: genericity, scaffold, guard rules, translator fixtures, runner preflight.
# Usage: bash tests/run.sh      (exit 0 = all pass)
set -u
FW="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
export DEVELOPER_DIR="${DEVELOPER_DIR:-/Library/Developer/CommandLineTools}"
PASS=0; FAIL=0
# Synthetic client terms generated at runtime, so this file never contains them.
R="$RANDOM$RANDOM"; CLIENT="Client$R"; SBX="sbx$R"; PRD="prd$R"
ok()   { echo "  ok   $1"; PASS=$((PASS + 1)); }
bad()  { echo "  FAIL $1"; FAIL=$((FAIL + 1)); }
expect() { # $1 name, $2 expected exit, $3.. command
  local name="$1" want="$2"; shift 2
  "$@" >"$TMP/last.log" 2>&1; local got=$?
  [ "$got" = "$want" ] && ok "$name" || { bad "$name (exit $got, want $want)"; tail -5 "$TMP/last.log"; }
}

echo "genericity"
expect "no client data in framework" 0 python3 "$FW/scripts/check_generic.py"

echo "scaffold"
expect "create engagement" 0 python3 "$FW/scripts/new_engagement.py" t --client "$CLIENT" \
  --sandbox-alias "$SBX" --prod-alias "$PRD" --mce-eid "9$R" --edition advanced --root "$TMP"
E="$TMP/t"
expect "engagement manifest validates" 0 python3 "$E/scripts/manifest.py" validate
expect "engagement outside framework" 1 python3 "$FW/scripts/new_engagement.py" x --client X \
  --sandbox-alias a --prod-alias b --mce-eid 1 --edition growth --root "$FW/out"
expect "check_generic sees engagement terms" 0 python3 "$FW/scripts/check_generic.py" --engagement "$E"

echo "guard"
guard() { printf '%s' "$1" | CLAUDE_PROJECT_DIR="$E" python3 "$FW/.claude/hooks/guard.py"; }
D='sf project deploy start'
expect "blocks prod deploy"          2 guard "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"$D -o $PRD\"}}"
expect "blocks deploy without -o"    2 guard "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"$D -d force-app\"}}"
expect "allows sandbox deploy"       0 guard "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"$D -o $SBX -d force-app\"}}"
expect "allows prod dry run"         0 guard "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"$D -o $PRD --dry-run\"}}"
expect "blocks self-approval"        2 guard '{"tool_name":"Bash","tool_input":{"command":"python3 scripts/approve.py k --reason x"}}'
expect "allows MCP read"             0 guard '{"tool_name":"mcp__sfmc__sfmc_get_journey","tool_input":{"id":"j1"}}'
expect "blocks MCP write"            2 guard '{"tool_name":"mcp__sfmc__sfmc_pause_journey","tool_input":{"id":"j1"}}'
expect "blocks unknown MCP tool"     2 guard '{"tool_name":"mcp__sfmc__sfmc_frobnicate","tool_input":{}}'
expect "chrome nav to prod is a read" 0 guard '{"tool_name":"mcp__claude-in-chrome__navigate","tool_input":{"url":"https://example.my.salesforce.com/x","tabId":7}}'
expect "blocks click on prod"        2 guard '{"tool_name":"mcp__claude-in-chrome__computer","tool_input":{"action":"left_click","tabId":7}}'
expect "chrome nav to sandbox"       0 guard '{"tool_name":"mcp__claude-in-chrome__navigate","tool_input":{"url":"https://example--uat.sandbox.my.salesforce-setup.com/x","tabId":8}}'
expect "allows click on sandbox"     0 guard '{"tool_name":"mcp__claude-in-chrome__computer","tool_input":{"action":"left_click","tabId":8}}'
expect "blocks JS with network call" 2 guard '{"tool_name":"mcp__claude-in-chrome__javascript_tool","tool_input":{"text":"fetch(\"/x\")","tabId":8}}'
expect "blocks act on unknown tab"   2 guard '{"tool_name":"mcp__claude-in-chrome__computer","tool_input":{"action":"left_click","tabId":99}}'
[ -f "$E/out/.chrome_state.json" ] && ok "chrome state kept in engagement" || bad "chrome state kept in engagement"

echo "journey translator fixtures"
S="$FW/.claude/skills/journey-to-flow-translator"
F="$S/evals/fixtures"
expect "triage"    0 python3 "$S/scripts/parse_journeys.py" --list "$F/interactions_list.json" --out "$TMP/j1" --as-of 2026-09-28
expect "translate" 0 python3 "$S/scripts/parse_journeys.py" --list "$F/interactions_list.json" --workdir "$F/journeys" --out "$TMP/j2" --as-of 2026-09-28
expect "render"    0 python3 "$S/scripts/render_specs.py" --out "$TMP/j2" --client "$CLIENT" --edition advanced
expect "qa"        0 python3 "$S/scripts/qa_outputs.py" --out "$TMP/j2"

echo "runner"
if command -v claude >/dev/null; then
  expect "autonomous runner preflight" 0 bash -c "cd '$E' && scripts/run_autonomous.sh --dry-run --resume test"
else
  echo "  skip autonomous runner preflight (claude CLI not installed)"
fi

echo "python"
expect "byte-compile" 0 python3 -m compileall -q "$FW/.claude" "$FW/scripts" "$FW/tools"

echo
echo "$PASS passed, $FAIL failed"
[ "$FAIL" = 0 ]
