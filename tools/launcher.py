"""Start the local application, reuse a healthy instance, never call providers."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / '.runtime'
INSTANCE = hashlib.sha256(str(ROOT).encode()).hexdigest()[:16]

def health(port):
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{int(port)}/api/health', timeout=1) as response:
            info = json.load(response)
            return info if info.get('app') == 'viral-prompt-studio' and info.get('instance') == INSTANCE else None
    except (OSError, ValueError):
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=None)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    if not (ROOT / 'frontend/dist/index.html').is_file():
        raise SystemExit('Run Install-Windows.ps1 first: frontend build is missing.')
    RUNTIME.mkdir(exist_ok=True)
    lock = (RUNTIME / 'startup.lock').open('a+b')
    lock.seek(0); lock.write(b'0'); lock.flush(); lock.seek(0)
    if os.name == 'nt':
        import msvcrt
        try: msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError: raise SystemExit('Another launcher is starting this application. Retry shortly.')
    else:
        import fcntl
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    process = None
    try:
        state_file = RUNTIME / 'server.json'
        try: state = json.loads(state_file.read_text())
        except (OSError, ValueError): state = {}
        port = state.get('port')
        if port and health(port):
            print(f'Viral Prompt Studio is already running: http://127.0.0.1:{port}')
        else:
            from dotenv import dotenv_values
            settings = dotenv_values(ROOT / '.env', interpolate=False) if (ROOT / '.env').exists() else {}
            preferred = args.port if args.port is not None else int(os.environ.get('VPS_PORT', settings.get('VPS_PORT') or 3100))
            if not 0 <= preferred <= 65535:
                raise ValueError('Port must be between 0 and 65535')
            with socket.socket() as probe:
                try: probe.bind(('127.0.0.1', preferred))
                except OSError: probe.bind(('127.0.0.1', 0))
                port = probe.getsockname()[1]
            env = os.environ.copy()
            env.update(VPS_PORT=str(port), PYTHONUTF8='1', PYTHONNOUSERSITE='1')
            with (RUNTIME / 'server.log').open('ab') as log:
                process = subprocess.Popen([sys.executable, str(ROOT / 'backend/app.py')], cwd=ROOT / 'backend', env=env,
                    stdout=log, stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            for _ in range(120):
                if health(port): break
                if process.poll() is not None: raise RuntimeError('Backend exited; inspect .runtime/server.log locally.')
                time.sleep(0.25)
            else: raise RuntimeError('Backend readiness timed out; inspect .runtime/server.log locally.')
            state_file.write_text(json.dumps({'port': port, 'pid': process.pid}), encoding='utf-8')
            print(f'Viral Prompt Studio ready: http://127.0.0.1:{port} (offline by default)')
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=3) as response:
            if b'<title>Viral Prompt Studio</title>' not in response.read():
                raise RuntimeError('Frontend verification failed')
        if not args.no_browser: webbrowser.open(f'http://127.0.0.1:{port}/')
    except Exception:
        if process and process.poll() is None:
            process.terminate(); process.wait(timeout=10)
        raise
    finally:
        lock.close()

if __name__ == '__main__':
    main()
