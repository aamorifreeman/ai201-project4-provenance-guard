"""Optional verification; reads an existing key without copying it into this repo."""
import argparse
import json
import os
from pathlib import Path
from dotenv import dotenv_values
from detection import analyze
from tests.test_project import AI,HUMAN,BORDER1,BORDER2
parser=argparse.ArgumentParser()
parser.add_argument('--existing-env',required=True)
args=parser.parse_args()
key=dotenv_values(args.existing_env).get('GROQ_API_KEY','')
if not key:
    raise SystemExit('No existing Groq key found; no credential created.')
results=[]
for name,text in [('course_ai',AI),('course_human',HUMAN),('formal_borderline',BORDER1),('edited_ai_borderline',BORDER2)]:
    result=analyze(text,api_key=key,model='llama-3.3-70b-versatile')
    results.append({'name':name,'input':text,'response':result})
    print(name,result['attribution'],result['confidence'], 'semantic_available='+str(result['signals'][2]['available']))
Path('evidence/live-model.json').write_text(json.dumps({'model':'llama-3.3-70b-versatile','examples':results},indent=2)+'\n')
