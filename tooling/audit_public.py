"""Check the Git candidate set, including forced tracked files. Manual review required."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'README.md', 'CONTRIBUTING.md', 'SECURITY.md', '.gitignore'}
DIRS = {'public', 'docs', 'examples', 'tooling', 'tests'}


def audit():
    names = subprocess.check_output(['git', 'ls-files', '-co', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    failures = []
    for name in set(filter(None, names)):
        path = ROOT / name
        if name not in ALLOWED and Path(name).parts[0] not in DIRS:
            failures.append(f'Outside publication allowlist: {name}')
            continue
        if path.is_symlink():
            failures.append(f'Symlink: {name}')
            continue
        if not path.exists():
            continue
        if path.stat().st_size > 2_000_000:
            failures.append(f'Oversized artifact requires review: {name}')
            continue
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            failures.append(f'Binary artifact requires review: {name}')
            continue
        patterns = [r'/(?:Users|home)/[A-Za-z0-9_.-]+/', '-' * 5 + 'BEGIN ' + r'.*PRIVATE KEY' + '-' * 5,
                    r'eyJ[A-Za-z0-9_-]{20,}\.eyJ', r'sk-[A-Za-z0-9_-]{20,}',
                    r'gh[pousr]_[A-Za-z0-9]{20,}']
        if any(re.search(pattern, text) for pattern in patterns):
            failures.append(f'Potential private data: {name}')
    if failures:
        raise SystemExit('\n'.join(failures))
    print(f'Checked {len(set(filter(None, names)))} publication candidates; manual content review still required.')


if __name__ == '__main__':
    audit()
