"""Optional verification; reads an existing key without copying it into this repo."""
import argparse
import json
import os
from pathlib import Path
from dotenv import dotenv_values
from app import create_app
import tempfile
from tests.test_project import AI,HUMAN,BORDER1,BORDER2
parser=argparse.ArgumentParser()
parser.add_argument('--existing-env',required=True)
args=parser.parse_args()
key=dotenv_values(args.existing_env).get('GROQ_API_KEY','')
if not key:
    raise SystemExit('No existing Groq key found; no credential created.')
directory=tempfile.TemporaryDirectory()
app=create_app({'TESTING':True,'DATABASE':str(Path(directory.name)/'live.sqlite3'),'GROQ_API_KEY':key,'RATELIMIT_ENABLED':False})
client=app.test_client()
results=[]
for name,text in [('course_ai',AI),('course_human',HUMAN),('formal_borderline',BORDER1),('edited_ai_borderline',BORDER2),('explicit_ai_disclosure','As an AI language model, I do not have personal experiences or feelings. This AI-generated paragraph provides a balanced overview of sustainable urban development. It is important to note that effective planning requires collaboration among stakeholders. Furthermore, responsible deployment of innovative technologies can enhance community resilience. In conclusion, a comprehensive approach integrates environmental stewardship, economic opportunity, and social inclusion.')]:
    response=client.post('/submit',json={'creator_id':'synthetic-live-verification','text':text})
    assert response.status_code==200
    result=response.json
    results.append({'name':name,'input':text,'response':result})
    print(name,result['attribution'],result['confidence'], 'semantic_available='+str(result['signals'][2]['available']))
Path('evidence/live-model.json').write_text(json.dumps({'model':'openai/gpt-oss-120b','client':'groq 0.15.0 / httpx 0.28.1, ordinary defaults','mode':'live semantic inference through POST /submit','examples':results},indent=2)+'\n')

assert all(next(s for s in e['response']['signals'] if s['name']=='semantic')['available'] for e in results), 'A live semantic request failed.'
assert {e['response']['attribution'] for e in results} == {'likely_ai','likely_human','uncertain'}, 'The live run did not reach all three labels.'
print('All live signals available; all three plain-text labels reached.')
