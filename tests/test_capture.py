import json
from pathlib import Path
import tempfile
import unittest
import server

class CaptureTest(unittest.TestCase):
    def test_filter_deduplicate_partial_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.addCleanup(setattr, server, 'SOURCE', server.SOURCE)
            server.SOURCE = Path(tmp)
            folder = server.SOURCE / 'sessions'
            folder.mkdir()
            def message(phase, text):
                return json.dumps({'type':'response_item','timestamp':'2026-01-01','payload':{'role':'assistant','phase':phase,'status':'completed','content':[{'type':'output_text','text':text}]}})+'\n'
            final = message('final_answer', 'Example answer')
            (folder/'fixture.jsonl').write_text(message('commentary','Working')+final+final+'{"partial":')
            result = server.capture()
            self.assertEqual(len(result),1)
            self.assertEqual(result[0]['text'],'Example answer')
            self.assertEqual(result[0]['id'],server.capture()[0]['id'])

    def test_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.addCleanup(setattr, server, 'SOURCE', server.SOURCE)
            server.SOURCE=Path(tmp)
            self.assertEqual(server.capture(),[])
