"""Prefer native session names; derive concise local fallback titles without uploads."""
import json
import os
import re
import sqlite3
from pathlib import Path


def concise(text):
    text = re.sub(r'<[^>]+>', '', text or '')
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'https?://\S+|[/\\][\w./\\-]{20,}', '', text)
    text = re.sub(r'^[#*\s]+', '', text).strip()
    parts = [s.strip(' *#-：:') for s in re.split(r'[\n。！？!?；;]',text) if s.strip()]
    candidates = [s for s in parts if len(s)>4 and not s.startswith(('引用：','要求：','【原回复】','【我的标注】'))]
    text = next((s for s in candidates if re.search(r'构建|开发|创建|分析|研究|整理|设计|实现|修复|安装|优化|搭建|对比|导出|生成',s)), (candidates or parts or ['未命名会话'])[0])
    text = re.sub(r'^(?:(?:我(?:现在)?(?:想要|想|希望|需要)?|请你|请|帮我|给我|能不能|可以|麻烦你|一下|一个)\s*)+', '', text)
    text = re.split(r'[，,](?:因为|出发点|然后|但是|这样|其中|现在|要求)',text)[0]
    text = re.sub(r'\s+', ' ',text).strip('，, ：:') or '未命名会话'
    return text if len(text)<=28 else text[:27].rstrip()+'…'


def native_titles(codex_root):
    titles={}
    try:
        for line in (codex_root/'session_index.jsonl').read_text().splitlines():
            try:
                row=json.loads(line)
                if row.get('id') and row.get('thread_name'):titles[('Codex',row['id'])]=row['thread_name']
            except (ValueError,AttributeError):continue
    except OSError:pass
    root=Path(os.environ.get('WORKBUDDY_HOME',str(Path.home()/'.workbuddy'))).expanduser()
    db=root/'workbuddy.db'
    if db.exists():
        try:
            connection=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True,timeout=1)
            try:
                for identity,title,custom in connection.execute('SELECT id,title,custom_title FROM sessions'):
                    if custom or title:titles[('WorkBuddy',identity)]=custom or title
            finally:connection.close()
        except (sqlite3.Error,ValueError):pass
    root=Path(os.environ.get('CLAUDE_HOME',str(Path.home()/'.claude'))).expanduser()
    for path in (root/'projects').glob('*/sessions-index.json'):
        try:
            for entry in json.loads(path.read_text()).get('entries',[]):
                if entry.get('sessionId') and entry.get('summary'):titles[('Claude Code',entry['sessionId'])]=entry['summary']
        except (OSError,ValueError,AttributeError):continue
    return titles


def apply_titles(messages,codex_root):
    names=native_titles(codex_root)
    for m in messages:
        original=names.get((m['provider'],m['thread']))
        raw=original or m['title']
        if not raw or raw==m['thread'] or raw.lstrip().startswith('<'):raw=m['text']
        m['title']=concise(raw)
        m['titleSource']='native' if original else 'local-summary'
    return messages
