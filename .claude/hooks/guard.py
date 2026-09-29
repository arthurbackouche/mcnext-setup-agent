#!/usr/bin/env python3
"""
PreToolUse guard. Claude Code pipes the tool call as JSON on stdin.
Exit 0 = allow. Exit 2 = block (stderr goes back to Claude).

Rules
- MCP tools: reads pass. Anything else needs a one-shot approval file.
- Bash `sf` commands: mutating commands against a production alias need approval.
  Deploying a flow file with <status>Active</status> needs approval on any org.
- Approvals: approvals/<key>.json created by scripts/approve.py. Consumed on use, expire after their TTL.
- Every non-read attempt is appended to approvals/audit.log.
"""
import datetime as dt, glob, json, os, re, shlex, sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
APPROVALS = os.path.join(ROOT, "approvals")
READ_VERB = re.compile(r"(^|_|-)(get|list|describe|find|query|search|retrieve|read|fetch|count|explore|payload_examples|getuserinfo|getobjectschema|getrelatedrecords|soqlquery|listrecent)", re.I)
WRITE_VERB = re.compile(r"(^|_|-)(create|update|delete|upsert|insert|publish|republish|pause|stop|resume|run|execute|schedule|send|fire|exit|clear|refresh|associate|remove|bulk|import|deploy|activate|move|rename|comment|reply|trash|share|merge|upload|spawn|label|unlabel|forward|mark)", re.I)
TARGET_KEYS = ("id", "journey_id", "automation_id", "definitionId", "interactionKey", "recordId", "key", "name", "path")
SF_MUTATING = re.compile(r"\bsf\s+(project\s+deploy|data\s+(create|update|delete|upsert|import)|apex\s+run|org\s+delete|org\s+assign|package\s+install)\b")

def now():
    return dt.datetime.now(dt.timezone.utc)

def audit(entry):
    os.makedirs(APPROVALS, exist_ok=True)
    entry["ts"] = now().isoformat(timespec="seconds")
    with open(os.path.join(APPROVALS, "audit.log"), "a") as fh:
        fh.write(json.dumps(entry) + "\n")

def safe(key):
    return re.sub(r"[^A-Za-z0-9_.:-]+", "_", key)[:180].replace(":", "__")

def consume(key):
    path = os.path.join(APPROVALS, safe(key) + ".json")
    if not os.path.exists(path):
        return None
    appr = json.load(open(path))
    if dt.datetime.fromisoformat(appr["expires_at"]) < now():
        os.remove(path)
        return None
    os.makedirs(os.path.join(APPROVALS, "used"), exist_ok=True)
    os.rename(path, os.path.join(APPROVALS, "used", f"{now():%Y%m%dT%H%M%S}_{safe(key)}.json"))
    return appr

def block(key, why):
    audit({"decision": "blocked", "key": key, "why": why})
    sys.stderr.write(
        f"BLOCKED by migration guard: {why}\n"
        f"This needs explicit human approval. Stop and ask the user to run:\n"
        f"  python3 scripts/approve.py \"{key}\" --reason \"<why>\"\n"
        f"Then retry the same call once. Do not try another route.\n")
    sys.exit(2)

def allow_with(key, why):
    appr = consume(key)
    if appr:
        audit({"decision": "approved", "key": key, "why": why, "reason": appr.get("reason"), "by": appr.get("by")})
        sys.exit(0)
    block(key, why)

def production_aliases():
    try:
        m = json.load(open(os.path.join(ROOT, "manifest.json")))
        return set(m.get("orgs", {}).get("production_aliases", []))
    except Exception:
        return set()

def trusted_org(host):
    """Standing trust for a non-sandbox demo/trial org, granted by the user with
    approve.py "trust:org:<mydomain>" --ttl <minutes>. Not consumed; valid until it expires."""
    mydomain = host.split(".")[0].split("--")[0] if host else ""
    if not mydomain:
        return False
    try:
        appr = json.load(open(os.path.join(APPROVALS, safe(f"trust:org:{mydomain}") + ".json")))
        if dt.datetime.fromisoformat(appr["expires_at"]) > now():
            audit({"decision": "trusted_org", "host": host})
            return True
    except Exception:
        pass
    return False

