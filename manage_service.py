"""Install, update, or uninstall the per-user macOS background service."""
import argparse
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys

LABEL = 'local.dialogue-enhancer'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['install', 'uninstall', 'status'])
    args = parser.parse_args()
    if sys.platform != 'darwin':
        parser.error('Background service requires macOS. Use python3 server.py elsewhere.')
    home = Path.home()
    target = home / 'Library/Application Support/DialogueEnhancer'
    config = home / 'Library/LaunchAgents' / (LABEL + '.plist')
    domain = 'gui/' + str(os.getuid())
    service = domain + '/' + LABEL
    if args.action == 'status':
        return subprocess.call(['launchctl', 'print', service])
    if args.action == 'uninstall':
        subprocess.run(['launchctl', 'bootout', service], check=False)
        if config.exists(): config.unlink()
        print('Autostart removed. Application files and browser drafts are preserved.')
        return 0
    source = Path(__file__).resolve().parent
    target.mkdir(parents=True, exist_ok=True)
    if source != target:
        for name in ['server.py', 'providers.py', 'transcripts.py', 'index.html', 'README.md', 'manage_service.py']:
            shutil.copy2(source / name, target / name)
        shutil.copytree(source / 'vendor', target / 'vendor', dirs_exist_ok=True)
    logs = home / 'Library/Logs/DialogueEnhancer'
    logs.mkdir(parents=True, exist_ok=True)
    config.parent.mkdir(parents=True, exist_ok=True)
    data = dict(Label=LABEL, ProgramArguments=[sys.executable, '-u', str(target/'server.py')],
                WorkingDirectory=str(target), RunAtLoad=True, KeepAlive=True,
                ThrottleInterval=5, ProcessType='Background',
                StandardOutPath=str(logs/'stdout.log'), StandardErrorPath=str(logs/'stderr.log'),
                EnvironmentVariables={'CODEX_HOME': str(Path(os.environ.get('CODEX_HOME', str(home/'.codex'))).expanduser().resolve())})
    for env in ['CLAUDE_HOME', 'WORKBUDDY_HOME']:
        if os.environ.get(env): data['EnvironmentVariables'][env] = str(Path(os.environ[env]).expanduser().resolve())
    subprocess.run(['launchctl', 'bootout', service], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    config.write_bytes(plistlib.dumps(data))
    subprocess.run(['launchctl', 'bootstrap', domain, str(config)], check=True)
    print('Installed: http://127.0.0.1:8765 — starts at login and restarts on exit.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
