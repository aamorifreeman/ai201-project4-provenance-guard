import io
import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from app import create_app, BADGE
from detection import analyze, combine, signal, semantic, LABELS

AI='Artificial intelligence represents a transformative paradigm shift in modern society. It is important to note that while the benefits of AI are numerous, it is equally essential to consider the ethical implications. Furthermore, stakeholders across various sectors must collaborate to ensure responsible deployment.'
HUMAN="ok so i finally tried that new ramen place downtown and honestly? underwhelming. the broth was fine but they put WAY too much sodium in it and i was thirsty for like three hours after. my friend got the spicy version and said it was better. probably won't go back unless someone drags me there"
BORDER1='The relationship between monetary policy and asset price inflation has been extensively studied in the literature. Central banks face a fundamental tension between their mandate for price stability and the unintended consequences of prolonged low interest rates on equity and real estate valuations.'
BORDER2="I've been thinking a lot about remote work lately. There are genuine tradeoffs — flexibility and no commute on one side, isolation and blurred work-life boundaries on the other. Studies show productivity varies widely by individual and role type."

@pytest.fixture
def app(tmp_path):
    return create_app({'TESTING':True,'DATABASE':str(tmp_path/'test.sqlite3'),'GROQ_API_KEY':'','RATELIMIT_ENABLED':False})
@pytest.fixture
def client(app):
    return app.test_client()
def submit(client, text=AI, method=None):
    body={'creator_id':'synthetic-demo','text':text}
    if method:
        body={'creator_id':'synthetic-demo','content_type':'metadata','metadata':{'title':'Example','description':text,'creation_method':method,'tools':[]}}
    return client.post('/submit',json=body)

def test_submission_and_three_labels(client):
    cases=[(AI,'ai','likely_ai'),(HUMAN,'human','likely_human'),(BORDER1,'unknown','uncertain')]
    for text,method,label in cases:
        response=submit(client,text,method)
        assert response.status_code==200
        item=response.json
        assert item['attribution']==label
        assert item['label']==LABELS[label]
        assert 0<=item['confidence']<=1
        assert sum(s['available'] for s in item['signals'])==3
        assert abs(sum(s['normalized_weight'] for s in item['signals'])-1)<.001
        assert client.get('/content/'+item['content_id']).json==item

def test_offline_text_and_four_cases(client):
    results=[submit(client,t).json for t in [AI,HUMAN,BORDER1,BORDER2]]
    assert all(r['attribution']=='uncertain' for r in results)
    assert max(r['ai_score'] for r in results)-min(r['ai_score'] for r in results)>.15
    assert all(any('Fewer than three' in x for x in r['uncertainty_reasons']) for r in results)

@pytest.mark.parametrize('score,label',[(.0,'likely_human'),(.25,'likely_human'),(.2501,'uncertain'),(.51,'uncertain'),(.7999,'uncertain'),(.8,'likely_ai'),(.95,'likely_ai'),(1,'likely_ai')])
def test_thresholds(score,label):
    r=combine([signal(str(i),score,1,{}) for i in range(3)],AI)
    assert r['attribution']==label
    assert r['label']==LABELS[label]

def test_conflict_damping_and_short_text():
    signals=[signal('one',1,1,{}),signal('two',1,1,{}),signal('three',0,1,{})]
    result=combine(signals,AI)
    assert result['ai_score']==pytest.approx(.6083,abs=.0001)
    assert result['attribution']=='uncertain'
    assert combine([signal(str(i),1,1,{}) for i in range(3)],'short poem')['attribution']=='uncertain'
    assert combine([signal(str(i),1,1,{}) for i in range(3)],'你好世界 '*50)['attribution']=='uncertain'

@pytest.mark.parametrize('data', [None,[],{}, {'creator_id':1,'text':'x'}, {'creator_id':'a','text':''}, {'creator_id':'a','text':3}, {'creator_id':'a','text':'x'*10001}, {'creator_id':'a','content_type':'image'}, {'creator_id':'a','content_type':'metadata','metadata':[]}, {'creator_id':'a','content_type':'metadata','metadata':{'title':'x','description':'x','creation_method':'other'}}, {'creator_id':'a','content_type':'metadata','metadata':{'title':'x','description':'x','creation_method':'human','tools':'not a list'}}])
def test_invalid_submissions(client,data):
    response=client.post('/submit',data=json.dumps(data),content_type='application/json')
    assert response.status_code==400
    assert not client.get('/log').json['entries']

def test_non_json_malformed_and_oversized(client):
    assert client.post('/submit',data='hello').status_code==415
    assert client.post('/submit',data='{',content_type='application/json').status_code==400
    assert client.post('/submit',data='x'*70000,content_type='application/json').status_code==413

def test_appeal_original_and_duplicate(client):
    original=submit(client).json
    body={'content_id':original['content_id'],'creator_reasoning':'I wrote this myself in a notebook.'}
    assert client.post('/appeal',json=body).status_code==200
    updated=client.get('/content/'+original['content_id']).json
    assert updated['status']=='under_review'
    assert updated['attribution']==original['attribution']
    assert client.post('/appeal',json=body).status_code==409
    entries=client.get('/log').json['entries']
    assert len(entries)==2
    assert entries[0]['appeal_reasoning']==body['creator_reasoning']
    assert entries[0]['original_decision']['confidence']==original['confidence']
    assert entries[1]['status']=='classified'
    assert len(client.get('/appeals').json['entries'])==1