def check_mcp(tool, args):
    parts = tool.split("__", 2)
    server, name = (parts[1], parts[2]) if len(parts) == 3 else ("?", tool)
    if server == "claude-in-chrome":
        check_chrome(name, args)
    if name.lower() == "execute" and isinstance(args, dict):
        inner = next((v for k, v in args.items() if k.lower() in ("toolname", "tool", "name", "tool_name") and isinstance(v, str)), "")
        if inner and READ_VERB.search(inner) and not WRITE_VERB.search(inner):
            sys.exit(0)
        name = f"execute:{inner or 'unknown'}"
    elif READ_VERB.search(name) and not WRITE_VERB.search(name):
        sys.exit(0)
    target = next((str(args[k]) for k in TARGET_KEYS if isinstance(args, dict) and args.get(k)), "any")
    allow_with(f"{server}:{name}:{target}", f"{server}.{name} is a write/action tool (target {target})")

# ---- Chrome (claude-in-chrome) rule ---------------------------------------
# Browser actions are allowed only on Salesforce SANDBOX hosts and neutral sites.
# Production Salesforce and MCE pages can be opened and read, but any click, type
# or script on them needs an approval. The guard tracks the last navigated host per tab; a tab with
# no known host must navigate by URL before acting.
# Per-engagement state: .claude is shared (symlinked) across engagements, so keep this under out/.
CHROME_STATE = os.path.join(ROOT, "out", ".chrome_state.json")
CHROME_READ_TOOLS = re.compile(r"^(tabs_context(_mcp)?|read_page|get_page_text|find|read_console_messages|read_network_requests|screenshot|gif_creator|resize_window|tabs_close_mcp)$")
CHROME_PASSIVE_ACTIONS = {"screenshot", "scroll", "scroll_to", "zoom", "wait", "hover", "mouse_move", "cursor_position"}
SANDBOX_HOST = re.compile(r"(\.sandbox\.(my\.salesforce|lightning\.force|my\.salesforce-setup|file\.force|my\.site)\.com$|^test\.salesforce\.com$)")
PROD_SF_HOST = re.compile(r"(salesforce\.com|force\.com|salesforce-setup\.com|cloudforce\.com)$")
MCE_HOST = re.compile(r"(exacttarget\.com|marketingcloudapps\.com|exct\.net|marketingcloud\.com)$")
DOCS_HOST = re.compile(r"^(help|developer|trailhead|admin)\.salesforce\.com$")
JS_RISKY = re.compile(r"fetch|XMLHttpRequest|location|window\.open|sendBeacon|\.submit\(|import\(", re.I)

def host_of(url):
    m = re.match(r"^[a-z]+://([^/:?#]+)", (url or "").strip(), re.I)
    return m.group(1).lower() if m else ""

def host_class(host):
    if not host:
        return "unknown"
    if SANDBOX_HOST.search(host):
        return "sandbox"
    if DOCS_HOST.match(host):
        return "neutral"
    if MCE_HOST.search(host):
        return "mce"
    if PROD_SF_HOST.search(host):
        return "sandbox" if trusted_org(host) else "prod"
    return "neutral"

def chrome_state():
    try:
        return json.load(open(CHROME_STATE))
    except Exception:
        return {}

def save_chrome_state(st):
    os.makedirs(os.path.dirname(CHROME_STATE), exist_ok=True)
    with open(CHROME_STATE, "w") as fh:
        json.dump(st, fh)

