"""Export user/assistant text from a single local session, in recorded order."""
import json
import os
from pathlib import Path
from providers import text_content, timestamp


def transcript(provider, thread, codex_root):
    if provider == 'Codex':
        paths = [p for folder in ('sessions','archived_sessions') for p in (codex_root/folder).rglob('*.jsonl')]
    elif provider in ('Claude Code','WorkBuddy'):
        env, default = ('CLAUDE_HOME','.claude') if provider == 'Claude Code' else ('WORKBUDDY_HOME','.workbuddy')
        root = Path(os.environ.get(env,str(Path.home()/default))).expanduser()
        paths = list((root/'projects').glob('*/*.jsonl'))
    else:
        raise ValueError('Unsupported provider')
    result=[];seen=set();found=False
    for path in paths:
        # Filename is a hint only; the session identity inside the file is authoritative.
        rows=[];identity=path.stem
        try:
            for line in path.read_text().splitlines():
                try: row=json.loads(line)
                except ValueError: continue
                if not isinstance(row,dict): continue
                if provider=='Codex' and row.get('type')=='session_meta':
                    identity=row.get('payload',{}).get('id',identity)
                elif row.get('sessionId'): identity=str(row['sessionId'])
                rows.append(row)
        except (OSError,UnicodeError): continue
        if identity!=thread: continue
        found=True
        for i,row in enumerate(rows):
            if provider=='Codex':
                if row.get('type')!='response_item': continue
                msg=row.get('payload',{})
            elif provider=='Claude Code':
                if row.get('isSidechain'): continue
                msg=row.get('message',{})
            else: msg=row
            if not isinstance(msg,dict): continue
            role=msg.get('role');body=text_content(msg.get('content'))
            if role not in ('user','assistant') or not body: continue
            if msg.get('status',row.get('status')) not in (None,'completed'): continue
            if role=='user' and body.lstrip().startswith(('<environment_context>','<permissions','<external_codex_apps')): continue
            key=(str(msg.get('id') or row.get('uuid') or row.get('id') or row.get('timestamp') or i),role,body)
            if key in seen:continue
            seen.add(key);result.append({'role':role,'text':body,'time':timestamp(row.get('timestamp'))})
    if not found: raise FileNotFoundError('Session not found')
    return result