def test_concurrent_appeals(app,client):
    item=submit(client).json
    body={'content_id':item['content_id'],'creator_reasoning':'This was written from personal experience.'}
    def appeal(_):
        with app.test_client() as c:
            return c.post('/appeal',json=body).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(appeal,range(2)))==[200,409]

def test_missing_and_empty_appeal(client):
    assert client.post('/appeal',json={'content_id':'missing','creator_reasoning':'An explanation of authorship.'}).status_code==404
    assert client.post('/appeal',json={'content_id':'missing','creator_reasoning':' '}).status_code==400
    assert client.get('/content/missing').status_code==404

def test_persistence(app,client):
    item=submit(client).json
    new=create_app({'TESTING':True,'DATABASE':app.config['DATABASE'],'GROQ_API_KEY':'','RATELIMIT_ENABLED':False})
    assert new.test_client().get('/content/'+item['content_id']).json==item
    assert len(new.test_client().get('/log').json['entries'])==1

def test_rate_limit(tmp_path):
    app=create_app({'TESTING':True,'DATABASE':str(tmp_path/'rate.sqlite3'),'GROQ_API_KEY':''})
    client=app.test_client()
    codes=[submit(client).status_code for _ in range(12)]
    assert codes==[200]*10+[429]*2
    last=submit(client)
    assert last.is_json and 'Retry-After' in last.headers
    # Changing caller-controlled creator ID cannot bypass the IP limit.
    assert client.post('/submit',json={'creator_id':'new','text':AI}).status_code==429
    assert len(client.get('/log').json['entries'])==10

def test_certificate_requires_review_and_bound_content(client):
    original=submit(client,HUMAN,'human').json
    body={'content_id':original['content_id'],'earlier_draft':'I tried a new ramen restaurant. It was too salty.',
          'process_explanation':'I drafted these observations in my notebook before revising the story.'}
    pending=client.post('/verification/request',json=body)
    assert pending.status_code==201
    assert client.get('/content/'+original['content_id']).json['certificate'] is None
    assert client.post('/verification/request',json=body).status_code==409
    review={'verification_id':pending.json['verification_id'],'reviewer':'Test reviewer','review_notes':'Checked the distinct earlier draft and process explanation.','approved':True}
    approved=client.post('/verification/review',json=review)
    assert approved.status_code==200
    cert=approved.json['certificate']
    assert cert['label']==BADGE and cert['content_hash']==original['content_hash']
    assert client.post('/verification/review',json=review).status_code==409
    assert client.get('/content/'+original['content_id']).json['attribution']==original['attribution']
    assert submit(client,HUMAN,'human').json['certificate'] is None

def test_rejected_certificate_and_invalid_review(client):
    item=submit(client).json
    invalid={'content_id':item['content_id'],'earlier_draft':item['text'],'process_explanation':'Here is my detailed process with enough characters for review.'}
    assert client.post('/verification/request',json=invalid).status_code==400
    invalid['earlier_draft']='A distinct but incomplete draft for a creative writing project.'
    pending=client.post('/verification/request',json=invalid).json
    review={'verification_id':pending['verification_id'],'reviewer':'Test reviewer','review_notes':'Not enough evidence to grant the limited credential.','approved':'true'}
    assert client.post('/verification/review',json=review).status_code==400
    review['approved']=False
    assert client.post('/verification/review',json=review).json['certificate'] is None

def test_analytics_no_events_double_count(client):
    assert client.get('/analytics').json['appeal_rate']==0
    a=submit(client,AI,'ai').json
    submit(client,HUMAN,'human')
    client.post('/appeal',json={'content_id':a['content_id'],'creator_reasoning':'This synthetic example is being appealed for testing.'})
    stats=client.get('/analytics').json
    assert stats['total_submissions']==2 and stats['appeal_rate']==.5
    assert stats['detection_patterns']=={'likely_ai':1,'likely_human':1,'uncertain':0}

def transport_for(assessment):
    def transport(body,timeout):
        assert timeout==15
        return {'choices':[{'message':{'content':json.dumps(assessment)}}]}
    return transport

@pytest.mark.parametrize('score',[True,'0.8',None,-1,2,float('nan'),float('inf')])
def test_semantic_rejects_invalid_model_scores(score):
    assert not semantic(AI,'synthetic-key',transport=transport_for({'ai_score':score,'explanation':'testing'}))['available']

def test_semantic_contract_and_failure():
    r=semantic(AI,'synthetic-key',transport=transport_for({'ai_score':.92,'explanation':'Synthetic provider response'}))
    assert r['available'] and r['score']==.92
    def offline(body,timeout):
        raise TimeoutError()
    assert not semantic(AI,'synthetic-key',transport=offline)['available']
    assert not semantic(AI)['available']

def test_ui_and_untrusted_input(client):
    assert client.get('/').status_code==200
    assert client.get('/static/app.js').status_code==200
    item=submit(client,'<script>alert(1)</script> '+HUMAN).json
    assert '<script>' in item['text']
    # UI uses textContent, never dynamic innerHTML, so source text stays data.
    script=client.get('/static/app.js').text
    assert 'innerHTML' not in script

def test_existing_course_model_request_budget():
    def transport(body, timeout):
        assert body['model']=='openai/gpt-oss-120b'
        assert body['max_completion_tokens']==1600
        assert body['response_format']=={'type':'json_object'}
        return {'choices':[{'message':{'content':json.dumps({'ai_score':.5,'explanation':'Synthetic request-contract test'})}}]}
    assert semantic(AI,'synthetic-key',transport=transport)['available']