def check_chrome(name, args):
    args = args if isinstance(args, dict) else {}
    tab = str(args.get("tabId", args.get("tab_id", "default")))
    st = chrome_state()
    if name == "computer" and str(args.get("action", "")).lower() in CHROME_PASSIVE_ACTIONS:
        sys.exit(0)
    if CHROME_READ_TOOLS.match(name):
        sys.exit(0)
    if name in ("navigate", "tabs_create_mcp"):
        url = str(args.get("url", ""))
        if name == "tabs_create_mcp" and not url:
            sys.exit(0)
        host = host_of(url)
        cls = host_class(host)
        if not host:  # back / forward: host unknown until the next URL navigation
            st[tab] = {"host": "", "class": "unknown"}
            save_chrome_state(st)
            sys.exit(0)
        # Opening any page (production included) is a read. The host class is recorded,
        # so clicks, typing and scripts on production or MCE pages still need approval.
        st[tab] = {"host": host, "class": cls}
        save_chrome_state(st)
        audit({"decision": "allowed_chrome_nav", "host": host, "class": cls, "tab": tab})
        sys.exit(0)
    # Anything else is an action: click, type, key, form_input, javascript_tool, upload.
    cur = st.get(tab) or {"host": "", "class": "unknown"}
    if cur["class"] == "unknown":
        sys.stderr.write("BLOCKED by migration guard: this tab has no known host. Call navigate with a full sandbox URL first, then act.\n")
        sys.exit(2)
    if name == "javascript_tool" and (JS_RISKY.search(json.dumps(args)) or cur["class"] != "sandbox"):
        allow_with(f"chrome:javascript:{cur['host']}", f"browser script with network or navigation calls, or off-sandbox, on {cur['host']}")
    if cur["class"] in ("prod", "mce"):
        allow_with(f"chrome:act:{cur['host']}", f"browser action {name} on {cur['class']} host {cur['host']}")
    audit({"decision": "allowed_chrome_act", "tool": name, "action": args.get("action"), "host": cur["host"]})
    sys.exit(0)

def check_bash(cmd):
    if re.search(r"approve\.py|approvals/", cmd):
        audit({"decision": "blocked_self_approval", "cmd": cmd[:300]})
        sys.stderr.write("BLOCKED: agents cannot grant or touch approvals. Only the user runs scripts/approve.py, in their own terminal.\n")
        sys.exit(2)
    if not SF_MUTATING.search(cmd):
        sys.exit(0)
    try:
        toks = shlex.split(cmd)
    except ValueError:
        toks = cmd.split()
    alias = None
    for i, t in enumerate(toks):
        if t in ("-o", "--target-org", "-u", "--targetusername") and i + 1 < len(toks):
            alias = toks[i + 1]
        elif t.startswith("--target-org="):
            alias = t.split("=", 1)[1]
    if "project deploy" in cmd:
        srcs = [toks[i + 1] for i, t in enumerate(toks) if t in ("-d", "--source-dir") and i + 1 < len(toks)] or ["force-app"]
        files = []
        for s in srcs:
            p = os.path.join(ROOT, s)
            files += [p] if p.endswith(".xml") else glob.glob(os.path.join(p, "**", "*.flow-meta.xml"), recursive=True)
        active = [os.path.basename(f) for f in files if os.path.exists(f) and "<status>Active</status>" in open(f).read()]
        if active and "--dry-run" not in cmd:
            allow_with(f"sf:activate:{alias or 'default'}", f"deploy would ACTIVATE {', '.join(active)} on {alias or 'default org'}")
    if alias is None:
        block("sf:no-alias", "mutating sf command without an explicit -o/--target-org. Always name the org")
    if alias in production_aliases() and "--dry-run" not in cmd:
        allow_with(f"sf:prod:{alias}", f"mutating sf command against production alias {alias}")
    audit({"decision": "allowed_nonprod", "cmd": cmd[:300], "alias": alias})
    sys.exit(0)

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # malformed input: do not break the session
    tool = data.get("tool_name", "")
    args = data.get("tool_input") or {}
    if tool.startswith("mcp__"):
        check_mcp(tool, args)
    elif tool == "Bash":
        check_bash(args.get("command", ""))
    sys.exit(0)

if __name__ == "__main__":
    main()
