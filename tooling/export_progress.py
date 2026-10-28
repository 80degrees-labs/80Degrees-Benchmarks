"""Export aggregate counts only. No logs, task content, accounts or local paths."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def export():
    db = sqlite3.connect(f'file:{ROOT / "ledger.sqlite"}?mode=ro', uri=True)
    counts = dict(db.execute('SELECT state,count(*) FROM cells GROUP BY state'))
    db.close()
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    keys = ['models', 'reasoning', 'tasks', 'primary_cells', 'adapter_commit',
            'source_base_commit', 'engine_commit', 'codex_cli', 'dataset_commit', 'harbor_commit']
    result = {k: manifest[k] for k in keys}
    result.update(snapshot_utc=datetime.now(timezone.utc).isoformat(), counts=counts,
                  final=False, claim_a='not established', claim_b='not established',
                  note='Ledger state is not proof of a live process or adjudicated correctness.')
    out = ROOT / 'public/studies/october-2026'
    out.mkdir(parents=True, exist_ok=True)
    analysis_file = out / 'analysis.json'
    if analysis_file.exists():
        analysis = json.loads(analysis_file.read_text())
        result.update(analysis_complete=analysis['analysis_complete'],
                      evidence_complete=analysis['evidence_complete'],
                      claim_a=analysis['claim_a'], claim_b=analysis['claim_b_tokens'],
                      claim_b_money=analysis['claim_b_money'])
    (out / 'progress.json').write_text(json.dumps(result, indent=2) + '\n')
    n = sum(counts.values())
    done = counts.get('scored', 0)
    width = round(650 * done / n)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="190" viewBox="0 0 760 190" role="img" aria-label="Provisional coverage: {done} of {n} scored slots">
<rect width="760" height="190" rx="14" fill="#101827"/>
<g font-family="sans-serif" fill="#f3f4f6"><text x="40" y="42" font-size="20">TERMINAL-BENCH 2.0 · MEDIUM</text>
<text x="40" y="73" font-size="16">{done} / {n} slots have recorded verifier outcomes · provisional</text>
<rect x="40" y="94" width="650" height="20" rx="4" fill="#374151"/>
<rect x="40" y="94" width="{width}" height="20" rx="4" fill="#5eead4"/>
<text x="40" y="144" font-size="13">Snapshot {result['snapshot_utc'][:19]} UTC · includes unadjudicated outcomes</text>
<text x="40" y="167" font-size="13">Raw correctness: Sol draw; Astra favors Codex. Full scorecard in README.</text></g></svg>'''
    (out / 'coverage.svg').write_text(svg)


if __name__ == '__main__':
    export()
