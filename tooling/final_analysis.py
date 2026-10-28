"""Reproduce the October analysis from sanitized rows; export private evidence explicitly.

python tooling/final_analysis.py --export-private   # local ledger required
python tooling/final_analysis.py                    # public rows are sufficient
Dependencies: numpy, scipy. Raw transcripts never enter the public export.
"""
import argparse
import csv
import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import beta, binomtest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public/studies/october-2026'
MODELS = ['gpt-6.1-sol', 'gpt-6-astra']
SEED = 10262026
BOOTSTRAPS = 50000


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def resolve(p):
    p = Path(p)
    if p.exists():
        return p
    for name in ('benchmark-medium-2026-10-26-aborted-refusal-adapter', 'benchmark-medium-2026-10-26'):
        if name in p.parts:
            return ROOT / 'evidence/historical-originals' / Path(*p.parts[p.parts.index(name):])
    return p


def classify(text, reward):
    if reward != 0:
        return 'verified_pass', False, None
    if 'Failed to download' in text and 'operation timed out' in text:
        return 'verifier_dependency_download_timeout', True, 'External Python download timed out before test execution.'
    if 'uvx: command not found' in text:
        if 'dpkg was interrupted' in text:
            return 'verifier_setup_interrupted_dpkg', True, 'Verifier unavailable; agent contribution to package-manager state is unresolved.'
        return 'verifier_setup_network_or_package_failure', True, 'Verifier command unavailable following failed package/network setup.'
    if 'Unable to obtain driver for chrome' in text:
        return 'mixed_assertion_and_browser_dependency_failure', False, 'Retained as raw fail: output assertions and browser dependency errors coexist; expanded sensitivity treats as unresolved.'
    return 'verified_fail', False, None


