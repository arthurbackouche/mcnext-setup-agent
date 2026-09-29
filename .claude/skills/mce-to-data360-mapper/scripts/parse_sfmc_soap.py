#!/usr/bin/env python3
"""Parse stored sfmc_soap_retrieve results (raw SOAP XML in tool_results JSON).

Usage:
  parse_sfmc_soap.py des     <de_retrieve.json>        > de_list.json
  parse_sfmc_soap.py folders <folder_retrieve.json>    > folders.json
  parse_sfmc_soap.py fields  <fields_batch.json> [...] > fields.json
Regex-based on purpose: the SOAP envelope carries unbound prefixes that break ElementTree.
"""
import json,sys,re
def text(path):
    d=json.load(open(path)); return d[0]['text'] if isinstance(d,list) else d['text']
def blocks(t):
    assert 'OverallStatus>OK' in t or 'MoreDataAvailable' in t, 'SOAP status not OK'
    if 'MoreDataAvailable' in t: print('WARNING: MoreDataAvailable, page with ContinueRequest',file=sys.stderr)
    return re.findall(r'<Results[^>]*>(.*?)</Results>',t,re.S)
def g(b,k):
    m=re.search(r'<'+k+r'>(.*?)</'+k+r'>',b,re.S); return m.group(1) if m else ''
mode=sys.argv[1]
if mode=='des':
    rows=[dict(name=g(b,'Name'),key=g(b,'CustomerKey'),cat=g(b,'CategoryID'),send=g(b,'IsSendable'),created=g(b,'CreatedDate')[:10],mod=g(b,'ModifiedDate')[:10]) for b in blocks(text(sys.argv[2]))]
    json.dump(rows,sys.stdout)
elif mode=='folders':
    F={}
    for b in blocks(text(sys.argv[2])):
        pid=re.search(r'<ParentFolder>.*?<ID>(\d+)</ID>',b,re.S)
        F[g(b,'ID')]=[g(b,'Name'),int(pid.group(1)) if pid else 0]
    json.dump(F,sys.stdout)
elif mode=='fields':
    rows=[]
    for p in sys.argv[2:]:
        for b in blocks(text(p)):
            ck=re.search(r'<DataExtension>.*?<CustomerKey>(.*?)</CustomerKey>',b,re.S)
            rows.append(dict(key=ck.group(1) if ck else '',field=g(b,'Name'),ftype=g(b,'FieldType'),maxlen=g(b,'MaxLength'),pk=g(b,'IsPrimaryKey'),req=g(b,'IsRequired'),ord=g(b,'Ordinal')))
    json.dump(rows,sys.stdout)
