import json
from pathlib import Path
import tempfile
import unittest
from providers import read_projects

class ProviderTest(unittest.TestCase):
    def fixture(self, rows, provider):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);project=root/'projects'/'sample';project.mkdir(parents=True)
            (project/'session.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows)+'{"unfinished":')
            return read_projects(root,provider)

    def test_claude(self):
        rows=[{'type':'user','sessionId':'s','message':{'role':'user','content':'Example question'}},
              {'type':'assistant','uuid':'a','sessionId':'s','message':{'role':'assistant','content':[{'type':'thinking','thinking':'private'},{'type':'text','text':'Example answer'}],'stop_reason':'end_turn'}}]
        result=self.fixture(rows,'Claude Code')
        self.assertEqual(result[0]['text'],'Example answer')
        self.assertEqual(result[0]['thread'],'s')
        self.assertEqual(result[0]['title'],'Example question')
        self.assertEqual(result[0]['question'],'Example question')

    def test_workbuddy(self):
        rows=[{'role':'assistant','status':'streaming','content':'Incomplete'},
              {'id':'a','sessionId':'s','role':'assistant','status':'completed','timestamp':1700000000000,'content':[{'type':'output_text','text':'Done'},{'type':'tool_use','text':'not user text'}]}]
        result=self.fixture(rows,'WorkBuddy')
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['text'],'Done')
        self.assertTrue(result[0]['time'].startswith('2023-'))
