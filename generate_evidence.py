"""Reproduce synthetic local evidence without changing the interactive database."""
import json
import tempfile
from pathlib import Path
from app import create_app
from tests.test_project import AI,HUMAN,BORDER1,BORDER2

def main():
    root=Path(__file__).parent/'evidence'
    root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        app=create_app({'TESTING':True,'DATABASE':str(Path(directory)/'evidence.sqlite3'),'GROQ_API_KEY':''})
        client=app.test_client()
        examples=[]
        for name,content in [('course_ai',AI),('course_human',HUMAN),('formal_borderline',BORDER1),('edited_ai_borderline',BORDER2)]:
            response=client.post('/submit',json={'creator_id':'synthetic-demo','text':content})
            assert response.status_code==200
            examples.append({'name':name,'input':content,'response':response.json})
        metadata=[]
        for name,content,method in [('declared_ai',AI,'ai'),('declared_human',HUMAN,'human'),('unknown',BORDER1,'unknown')]:
            response=client.post('/submit',json={'creator_id':'synthetic-demo','content_type':'metadata','metadata':{'title':name,'description':content,'creation_method':method,'tools':[]}})
            assert response.status_code==200
            metadata.append({'name':name,'response':response.json})
        cid=metadata[0]['response']['content_id']
        appeal=client.post('/appeal',json={'content_id':cid,'creator_reasoning':'Synthetic test appeal: please review the original attribution and process.'})
        assert appeal.status_code==200
        human_id=metadata[1]['response']['content_id']
        verification=client.post('/verification/request',json={'content_id':human_id,'earlier_draft':'The ramen place had salty broth. My friend chose spicy ramen.', 'process_explanation':'Synthetic fixture: a draft was revised into an informal review with personal observations.'})
        assert verification.status_code==201
        reviewed=client.post('/verification/review',json={'verification_id':verification.json['verification_id'],'reviewer':'AUTOMATED TEST FIXTURE — not a human review','review_notes':'Synthetic workflow test only. No real creator verification was performed.','approved':True})
        assert reviewed.status_code==200
        results={'mode':'offline; synthetic fixtures only','text_examples':examples,'metadata_examples':metadata,'appeal':appeal.json,'certificate_workflow':reviewed.json,'analytics':client.get('/analytics').json}
        (root/'examples.json').write_text(json.dumps(results,indent=2)+'\n')
        (root/'audit-sample.json').write_text(json.dumps(client.get('/log').json,indent=2)+'\n')
        app2=create_app({'TESTING':True,'DATABASE':str(Path(directory)/'limit.sqlite3'),'GROQ_API_KEY':''})
        rate=app2.test_client()
        responses=[rate.post('/submit',json={'creator_id':'rate-demo','text':AI}) for _ in range(12)]
        codes=[r.status_code for r in responses]
        assert codes==[200]*10+[429]*2
        (root/'rate-limit.json').write_text(json.dumps({'limits':'10 per minute;100 per day','codes':codes,'final_body':responses[-1].json,'retry_after':responses[-1].headers.get('Retry-After')},indent=2)+'\n')
        print(json.dumps({'labels':[x['response']['attribution'] for x in metadata],'scores':[x['response']['ai_score'] for x in metadata],'rate_limit':codes,'audit_entries':len(client.get('/log').json['entries'])}))
if __name__=='__main__':main()
