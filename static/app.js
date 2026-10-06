'use strict';
let current = null;
const $ = id => document.getElementById(id);
const sample = 'ok so i finally tried that new ramen place downtown and honestly? underwhelming. the broth was fine but they put WAY too much sodium in it and i was thirsty for like three hours after. my friend got the spicy version and said it was better. probably won\'t go back unless someone drags me there';
async function api(path, body) {
  const response = await fetch(path, body === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const value = await response.json();
  if (!response.ok) throw new Error(value.error || 'Request failed');
  return value;
}
function text(tag, value, cls) { const el=document.createElement(tag);el.textContent=value;if(cls)el.className=cls;return el; }
async function act(fn, button) {
  $('error').textContent='';if(button)button.disabled=true;
  try { await fn(); } catch(e) {$('error').textContent=e.message;$('error').scrollIntoView({block:'nearest'});}
  finally{if(button)button.disabled=button.form?.id==='appeal-form' && current?.status==='under_review';}
}
function show(item) {
  current=item;$('result').hidden=false;$('empty').hidden=true;
  $('label').textContent=item.label;
  $('score').textContent=`Evidence strength: ${(item.confidence*100).toFixed(1)}% · AI evidence index: ${item.ai_score.toFixed(3)} (not a probability)`;
  $('status').textContent=`Status: ${item.status.replaceAll('_',' ')} · ${item.content_id}`;
  $('badge').hidden=!item.certificate;$('badge').textContent=item.certificate?.label || '';
  $('reasons').replaceChildren(...item.uncertainty_reasons.map(r=>text('li',r)));
  $('signals').replaceChildren(...item.signals.map(s=>{const row=text('div','', 'signal');const name=text('div',s.name);name.append(text('small',`Weight: ${s.normalized_weight} · ${s.available?'available':'unavailable'}`));row.append(name,text('strong',s.score===null?'—':s.score.toFixed(3)));return row;}));
  $('raw').textContent=JSON.stringify(item,null,2);
  $('appeal-form').querySelector('button').disabled=item.status==='under_review';
}
async function refresh() {
  const [stats,log,queue]=await Promise.all([api('/analytics'),api('/log'),api('/verification')]);
  $('total').textContent=stats.total_submissions;$('appeal-rate').textContent=`${(stats.appeal_rate*100).toFixed(1)}%`;
  $('confidence').textContent=`${(stats.mean_confidence*100).toFixed(1)}%`;$('verified').textContent=stats.verified_count;
  $('patterns').textContent=`Detection patterns: ${stats.detection_patterns.likely_ai} likely AI · ${stats.detection_patterns.likely_human} likely human · ${stats.detection_patterns.uncertain} uncertain`;
  $('log').replaceChildren(...log.entries.map(e=>{const row=text('div','', 'event');row.append(text('strong',`${e.event} · ${e.attribution} · confidence ${e.confidence}`),text('p',`${e.timestamp} · ${e.content_id}`,''));if(e.appeal_reasoning)row.append(text('p',`Appeal: ${e.appeal_reasoning}`));return row;}));
  if(!log.entries.length)$('log').append(text('p','No decisions yet. Analyze a work to begin.'));
  $('queue').replaceChildren(...queue.entries.map(v=>{const box=text('div','', 'review');box.append(text('strong',`${v.status} · ${v.content_id}`),text('p',`Earlier draft: ${v.earlier_draft}`),text('p',`Process: ${v.process_explanation}`));
    if(v.status==='pending'){
      const form=document.createElement('form');const reviewer=document.createElement('input');reviewer.placeholder='Reviewer name';reviewer.setAttribute('aria-label','Reviewer name');reviewer.required=true;reviewer.minLength=2;
      const notes=document.createElement('textarea');notes.placeholder='What did you check? (20+ characters)';notes.setAttribute('aria-label','Review notes');notes.required=true;notes.minLength=20;
      const verdict=document.createElement('select');verdict.setAttribute('aria-label','Review decision');for(const [value,label] of [['reject','Reject verification'],['approve','Approve after reviewing draft/process']]){const opt=text('option',label);opt.value=value;verdict.append(opt);}
      const button=text('button','Save local review');form.append(reviewer,notes,verdict,button);form.onsubmit=e=>{e.preventDefault();act(async()=>{await api('/verification/review',{verification_id:v.verification_id,reviewer:reviewer.value,review_notes:notes.value,approved:verdict.value==='approve'});if(current)show(await api('/content/'+current.content_id));await refresh();},button);};box.append(form);
    }return box;}));
  if(!queue.entries.length)$('queue').append(text('p','No verification requests yet.'));
}
$('kind').onchange=()=>{$('metadata-fields').hidden=$('kind').value!=='metadata';};
$('example').onclick=()=>{$('text').value=sample;};
$('submit-form').onsubmit=e=>{e.preventDefault();act(async()=>{const body={creator_id:$('creator').value,content_type:$('kind').value};if(body.content_type==='text')body.text=$('text').value;else body.metadata={title:$('title').value,description:$('text').value,creation_method:$('method').value,tools:$('tools').value.split(',').map(s=>s.trim()).filter(Boolean)};show(await api('/submit',body));await refresh();},e.submitter);};
$('appeal-form').onsubmit=e=>{e.preventDefault();act(async()=>{await api('/appeal',{content_id:current.content_id,creator_reasoning:$('reason').value});show(await api('/content/'+current.content_id));await refresh();},e.submitter);};
$('verification-form').onsubmit=e=>{e.preventDefault();act(async()=>{await api('/verification/request',{content_id:current.content_id,earlier_draft:$('draft').value,process_explanation:$('process').value});await refresh();},e.submitter);};
$('refresh').onclick=()=>act(refresh);act(refresh);
