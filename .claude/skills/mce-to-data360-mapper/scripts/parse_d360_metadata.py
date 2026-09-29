#!/usr/bin/env python3
"""Parse a stored d360_metadata tool result into DMO inventory CSVs.

Usage: parse_d360_metadata.py <tool_result.json> <out_dir> [--prefix CLIENT]
Produces <prefix>_D360_DMO_summary.csv and <prefix>_D360_DMO_field_inventory.csv
and prints a JSON summary (counts, type distribution, findings) to stdout.
"""
import json,sys,csv,re,os
from collections import Counter

def load(path):
    d=json.load(open(path))
    t=d[0]['text'] if isinstance(d,list) else d.get('text',json.dumps(d))
    p=json.loads(t)
    inner=p.get('defaultExc',p)
    if isinstance(inner,str): inner=json.loads(inner)
    return inner['result']['metadata']

def layer(n):
    if n.startswith(('Dg_','Data_Graph','Data_360_Data_Graph')) or n=='DataGraphStateTable__dlm': return 'Data graph'
    if n.startswith('Unified'): return 'Identity resolution'
    if '_Unified_SM' in n: return 'Segment membership'
    if n.startswith('ssot__'): return 'Standard model (ssot__)'
    if n.startswith('PR_'): return 'Profile refresh (PR_)'
    if n.endswith(('_Home__dll','_Home__dlm')): return 'CRM Home'
    if n.startswith('CUR_'): return 'Curated'
    if n.endswith('__dll'): return 'Raw DLO'
    if n.endswith('__cio'): return 'Calculated insight'
    return 'Custom / events'

def main():
    src,out=sys.argv[1],sys.argv[2]
    prefix=sys.argv[sys.argv.index('--prefix')+1] if '--prefix' in sys.argv else 'Client'
    os.makedirs(out,exist_ok=True)
    m=load(src)
    fields=[];summ=[]
    for o in m:
        pk={k['name'] for k in (o.get('primaryKeys') or [])}
        for f in o.get('fields',[]):
            fields.append([o['name'],o.get('displayName'),o.get('category') or '',layer(o['name']),f['name'],f.get('displayName'),f.get('type'),f.get('businessType'),'Y' if f['name'] in pk else ''])
        summ.append([o['name'],o.get('displayName'),o.get('category') or '',layer(o['name']),len(o.get('fields',[])),';'.join(pk)])
    with open(f'{out}/{prefix}_D360_DMO_field_inventory.csv','w',newline='') as fh:
        w=csv.writer(fh);w.writerow(['dmo_api_name','dmo_label','category','layer','field_api_name','field_label','type','business_type','is_primary_key']);w.writerows(fields)
    with open(f'{out}/{prefix}_D360_DMO_summary.csv','w',newline='') as fh:
        w=csv.writer(fh);w.writerow(['dmo_api_name','dmo_label','category','layer','field_count','primary_keys']);w.writerows(sorted(summ,key=lambda r:(r[3],r[0])))
    flags=Counter()
    for r in fields:
        n=r[4].lower()
        if re.match(r'^(is|has)[_A-Z]',r[4]) and r[7]!='BOOLEAN': flags['bool_flag_not_boolean']+=1
        if re.search(r'(dob|dateofbirth|date_of_birth)',n) and r[7] not in ('DATE','DATE_TIME'): flags['dob_not_date']+=1
        if re.search(r'emailaddress$',n) and r[7]!='EMAIL': flags['email_not_email_type']+=1
    print(json.dumps(dict(dmos=len(summ),fields=len(fields),by_layer=Counter(s[3] for s in summ),by_category=Counter(s[2] for s in summ),
        by_business_type=Counter(r[7] for r in fields),no_pk=[s[0] for s in summ if not s[5]],zero_fields=[s[0] for s in summ if s[4]==0],
        duplicate_env_twins=[s[0] for s in summ if re.search(r'_(UAT|DEV|SIT|PROD)\d*__dl',s[0])],
        demo_rulesets=[s[0] for s in summ if s[0].startswith('Unified') and s[0].endswith('Demo__dlm')],typing_flags=flags),indent=1,default=str))
if __name__=='__main__': main()
