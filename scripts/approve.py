#!/usr/bin/env python3
"""Grant a one-shot approval for a blocked action.
  python3 scripts/approve.py "<key from the block message>" --reason "why" [--ttl 30] [--by "<your name>"]
The guard consumes the approval on the next matching call. Default TTL 30 minutes."""
import argparse, datetime as dt, getpass, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def safe(key):
    return re.sub(r"[^A-Za-z0-9_.:-]+", "_", key)[:180].replace(":", "__")
ap = argparse.ArgumentParser()
ap.add_argument("key"); ap.add_argument("--reason", required=True)
ap.add_argument("--ttl", type=int, default=30, help="minutes"); ap.add_argument("--by", default=getpass.getuser())
a = ap.parse_args()
d = os.path.join(ROOT, "approvals"); os.makedirs(d, exist_ok=True)
now = dt.datetime.now(dt.timezone.utc)
rec = {"key": a.key, "reason": a.reason, "by": a.by, "granted_at": now.isoformat(timespec="seconds"),
       "expires_at": (now + dt.timedelta(minutes=a.ttl)).isoformat(timespec="seconds")}
json.dump(rec, open(os.path.join(d, safe(a.key) + ".json"), "w"), indent=2)
with open(os.path.join(d, "audit.log"), "a") as fh:
    fh.write(json.dumps({"decision": "granted", **rec}) + "\n")
print(f"Approved once: {a.key} (expires {rec['expires_at']})")
