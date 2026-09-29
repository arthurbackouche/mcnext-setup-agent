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

echo "demo-org trust grant"
DEMO='{"tool_name":"mcp__claude-in-chrome__navigate","tool_input":{"url":"https://demoorg123.lightning.force.com/x","tabId":21}}'
CLICK='{"tool_name":"mcp__claude-in-chrome__computer","tool_input":{"action":"left_click","tabId":21}}'
guard "$DEMO" >/dev/null 2>&1
expect "blocks click on untrusted demo org" 2 guard "$CLICK"
expect "user grants org trust" 0 python3 "$E/scripts/approve.py" "trust:org:demoorg123" --reason test --ttl 5
guard "$DEMO" >/dev/null 2>&1
expect "allows click on trusted demo org" 0 guard "$CLICK"
expect "trust grant is not consumed" 0 guard "$CLICK"
OTHER='{"tool_name":"mcp__claude-in-chrome__navigate","tool_input":{"url":"https://otherorg.lightning.force.com/x","tabId":22}}'
guard "$OTHER" >/dev/null 2>&1
expect "other orgs stay blocked" 2 guard '{"tool_name":"mcp__claude-in-chrome__computer","tool_input":{"action":"left_click","tabId":22}}'

echo "setup intake and handover"
SK="$FW/.claude/skills/mcnext-setup/scripts"
expect "intake init" 0 python3 "$SK/intake.py" init "$E"
expect "blank intake fails check" 1 python3 "$SK/intake.py" check "$E"
python3 - "$E" <<'PY'
import json, sys, os
e = sys.argv[1]
d = json.load(open(os.path.join(e, "out/setup/intake.json")))
d["org"].update(my_domain="example-uat", sf_alias="ex-uat", org_type="sandbox", edition="advanced")
d["setup_user"]["username"] = "admin@example.com"
d["company"] = {"street": "1 Example Street", "city": "Example City", "state": "EX", "postal_code": "0000", "country": "Exampleland"}
d["security_contact"] = {"name": "Example Admin", "email": "security@example.com", "phone": "+10000000000"}
d["sending_domain"].update(root_domain="example.com", from_display_name="Example Co", activate=False)
json.dump(d, open(os.path.join(e, "out/setup/intake.json"), "w"), indent=2)
steps = {f"S{i}": {"status": "done", "evidence": "SOQL check", "summary": f"Step {i} verified."} for i in range(1, 24)}
for s in ("S12", "S22", "S23"):
    steps[s] = {"status": "skipped", "summary": "Not requested in the intake."}
json.dump(steps, open(os.path.join(e, "out/setup/steps.json"), "w"), indent=2)
open(os.path.join(e, "out/setup/dns_records.md"), "w").write(
    "| # | Purpose | Type | Host | Value |\n|---|---|---|---|---|\n| 1 | DKIM | CNAME | `s1._domainkey.e.example.com.` | `s1.e.example.com.dkim.example.net.` |\n")
PY
expect "filled intake passes check" 0 python3 "$SK/intake.py" check "$E"
expect "intake plan" 0 python3 "$SK/intake.py" plan "$E"
if python3 -c "import reportlab" 2>/dev/null; then
  expect "handover PDF generated" 0 python3 "$SK/handover_pdf.py" "$E" --out "$TMP/handover.pdf"
  [ -s "$TMP/handover.pdf" ] && head -c 5 "$TMP/handover.pdf" | grep -q "%PDF" && ok "handover is a PDF" || bad "handover is a PDF"
else
  echo "  skip handover PDF (reportlab not installed)"
fi

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
