"""Render an explicitly AI-narrated walkthrough of recorded, real API evidence.
No personal voice, experiences, browser recordings, or live interactions are fabricated.
Requires locally available Pillow, ffmpeg, ffprobe and macOS say; not app dependencies.
"""
from pathlib import Path
import json,subprocess,textwrap
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'demo'
WORK=OUT/'render'
WORK.mkdir(exist_ok=True)
live=json.loads((ROOT/'evidence/live-model.json').read_text())
by_name={x['name']:x['response'] for x in live['examples']}
proof=json.loads((ROOT/'evidence/examples.json').read_text())
rate=json.loads((ROOT/'evidence/rate-limit.json').read_text())
scenes=[
('Provenance Guard', ['AI201 Project 4 · Technical walkthrough','Text attribution → uncertainty labels → creator review','AI-generated narration · Replay of recorded API evidence','All test examples are synthetic or course-provided.'],
 'This is an AI-narrated technical walkthrough of Provenance Guard. It replays recorded API evidence, not a fabricated live screen recording. The system analyzes creative text, communicates uncertainty, and gives creators a path to appeal. No detector score proves authorship.'),
('Three signals, one cautious result', ['Semantic assessment: 55%','Structural stylometry: 25%','Lexical evidence: 20%','Conflicting signals are pulled toward uncertainty.','AI threshold: 0.80 · Human threshold: 0.25'],
 'A text submission passes through three signals: semantic assessment, structural stylometry, and lexical evidence. Their weights are fifty-five, twenty-five, and twenty percent. Strong disagreement pulls the result toward uncertainty. Short text, unsupported language, or missing evidence triggers abstention.'),
('Actual live text results', [f"AI-disclosed control: {by_name['explicit_ai_disclosure']['attribution']} · {by_name['explicit_ai_disclosure']['confidence']:.4f}",f"Informal review: {by_name['course_human']['attribution']} · {by_name['course_human']['confidence']:.4f}",f"Formal borderline: {by_name['formal_borderline']['attribution']} · {by_name['formal_borderline']['confidence']:.4f}",f"Generic AI example: uncertain · AI index {by_name['course_ai']['ai_score']:.4f}",'Real Groq responses through POST /submit, saved as JSON.'],
 'Actual live submissions reached all three labels. The explicitly AI-disclosed positive control scored point eight eight one seven. The informal review received a human label at point eight three one three confidence. Formal prose stayed uncertain. The generic AI example also stayed uncertain, showing why style is not proof.'),
('Appeal without rewriting history', ['POST /appeal + creator_reasoning','status: classified → under_review','Original classification and signal scores remain unchanged.','New audit event stores reasoning and original_decision.','Duplicate open appeals: HTTP 409'],
 'An appeal records the creator’s reasoning and changes the content status to under review. The original decision stays intact. A separate structured audit event links the explanation to that decision. Duplicate open appeals are rejected, and the tests also check concurrent requests and database persistence.'),
('All four stretch features', ['Ensemble: individual scores + normalized weights','Certificate: distinct draft + process explanation + review','Analytics: verdicts, appeal rate, mean confidence','Second content type: validated structured metadata','Verified badge stays separate from the detector label.'],
 'The four stretch features are implemented. The ensemble exposes its individual scores. A draft and process review can issue a content-bound certificate, separate from the detector label. Analytics reports verdict patterns, appeal rate, and mean confidence. Structured metadata adds a creation-process signal. Demonstration approvals are clearly marked synthetic.'),
('Safety and verification', ['Submission limit: 10/minute and 100/day per IP','12 requests: '+ ' '.join(str(x) for x in rate['codes']), '41 automated tests passed','Real browser: classification, appeal, certificate, analytics','Loopback only · reviewer names are not authentication'],
 'Rate limiting permits ten submissions per minute and one hundred per day. Twelve consecutive requests produced ten successful responses and two rate-limit errors. Forty-one automated tests passed. Browser checks covered classification, appeals, certificates, and analytics. This local prototype still needs real authentication before any public deployment.'),
('What changed and what remains', ['Resolved: custom urllib client → official Groq SDK','Matched prior projects: Groq 0.15.0 + httpx 0.28.1','Model: openai/gpt-oss-120b · 1600-token output budget','No spoofing, proxy workaround, or new credentials','Next: review deliverables and approve publication/submission'],
 'The initial custom HTTP client failed. Comparing prior course projects identified the ordinary official Groq SDK and a larger reasoning-token budget. That setup restored real inference without a proxy or identity workaround. The README records the changes, limitations, and AI assistance. Publication and final submission still require approval.')]
fonts={s:ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',s) for s in [20,26,30,54]}
segments=[]
script=[]
for i,(title,lines,narration) in enumerate(scenes):
 image=Image.new('RGB',(1280,720),'#f1f2ec');draw=ImageDraw.Draw(image)
 draw.rectangle((0,0,1280,12),fill='#173f38')
 draw.text((72,48),'AI201  /  PROJECT 04  /  RECORDED EVIDENCE',font=fonts[20],fill='#5b7566')
 draw.text((72,105),title,font=fonts[54],fill='#173f38')
 y=215
 for line in lines:
  for wrapped in textwrap.wrap(line,76):
   draw.text((80,y),wrapped,font=fonts[26],fill='#223e36');y+=40
  y+=14
 draw.line((72,640,1208,640),fill='#bacabc',width=2)
 draw.text((72,665),'AI-generated narration · No personal authorship or real verification claimed',font=fonts[20],fill='#5b7566')
 draw.text((1120,665),f'{i+1} / {len(scenes)}',font=fonts[20],fill='#5b7566')
 png=WORK/f'{i:02d}.png';audio=WORK/f'{i:02d}.aiff';mp4=WORK/f'{i:02d}.mp4'
 image.save(png)
 speech=WORK/f'{i:02d}.txt';speech.write_text(narration)
 subprocess.run(['say','-r','170','-f',str(speech),'-o',str(audio)],check=True)
 subprocess.run(['ffmpeg','-loglevel','error','-y','-loop','1','-framerate','15','-i',str(png),'-i',str(audio),'-c:v','libx264','-preset','fast','-tune','stillimage','-pix_fmt','yuv420p','-af','apad=pad_dur=0.6','-c:a','aac','-ar','44100','-ac','1','-shortest',str(mp4)],check=True)
 segments.append(mp4);script.append(f'## {i+1}. {title}\n\n{narration}\n')
playlist=WORK/'concat.txt';playlist.write_text(''.join("file '"+str(x)+"'\n" for x in segments))
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',str(playlist),'-c','copy','-movflags','+faststart',str(OUT/'provenance-guard-demo.mp4')],check=True)
(OUT/'NARRATION.md').write_text('# AI-narrated technical walkthrough\n\nThis replays actual recorded API evidence; it is not Aamori’s voice or personal reflection.\n\n'+'\n'.join(script))
print(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-of','json',str(OUT/'provenance-guard-demo.mp4')],text=True))
