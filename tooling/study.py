"""Portable, serial Harbor study runner. Python standard library only."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess


def prepare(spec_path, root):
    spec = json.loads(Path(spec_path).read_text())
    if 'REPLACE' in json.dumps(spec):
        raise ValueError('Replace all example placeholders before preparing')
    if root.exists():
        raise ValueError('Study directory already exists; resume it instead')
    if not spec['tasks'] or len(spec['agents']) < 2:
        raise ValueError('Require tasks and at least two arms')
    ids = [a['id'] for a in spec['agents']]
    if len(ids) != len(set(ids)) or any(not x.replace('-', '').isalnum() for x in ids):
        raise ValueError('Arm IDs must be unique alphanumeric/hyphen strings')
    for task in spec['tasks']:
        if not Path(task).is_dir():
            raise ValueError(f'Task directory missing: {task}')
    root.mkdir(parents=True)
    (root / 'configs').mkdir()
    (root / 'manifest.json').write_text(json.dumps(spec, indent=2))
    db = sqlite3.connect(root / 'ledger.sqlite')
    db.execute('CREATE TABLE cells (id TEXT PRIMARY KEY, digest TEXT, state TEXT, attempts INTEGER)')
    for i, task in enumerate(spec['tasks']):
        for arm in spec['agents']:
            cell = f'{i:04d}-{arm["id"]}'
            config = {'job_name': cell, 'jobs_dir': str(root / 'runs'),
                      'n_attempts': 1, 'n_concurrent_trials': 1,
                      'retry': {'max_retries': 0},
                      'tasks': [{'path': str(Path(task).resolve())}],
                      'environment': {'type': 'docker', 'delete': True},
                      'agents': [arm['harbor']]}
            data = json.dumps(config, indent=2).encode()
            (root / 'configs' / f'{cell}.json').write_bytes(data)
            db.execute('INSERT INTO cells VALUES (?,?,?,0)',
                       (cell, hashlib.sha256(data).hexdigest(), 'pending'))
    db.commit()
    db.close()


def run(root, retry_failed=False):
    with (root / 'runner.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        db = sqlite3.connect(root / 'ledger.sqlite')
        db.execute('PRAGMA synchronous=FULL')
        # A crash is ambiguous: never auto-relaunch an orphan reservation.
        if db.execute("SELECT count(*) FROM cells WHERE state='running'").fetchone()[0]:
            raise RuntimeError('Orphan running reservation: reconcile raw output before any retry')
        spec = json.loads((root / 'manifest.json').read_text())
        version = subprocess.check_output(['harbor', '--version'], text=True).strip()
        if version != spec['harbor_version_output']:
            raise RuntimeError('Harbor version differs from the manifest')
        if retry_failed:
            db.execute("UPDATE cells SET state='pending' WHERE state='error' AND attempts<3")
            db.commit()
        elif db.execute("SELECT count(*) FROM cells WHERE state='error'").fetchone()[0]:
            raise RuntimeError('Review failures before explicit --retry-failed')
        for cell, digest, state, attempts in db.execute('SELECT * FROM cells ORDER BY id').fetchall():
            if state != 'pending':
                continue
            path = root / 'configs' / f'{cell}.json'
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise RuntimeError('Frozen config changed')
            if attempts >= 3:
                raise RuntimeError('Three-attempt cap reached')
            attempts += 1
            config = json.loads(path.read_text())
            job = f'{cell}-attempt-{attempts}'
            config['job_name'] = job
            launch = root / f'{job}.json'
            launch.write_text(json.dumps(config, indent=2))
            db.execute("UPDATE cells SET state='running', attempts=? WHERE id=?", (attempts, cell))
            db.commit()
            with (root / f'{job}.log').open('w') as log:
                result = subprocess.run(['harbor', 'run', '--config', str(launch)], stdout=log, stderr=subprocess.STDOUT)
            results = list((root / 'runs' / job).glob('*/result.json'))
            valid = False
            if result.returncode == 0 and len(results) == 1:
                raw = json.loads(results[0].read_text())
                rewards = (raw.get('verifier_result') or {}).get('rewards')
                valid = not raw.get('exception_info') and bool(rewards)
            db.execute('UPDATE cells SET state=? WHERE id=?', ('completed' if valid else 'error', cell))
            db.commit()
            if not valid:
                raise RuntimeError(f'{job} requires review; raw attempt retained')
        db.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['prepare', 'run'])
    p.add_argument('spec', nargs='?')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--retry-failed', action='store_true')
    a = p.parse_args()
    root = a.output.resolve()
    if a.action == 'prepare':
        prepare(a.spec, root)
    else:
        run(root, a.retry_failed)
