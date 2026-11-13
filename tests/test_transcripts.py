import json
from pathlib import Path
import tempfile
import unittest
from transcripts import transcript

class TranscriptTest(unittest.TestCase):
    def test_roles_order_and_session_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'sessions').mkdir()
            rows=[{'type':'session_meta','payload':{'id':'target'}}]
            for role,text in [('user','Question one'),('assistant','Answer one'),('user','Question two')]:
                rows.append({'type':'response_item','payload':{'role':role,'content':[{'type':'input_text' if role=='user' else 'output_text','text':text}]}})
            (root/'sessions'/'fixture.jsonl').write_text('\n'.join(json.dumps(x) for x in rows))
            actual=transcript('Codex','target',root)
            self.assertEqual([r['role'] for r in actual],['user','assistant','user'])
            self.assertEqual([r['text'] for r in actual],['Question one','Answer one','Question two'])
            with self.assertRaises(FileNotFoundError):transcript('Codex','missing',root)
