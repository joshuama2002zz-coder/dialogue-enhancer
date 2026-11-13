"""Read local Claude Code and WorkBuddy transcripts; never modify source data."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def text_content(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return '\n'.join(c['text'] for c in content if isinstance(c, dict)
                         and c.get('type') in ('text', 'output_text', 'input_text')
                         and isinstance(c.get('text'), str))
    return ''


def timestamp(value):
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value / 1000 if value > 1e11 else value, timezone.utc).isoformat()
        except (ValueError, OSError, OverflowError):
            return ''
    return value if isinstance(value, str) else ''


def read_projects(root, provider):
    result = []
    # Top-level session files only: subagents are separate internal conversations.
    for path in (root / 'projects').glob('*/*.jsonl'):
        messages = {}; title = ''; question = ''; thread = path.stem
        try:
            with path.open() as stream:
                for index, line in enumerate(stream):
                    try:
                        row = json.loads(line)
                    except ValueError:
                        continue
                    if not isinstance(row, dict):
                        continue
                    thread = row.get('sessionId') or thread
                    msg = row.get('message') if provider == 'Claude Code' else row
                    if not isinstance(msg, dict):
                        continue
                    role = msg.get('role', row.get('type'))
                    content = msg.get('content')
                    body = text_content(content)
                    if role == 'user' and body and not body.lstrip().startswith(('<environment_context>', '<system', '<permissions', '<external_codex_apps', '<tool_result')):
                        question = body
                        if not title: title = body[:100]
                    if role != 'assistant' or not body:
                        continue
                    if row.get('status') not in (None, 'completed'):
                        continue
                    if provider == 'Claude Code' and (row.get('isSidechain') or msg.get('stop_reason') == 'tool_use'):
                        continue
                    identity = str(row.get('uuid') or row.get('id') or msg.get('id') or index)
                    key = hashlib.sha256((provider+'\0'+str(thread)+'\0'+identity+'\0'+body).encode()).hexdigest()
                    messages[identity] = dict(id=key, thread=str(thread), text=body,
                        time=timestamp(row.get('timestamp')), provider=provider, question=question)
            for item in messages.values():
                item['title'] = title or str(thread)
                result.append(item)
        except (OSError, UnicodeError):
            continue
    return result


def capture_other():
    result = []
    for env, default, provider in [('CLAUDE_HOME', '.claude', 'Claude Code'),
                                   ('WORKBUDDY_HOME', '.workbuddy', 'WorkBuddy')]:
        root = Path(os.environ.get(env, str(Path.home()/default))).expanduser()
        result.extend(read_projects(root, provider))
    return result
