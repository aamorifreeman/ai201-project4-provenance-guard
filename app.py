"""Loopback-only teaching application; not a multi-user production service."""
import hashlib
import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import HTTPException

from detection import analyze

BADGE = 'Verified human — draft/process reviewed (demo credential; not proof).'

def now():
    return datetime.now(timezone.utc).isoformat()

def create_app(config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.update(DATABASE=str(Path(__file__).parent/'provenance.sqlite3'),
        MAX_CONTENT_LENGTH=65536, GROQ_API_KEY=os.getenv('GROQ_API_KEY',''),
        GROQ_MODEL=os.getenv('GROQ_MODEL','openai/gpt-oss-120b'),
        SUBMISSION_LIMIT='10 per minute;100 per day', RATELIMIT_HEADERS_ENABLED=True)
    if config:
        app.config.update(config)
    @contextmanager
    def db():
        connection = sqlite3.connect(app.config['DATABASE'], timeout=10)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()
    with db() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS content(id TEXT PRIMARY KEY, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS verification(id TEXT PRIMARY KEY, body TEXT NOT NULL);
        ''')
    limiter = Limiter(get_remote_address, app=app, default_limits=[], storage_uri='memory://')
    app.extensions['project_limiter'] = limiter

    def fail(message, status=400):
        from werkzeug.exceptions import BadRequest
        if status == 400:
            raise BadRequest(message)
        error = HTTPException(message)
        error.code = status
        raise error

    def payload():
        if not request.is_json:
            fail('Send Content-Type: application/json.',415)
        data = request.get_json()
        if not isinstance(data,dict):
            fail('The JSON body must be an object.')
        return data

    def string(data, key, minimum=1, maximum=10000):
        value = data.get(key)
        if not isinstance(value,str) or not minimum <= len(value.strip()) <= maximum:
            fail(f'{key} must be a string of {minimum}–{maximum} non-blank characters.')
        return value.strip()

    def get_content(con, content_id):
        row = con.execute('SELECT body FROM content WHERE id=?',(content_id,)).fetchone()
        if not row:
            fail('Content not found.',404)
        return json.loads(row['body'])

    def save_content(con, item):
        con.execute('INSERT OR REPLACE INTO content VALUES (?,?)',(item['content_id'],json.dumps(item)))

    def audit(con, item, event, **extra):
        entry = {key:item[key] for key in ('content_id','creator_id','attribution','confidence','ai_score','label','signals','status')}
        entry.update(event=event,timestamp=now(),appeal_reasoning=item.get('appeal_reasoning'),**extra)
        con.execute('INSERT INTO audit(body) VALUES (?)',(json.dumps(entry),))

    @app.errorhandler(HTTPException)
    def http_error(error):
        response = jsonify(error=error.description, status=error.code)
        response.status_code = error.code
        return response

    @app.get('/')
    def index():
        return render_template('index.html', badge=BADGE)

    @app.get('/health')
    def health():
        return jsonify(status='ok',mode='groq' if app.config['GROQ_API_KEY'] else 'offline',
                       model=app.config['GROQ_MODEL'], submission_limit=app.config['SUBMISSION_LIMIT'])

    @app.post('/submit')
    @limiter.limit(lambda: app.config['SUBMISSION_LIMIT'])
    def submit():
        data = payload()
        creator = string(data,'creator_id',maximum=100)
        kind = data.get('content_type','text')
        metadata = None
        if kind == 'text':
            text = string(data,'text')
        elif kind == 'metadata':
            metadata = data.get('metadata')
            if not isinstance(metadata,dict):
                fail('metadata must be a JSON object.')
            title = string(metadata,'title',maximum=200)
            description = string(metadata,'description',maximum=10000)
            method = metadata.get('creation_method')
            if method not in ('human','ai','assisted','unknown'):
                fail('creation_method must be human, ai, assisted, or unknown.')
            for field, count, size in [('tools',20,100),('revisions',10,10000)]:
                value = metadata.get(field,[])
                if not isinstance(value,list) or len(value)>count or any(not isinstance(v,str) or not v.strip() or len(v)>size for v in value):
                    fail(f'{field} must contain at most {count} non-blank strings, each at most {size} characters.')
            metadata = dict(title=title,description=description,creation_method=method,
                            tools=metadata.get('tools',[]),revisions=metadata.get('revisions',[]))
            # Titles are labels, not prose; including them distorts sentence variance.
            text = description
        else:
            fail('content_type must be text or metadata.')
        analyzer = app.config.get('ANALYZER', analyze)
        result = analyzer(text, metadata, app.config['GROQ_API_KEY'], app.config['GROQ_MODEL'])
        digest = hashlib.sha256(json.dumps({'type':kind,'text':text,'metadata':metadata},sort_keys=True).encode()).hexdigest()
        item = dict(result,content_id=str(uuid.uuid4()),creator_id=creator,content_type=kind,
                    text=text,metadata=metadata,content_hash=digest,status='classified',
                    timestamp=now(),appeal_reasoning=None,certificate=None)
        with db() as con:
            save_content(con,item)
            audit(con,item,'classification')
        return jsonify(item),200

    @app.get('/content/<content_id>')
    def content(content_id):
        with db() as con:
            return jsonify(get_content(con,content_id))

    @app.post('/appeal')
    def appeal():
        data=payload()
        content_id=string(data,'content_id',maximum=100)
        reasoning=string(data,'creator_reasoning',minimum=10,maximum=3000)
        with db() as con:
            # Acquire write lock before reading to prevent concurrent duplicate appeals.
            con.execute('BEGIN IMMEDIATE')
            item=get_content(con,content_id)
            if item['status']=='under_review':
                fail('This content already has an open appeal.',409)
            item.update(status='under_review',appeal_reasoning=reasoning)
            save_content(con,item)
            audit(con,item,'appeal',original_decision=dict(attribution=item['attribution'],confidence=item['confidence'],ai_score=item['ai_score']))
        return jsonify(content_id=content_id,status='under_review',message='Appeal received; original decision preserved.'),200

    @app.get('/log')
    def log():
        with db() as con:
            entries=[dict(json.loads(row['body']),event_id=row['id']) for row in con.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 100')]
        return jsonify(entries=entries)

    @app.get('/appeals')
    def appeals():
        with db() as con:
            items=[json.loads(row['body']) for row in con.execute('SELECT body FROM content')]
        return jsonify(entries=[item for item in items if item['status']=='under_review'])

    @app.post('/verification/request')
    def verification_request():
        data=payload()
        content_id=string(data,'content_id',maximum=100)
        draft=string(data,'earlier_draft',minimum=20)
        process=string(data,'process_explanation',minimum=40,maximum=3000)
        with db() as con:
            con.execute('BEGIN IMMEDIATE')
            item=get_content(con,content_id)
            if draft.strip()==item['text'].strip():
                fail('Provide a distinct earlier draft, not the final content.')
            for row in con.execute('SELECT body FROM verification'):
                prior=json.loads(row['body'])
                if prior['content_id']==content_id and prior['status']=='pending':
                    fail('A verification request is already pending.',409)
            if item['certificate']:
                fail('This content already has a certificate.',409)
            review=dict(verification_id=str(uuid.uuid4()),content_id=content_id,content_hash=item['content_hash'],
                        earlier_draft=draft,process_explanation=process,status='pending',timestamp=now())
            con.execute('INSERT INTO verification VALUES (?,?)',(review['verification_id'],json.dumps(review)))
            audit(con,item,'verification_requested',verification_id=review['verification_id'])
        return jsonify(review),201

    @app.get('/verification')
    def verification_queue():
        with db() as con:
            return jsonify(entries=[json.loads(row['body']) for row in con.execute('SELECT body FROM verification')])

    @app.post('/verification/review')
    def verification_review():
        data=payload()
        review_id=string(data,'verification_id',maximum=100)
        reviewer=string(data,'reviewer',minimum=2,maximum=100)
        notes=string(data,'review_notes',minimum=20,maximum=3000)
        approved=data.get('approved')
        if not isinstance(approved,bool):
            fail('approved must be a JSON boolean.')
        with db() as con:
            con.execute('BEGIN IMMEDIATE')
            row=con.execute('SELECT body FROM verification WHERE id=?',(review_id,)).fetchone()
            if not row:
                fail('Verification request not found.',404)
            review=json.loads(row['body'])
            if review['status']!='pending':
                fail('This request has already been reviewed.',409)
            item=get_content(con,review['content_id'])
            review.update(status='approved' if approved else 'rejected',reviewer=reviewer,review_notes=notes,reviewed_at=now())
            con.execute('UPDATE verification SET body=? WHERE id=?',(json.dumps(review),review_id))
            if approved:
                item['certificate']=dict(certificate_id=str(uuid.uuid4()),content_hash=item['content_hash'],
                    label=BADGE,reviewer=reviewer,issued_at=now(),scope='Local demonstration; draft/process review only')
                save_content(con,item)
            audit(con,item,'verification_reviewed',verification_id=review_id,approved=approved,reviewer=reviewer,review_notes=notes)
        return jsonify(review=review,certificate=item['certificate'])

    @app.get('/analytics')
    def analytics():
        with db() as con:
            items=[json.loads(row['body']) for row in con.execute('SELECT body FROM content')]
        total=len(items)
        counts={label:sum(item['attribution']==label for item in items) for label in ('likely_ai','likely_human','uncertain')}
        return jsonify(total_submissions=total,detection_patterns=counts,
            appeal_rate=round(sum(i['status']=='under_review' for i in items)/total,4) if total else 0,
            mean_confidence=round(sum(i['confidence'] for i in items)/total,4) if total else 0,
            verified_count=sum(bool(i['certificate']) for i in items))
    return app

if __name__ == '__main__':
    create_app().run(host='127.0.0.1',port=5054,debug=False)
