"""Standard API-equivalent token estimates; never subscription invoices."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/studies/october-2026'
RATES={'gpt-6.1-sol':{'input':2,'cache_read':.1,'cache_write':2.5,'output':10},
       'gpt-6-astra':{'input':10,'cache_read':1,'cache_write':12.5,'output':50}}


def export_audit():
    db=sqlite3.connect(f'file:{ROOT/"ledger.sqlite"}?mode=ro',uri=True)
    audit=[]
    for cell,detail in db.execute("SELECT id,detail FROM cells WHERE state='scored'"):
        p=Path(json.loads(detail)['result']); raw=json.loads(p.read_text()); u=raw.get('agent_result') or {}
        expected=[u.get('n_input_tokens'),u.get('n_output_tokens'),u.get('n_cache_tokens')]
        if None in expected: continue
        requests=[]; files=[]
        if cell.endswith('--80degrees'):
            assert u['metadata']['cache_write_tokens']==0
            f=p.parent/'agent/events.jsonl'; files.append(f)
            for line in f.read_text().splitlines():
                e=json.loads(line); m=e.get('message',{}); x=m.get('usage')
                if e.get('type')=='message_end' and m.get('role')=='assistant' and x:
                    requests.append([x.get('input',0)+x.get('cacheRead',0)+x.get('cacheWrite',0),x.get('output',0),x.get('cacheRead',0),x.get('cacheWrite',0)])
        else:
            for f in sorted((p.parent/'agent/sessions').rglob('*.jsonl')):
                files.append(f); previous=None
                for line in f.read_text().splitlines():
                    v=json.loads(line).get('payload',{}); info=v.get('info')
                    if v.get('type')=='token_count' and info:
                        total=info.get('total_token_usage'); last=info.get('last_token_usage')
                        if total and last and total!=previous:
                            requests.append([last.get('input_tokens',0),last.get('output_tokens',0),last.get('cached_input_tokens',0),last.get('cache_write_input_tokens',0)])
                            previous=total
        assert requests
        assert all(x[3]==0 and 0<=x[2]<=x[0] for x in requests)
        summed=[sum(x[i] for x in requests) for i in range(3)]
        residual=[a-b for a,b in zip(expected,summed)]
        assert all(x>=0 for x in residual) and residual[2]<=residual[0]
        assert residual[0]<=272000 and max(x[0] for x in requests)<=272000
        audit.append(dict(cell=cell,requests_observed=len(requests),max_observed_request_input=max(x[0] for x in requests),
                          residual_input_tokens=residual[0],residual_output_tokens=residual[1],residual_cached_input_tokens=residual[2],
                          cache_write_tokens=0,long_context_premium_applies=False,
                          trace_sha256=[hashlib.sha256(f.read_bytes()).hexdigest() for f in files]))
    db.close()
    (OUT/'pricing-audit.json').write_text(json.dumps(audit,indent=2)+'\n')


def estimate(row):
    r=RATES[row['model']]
    return ((row['input_tokens']-row['cache_tokens'])*r['input']+
            row['cache_tokens']*r['cache_read']+row['output_tokens']*r['output'])/1e6


def generate():
    rows=json.loads((OUT/'task-results.json').read_text())
    audit={x['cell']:x for x in json.loads((OUT/'pricing-audit.json').read_text())}
    result=dict(date='2026-10-28',basis='Standard short-context API-equivalent text-token estimate in USD; not actual subscription spending',
                rates_per_million=RATES,sources=['https://developers.openai.com/api/docs/pricing',
                'https://developers.openai.com/api/docs/models/gpt-6.1-sol','https://developers.openai.com/api/docs/models/gpt-6-astra'],
                assumptions=['Same Standard tier for both arms; no regional premium, tools, tax or subscription allocation.',
                             'Observed cache reads retained; zero recorded cache writes. All observed requests and aggregate residuals are below the >272K long-context threshold.',
                             'Two native aggregate-versus-event residuals are priced using aggregate totals; each residual is below 272K input tokens.',
                             'Scored complete pairs only. Unmeasured timeout usage, failed reservations and historical attempts are excluded; not whole-study cost.'],models={})
    for model in RATES:
        groups={}
        for row in rows:
            if row['model']==model: groups.setdefault(row['task'],{})[row['harness']]=row
        subsets={}
        for name in ['raw_complete','resolved_complete','both_solved']:
            pairs=[]
            for g in groups.values():
                a,b=g['80degrees'],g['codex']
                if any(x['cell'] not in audit for x in [a,b]):continue
                if name!='raw_complete' and (a['unresolved'] or b['unresolved']):continue
                if name=='both_solved' and (a['raw_reward']!=1 or b['raw_reward']!=1):continue
                pairs.append((a,b))
            aa=np.array([estimate(a) for a,b in pairs]); bb=np.array([estimate(b) for a,b in pairs])
            rng=np.random.default_rng(10262026); indices=rng.integers(0,len(pairs),size=(50000,len(pairs)))
            boot=aa[indices].sum(axis=1)/bb[indices].sum(axis=1)
            subsets[name]=dict(n=len(pairs),native_usd=float(aa.sum()),codex_usd=float(bb.sum()),
                               reduction=float(1-aa.sum()/bb.sum()),ratio=float(aa.sum()/bb.sum()),
                               bootstrap_central_95=[float(x) for x in np.quantile(boot,[.025,.975])],
                               bootstrap_upper_one_sided_95=float(np.quantile(boot,.95)))
        result['models'][model]=subsets
    (OUT/'api-equivalent-costs.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--export-private',action='store_true'); a=p.parse_args()
    if a.export_private: export_audit()
    generate()
