#!/usr/bin/env python3
"""Reduce a full DE list to the main / useful set using folder paths and name patterns.

Usage: shortlist_des.py de_list.json folders.json [config.json] > shortlist.json
Prints per-top-folder counts to stderr. Pass a config when a client uses a different
folder taxonomy. Defaults encode the common '_Master / 0N Category' convention.
"""
import json,sys,re
from collections import Counter
des=json.load(open(sys.argv[1])); F=json.load(open(sys.argv[2]))
cfg=json.load(open(sys.argv[3])) if len(sys.argv)>3 else {}
INCLUDE_TOP=cfg.get('include_top',['_Master','05 System','04 Reporting','03 Journeys','02 Transactional'])
ROOT_KEEP=re.compile(cfg.get('root_keep',r'^(IGO_|PI_|Einstein_|CloudPages_|Contacts without Channel|ExpressionBuilderAttributes|_Mobile|_Push|_WhatsApp|_ChatMessaging|JourneySubject_Audit)'))
EXCL_NAME=cfg.get('exclude_name',[r'_TEMP$',r'_Backup$',r'\bVPR\d+',r'[Tt]est',r'TEST',r'Debug',r'_Check\b',r' - 20\d\d-',r'Simulation',r'Sprint [123]\b',r'\b20\d{6}\b',
 r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\s?20\d\d',r'Erroneous',r'Cohort',r'^_DeleteTracking',r'^APIEvent',r'^zz_',r'_stg$',r'_stging$',r'_STAGING1$'])
EXCL_PATH=cfg.get('exclude_path',['Archive','Previews','Erroneous Payments','Catch Up','Missed Payment','Missed First Payment','Discount_Code_Error','Active Subs Awaiting','Referral Marketing','Inactive','IP Warming','QueryStudioResults','07 Test','01 Commercial','Advertising Audiences','Audiences'])
def path(cid):
    p=[];c=str(cid)
    while c in F: n,par=F[c];p.append(n);c=str(par)
    return ' / '.join(reversed(p)) or f'UNKNOWN({cid})'
keep=[];tops=Counter()
for d in des:
    d['path']=path(d['cat']); parts=d['path'].split(' / '); top=parts[1] if len(parts)>1 else parts[0]; tops[top]+=1
    if any(x in d['path'] for x in EXCL_PATH): continue
    if any(re.search(r_,d['name']) for r_ in EXCL_NAME): continue
    if top=='Data Extensions' and not ROOT_KEEP.match(d['name']): continue
    if top!='Data Extensions' and top not in INCLUDE_TOP: continue
    keep.append(d)
print(json.dumps(dict(total=len(des),kept=len(keep),by_top=tops),indent=1),file=sys.stderr)
json.dump(keep,sys.stdout)