def export_private():
    db = sqlite3.connect(f'file:{ROOT / "ledger.sqlite"}?mode=ro', uri=True)
    cells = db.execute('SELECT id,state,detail FROM cells').fetchall()
    attempts = db.execute('SELECT id,cell,path,state FROM attempts ORDER BY id').fetchall()
    rows = []
    for cell, state, detail in cells:
        model, effort, task, arm = cell.split('--')
        row = dict(cell=cell, model=model, effort=effort, task=task, harness=arm,
                   state=state, raw_reward=None, input_tokens=None, output_tokens=None,
                   cache_tokens=None, identity_verified=False, result_sha256=None,
                   verifier_sha256=None, classification='historical_excluded', unresolved=True,
                   task_checksum=None, exception=None, note=None)
        if state == 'scored':
            detail = json.loads(detail)
            p = resolve(detail['result'])
            raw = json.loads(p.read_text())
            usage = raw.get('agent_result') or {}
            v = p.parent / 'verifier/test-stdout.txt'
            text = v.read_text(errors='replace') if v.exists() else ''
            classification, unresolved, note = classify(text, detail['reward'])
            assert v.exists(), f'Missing verifier for {cell}'
            row.update(raw_reward=int(detail['reward']), input_tokens=usage.get('n_input_tokens'),
                       output_tokens=usage.get('n_output_tokens'), cache_tokens=usage.get('n_cache_tokens'),
                       identity_verified=detail['identity_verified'], result_sha256=sha(p), verifier_sha256=sha(v),
                       classification=classification, unresolved=unresolved, task_checksum=raw.get('task_checksum'),
                       exception=(raw.get('exception_info') or {}).get('exception_type'), note=note)
            assert row['identity_verified'], cell
        rows.append(row)
    attempt_rows = []
    for ident, cell, path, state in attempts:
        results = list(resolve(path).glob('*/result.json'))
        assert len(results) <= 1
        r = json.loads(results[0].read_text()) if results else {}
        u = r.get('agent_result') or {}
        i, o = u.get('n_input_tokens'), u.get('n_output_tokens')
        # Provider errors may report placeholder zeroes, not measured zero cost.
        complete = i is not None and o is not None and not (i + o == 0 and state != 'scored')
        attempt_rows.append(dict(attempt_id=ident, cell=cell, state=state,
                                 input_tokens=i if complete else None, output_tokens=o if complete else None,
                                 usage_complete=complete, result_present=bool(results),
                                 result_sha256=sha(results[0]) if results else None))
    db.close()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'task-results.json').write_text(json.dumps(sorted(rows, key=lambda x:x['cell']), indent=2)+'\n')
    with (OUT / 'task-results.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); writer.writeheader(); writer.writerows(rows)
    (OUT / 'attempts.json').write_text(json.dumps(attempt_rows, indent=2)+'\n')
    private_manifest = json.loads((ROOT / 'manifest.json').read_text())
    provenance = {k:private_manifest[k] for k in ['models','reasoning','tasks','primary_cells','adapter_commit',
                  'source_base_commit','engine_commit','codex_cli','dataset_commit','harbor_commit']}
    provenance.update(harbor_version='0.24.0', architecture='Apple Silicon host; linux/amd64 containers under emulation',
                      source_note='Headless single-agent profile; dirty frontend lockfile excluded. Actual engine checkout differs from parent gitlink.',
                      ledger_sha256=sha(ROOT/'ledger.sqlite'), protocol_sha256=sha(ROOT/'PROTOCOL.md'),
                      frozen_manifest_sha256=sha(ROOT/'frozen.json'),
                      redaction='Allowlisted numeric outcomes, classifications, task IDs and content hashes only. No transcript, credential, account/session identifier or local path exported.',
                      scope='370 ledger reservations including historical attempts; separate synthetic preflights are outside this ledger.',
                      audit_limit='Study-owner artifact review. Independent validation requires access to source evidence; hashes support artifact integrity checks.')
    (OUT/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')


def bound(k, n, lower):
    if lower:
        return 0.0 if k == 0 else float(beta.ppf(.025, k, n-k+1))
    return 1.0 if k == n else float(beta.ppf(.975, k+1, n-k))


def paired_stats(pairs):
    n = len(pairs)
    w = sum(a['raw_reward']==1 and b['raw_reward']==0 for a,b in pairs)
    l = sum(a['raw_reward']==0 and b['raw_reward']==1 for a,b in pairs)
    both = sum(a['raw_reward']==b['raw_reward']==1 for a,b in pairs)
    return dict(n=n, native_solved=both+w, codex_solved=both+l, native_only=w, codex_only=l,
                both_solved=both, both_failed=n-both-w-l, difference=(w-l)/n,
                mcnemar_p=float(binomtest(w,w+l,.5).pvalue) if w+l else 1.0,
                noninferiority_lower=bound(w,n,True)-bound(l,n,False),
                superiority_lower=bound(w,n,True)-bound(l,n,False))


def tokens(pairs):
    complete=[(a,b) for a,b in pairs if all(x['input_tokens'] is not None and x['output_tokens'] is not None for x in (a,b))]
    if not complete:
        return {'n':0}
    a=np.array([x['input_tokens']+x['output_tokens'] for x,y in complete],dtype=np.float64)
    b=np.array([y['input_tokens']+y['output_tokens'] for x,y in complete],dtype=np.float64)
    rng=np.random.default_rng(SEED)
    sample=rng.integers(0,len(a),size=(BOOTSTRAPS,len(a)))
    ratios=a[sample].sum(axis=1)/b[sample].sum(axis=1)
    return dict(n=len(a), native_tokens=int(a.sum()), codex_tokens=int(b.sum()),
                ratio=float(a.sum()/b.sum()), reduction=float(1-a.sum()/b.sum()),
                bootstrap_upper_one_sided_95=float(np.quantile(ratios,.95)),
                bootstrap_central_95=[float(x) for x in np.quantile(ratios,[.025,.975])])


def sensitivity(pairs, expanded=False):
    low=high=0
    for a,b in pairs:
        def interval(x):
            unknown=x['unresolved'] or (expanded and x['classification']=='mixed_assertion_and_browser_dependency_failure')
            return (0,1) if unknown else (x['raw_reward'],x['raw_reward'])
        aa,bb=interval(a),interval(b)
        low+=aa[0]-bb[1]; high+=aa[1]-bb[0]
    return [low/len(pairs), high/len(pairs)]


def analyze():
    rows=json.loads((OUT/'task-results.json').read_text())
    attempts=json.loads((OUT/'attempts.json').read_text())
    models={}
    for model in MODELS:
        groups=defaultdict(dict)
        for row in rows:
            if row['model']==model: groups[row['task']][row['harness']]=row
        allpairs=[(v['80degrees'],v['codex']) for v in groups.values()]
        raw=[(a,b) for a,b in allpairs if a['state']==b['state']=='scored']
        assert all(a['task_checksum']==b['task_checksum'] for a,b in raw)
        adjudicated=[(a,b) for a,b in raw if not a['unresolved'] and not b['unresolved']]
        both=[(a,b) for a,b in adjudicated if a['raw_reward']==b['raw_reward']==1]
        models[model]=dict(raw=paired_stats(raw), resolved_pairs=paired_stats(adjudicated),
                           tokens_raw_complete=tokens(raw), tokens_resolved_complete=tokens(adjudicated),
                           tokens_both_solved_descriptive=tokens(both),
                           full89_difference_sensitivity=sensitivity(allpairs),
                           expanded_difference_sensitivity=sensitivity(allpairs,True),
                           unknown_cells=sum(x['unresolved'] for pair in allpairs for x in pair),
                           raw_wins=[a['task'] for a,b in raw if a['raw_reward']>b['raw_reward']],
                           raw_losses=[a['task'] for a,b in raw if a['raw_reward']<b['raw_reward']])
    for view in ['raw','resolved_pairs']:
        order=sorted(MODELS,key=lambda m:models[m][view]['mcnemar_p'])
        previous=0
        for rank,m in enumerate(order):
            previous=max(previous,min(1,models[m][view]['mcnemar_p']*(2-rank)))
            models[m][view]['mcnemar_holm']=previous
    accounting={}
    for model in MODELS:
        for arm in ['80degrees','codex']:
            aa=[a for a in attempts if a['cell'].startswith(model+'--') and a['cell'].endswith('--'+arm)]
            complete=[a for a in aa if a['usage_complete']]
            accounting[model+' / '+arm]=dict(reservations=len(aa), measured_attempts=len(complete),
                missing_usage=len(aa)-len(complete), observed_tokens=sum(a['input_tokens']+a['output_tokens'] for a in complete),
                zero_model_call_local_failures=sum(a['state']=='local_prelaunch_failure' for a in aa))
    result=dict(analysis_date='2026-10-28', analysis_version='1.1', seed=SEED, bootstraps=BOOTSTRAPS,
                task_cells=len(rows), scored_cells=sum(r['state']=='scored' for r in rows),
                classifications=dict(Counter(r['classification'] for r in rows)),
                attempt_states=dict(Counter(a['state'] for a in attempts)), accounting=accounting, models=models,
                claim_a='Observed raw result: Sol draw; Astra favors Codex. No demonstrated 80 Degrees superiority.',
                claim_b_tokens='Observed complete-pair tokens favor 80 Degrees; the combined comparable-correctness claim does not pass its evidence gate.',
                claim_b_money='Observed Standard API-equivalent raw complete-pair cost favors 80 Degrees; see api-equivalent-costs.json. Not actual subscription spending.',
                analysis_complete=True, evidence_complete=False,
                limitation='Unavailable-verifier outcomes and historical exclusions remain unknown. Findings apply to the recorded medium-reasoning Terminal-Bench 2.0 profiles.')
    (OUT/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--export-private',action='store_true'); args=p.parse_args()
    if args.export_private: export_private()
    analyze()
