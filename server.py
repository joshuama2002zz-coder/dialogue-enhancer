import json, hashlib, os
from providers import capture_other
from transcripts import transcript
from titles import apply_titles
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
ROOT=Path(__file__).resolve().parent
SOURCE=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))

def capture_codex():
    result=[]
    for directory in ['sessions','archived_sessions']:
        for path in (SOURCE/directory).rglob('*.jsonl'):
            try:
                thread=path.stem; title=''; messages=[]
                with path.open() as stream:
                    for line in stream:
                        try: row=json.loads(line)
                        except (ValueError,TypeError): continue
                        p=row.get('payload',{})
                        if row.get('type')=='session_meta': thread=p.get('id',thread)
                        if row.get('type')!='response_item': continue
                        if p.get('role')=='user' and not title:
                            text='\n'.join(c.get('text','') for c in p.get('content',[]) if c.get('type') in ('input_text','text'))
                            if text and not text.startswith(('<environment_context>','<permissions')): title=text[:100]
                        if p.get('role')!='assistant' or p.get('phase',p.get('channel')) not in ('final_answer','final'): continue
                        if p.get('status') not in (None,'completed'): continue
                        body='\n'.join(c.get('text','') for c in p.get('content',[]) if c.get('type') in ('output_text','text'))
                        if body:
                            key=hashlib.sha256((thread+'\0'+str(p.get('id') or row.get('timestamp'))+'\0'+body).encode()).hexdigest()
                            messages.append(dict(id=key,thread=thread,text=body,time=row.get('timestamp',''),provider='Codex'))
                for m in messages: m['title']=title or thread; result.append(m)
            except (OSError,UnicodeError): continue
    return sorted({m['id']:m for m in result}.values(),key=lambda m:m['time'],reverse=True)

def capture():
    return sorted(apply_titles(capture_codex()+capture_other(),SOURCE),key=lambda m:m['time'],reverse=True)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.headers.get('Host') not in ('127.0.0.1:8765','localhost:8765'):
            self.send_error(403); return
        if self.path=='/api/messages':
            data=json.dumps(capture(),ensure_ascii=False).encode(); kind='application/json'
        elif self.path.startswith('/api/transcript?'):
            query=parse_qs(urlparse(self.path).query)
            try:
                messages=transcript(query.get('provider',[''])[0],query.get('thread',[''])[0],SOURCE)
                data=json.dumps({'messages':messages},ensure_ascii=False).encode();kind='application/json'
            except (ValueError,FileNotFoundError): self.send_error(404);return
        elif self.path.startswith('/api/document?'):
            try:
                name=parse_qs(urlparse(self.path).query).get('path',[''])[0]
                path=Path(name).resolve()
                path.relative_to(ROOT)
                if path.suffix.lower() not in ('.md','.txt','.py','.js','.json','.command','.html','.css') or path.stat().st_size>1000000: raise ValueError()
                data=json.dumps({'text':path.read_text(),'markdown':path.suffix.lower()=='.md'},ensure_ascii=False).encode(); kind='application/json'
            except (OSError,ValueError,UnicodeError): self.send_error(404); return
        elif self.path in ('/vendor/marked.js','/vendor/purify.js'):
            data=(ROOT/self.path.lstrip('/')).read_bytes(); kind='application/javascript'
        elif self.path in ('/','/index.html'):
            data=(ROOT/'index.html').read_bytes(); kind='text/html; charset=utf-8'
        else: self.send_error(404); return
        self.send_response(200); self.send_header('Content-Type',kind); self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.end_headers(); self.wfile.write(data)
    def log_message(self,*a): pass
if __name__=='__main__':
    print('对话增强器：http://127.0.0.1:8765',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
