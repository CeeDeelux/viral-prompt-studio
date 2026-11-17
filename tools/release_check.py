"""Offline release hygiene check. Prints file names/categories, never matching values.
Not a substitute for reviewing a Git diff or for a full secret scanning service.
"""
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PARTS = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.runtime', 'dist'}
PATTERNS = {
    'credential-like value': re.compile(rb'AIza[0-9A-Za-z_-]{30,}|apify_api_[0-9A-Za-z]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'absolute personal path': re.compile(rb'(?i)(?<![A-Za-z])[A-Z]:[\\/]' + b'|' + b'/'+ b'Users/[^/\\s]+|' + b'/'+ b'home/[^/\\s]+'),
}

def check():
    manifest = json.loads((ROOT / 'release-manifest.json').read_text(encoding='utf-8'))
    failures = []
    expected = set(manifest['files'])
    for path in ROOT.rglob('*'):
        if not path.is_file(): continue
        relative = path.relative_to(ROOT)
        if set(relative.parts) & FORBIDDEN_PARTS: continue
        if path.name.startswith('.env') and path.name != '.env.example': continue
        if relative.as_posix() not in expected:
            failures.append((relative.as_posix(), 'unreviewed file outside manifest'))
    for name in manifest['files']:
        path = ROOT / name
        if not path.is_file() or path.resolve().is_relative_to(ROOT) is False:
            failures.append((name, 'missing or invalid file')); continue
        if set(path.relative_to(ROOT).parts) & FORBIDDEN_PARTS or (path.name.startswith('.env') and path.name != '.env.example'):
            failures.append((name, 'excluded local artifact'))
        raw = path.read_bytes()
        for category, pattern in PATTERNS.items():
            if pattern.search(raw): failures.append((name, category))
    env = (ROOT / '.env.example').read_text(encoding='utf-8')
    for key in ('GEMINI_API_KEY', 'APIFY_API_KEY'):
        if not re.search(r'^' + key + r'=\s*$', env, re.M): failures.append(('.env.example', 'nonempty or missing example key'))
    # If a Git repository is created later, reject tracked local artifacts too.
    if (ROOT / '.git').exists():
        tracked = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-z']).decode().split('\0')
        for name in filter(None, tracked):
            p = Path(name)
            if set(p.parts) & FORBIDDEN_PARTS or (p.name.startswith('.env') and p.name != '.env.example'):
                failures.append((name, 'local artifact tracked by Git'))
        for oid in subprocess.check_output(['git', '-C', str(ROOT), 'rev-list', '--objects', '--all']).decode().splitlines():
            obj = oid.split(' ', 1)[0]
            raw = subprocess.check_output(['git', '-C', str(ROOT), 'cat-file', '-p', obj])
            if any(pattern.search(raw) for pattern in PATTERNS.values()): failures.append((obj, 'historical pattern match'))
    for name, category in failures: print(category + ': ' + name)
    print('FAIL' if failures else 'PASS: release manifest, empty example keys and sensitive-pattern checks')
    return not failures

if __name__ == '__main__': sys.exit(0 if check() else 1)
