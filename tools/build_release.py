"""Build a source-only archive from the reviewed allowlist; never package local data."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from release_check import ROOT, check

parser = argparse.ArgumentParser()
parser.add_argument('output', help='Output zip path outside the source directory')
args = parser.parse_args()
output = Path(args.output).resolve()
if output.is_relative_to(ROOT): raise SystemExit('Archive must be outside the source directory')
if output.exists(): raise SystemExit('Output already exists; refusing to overwrite')
if not check(): raise SystemExit('Release check failed')
manifest = json.loads((ROOT / 'release-manifest.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for name in manifest['files']:
        archive.write(ROOT / name, 'viral-prompt-studio/' + name)
print('SHA256: ' + hashlib.sha256(output.read_bytes()).hexdigest())
