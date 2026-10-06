# Provenance Guard

A local attribution-analysis API and review interface for AI201 Project 4.

**Status: implemented and locally verified AI-assisted course project; course submission pending.**
Codex created the plan, code, tests and technical documentation from the authenticated
course rubric. On October 6, Aamori clarified that her professor said AI could complete
the rest and that the online outline was not current. That updated user-reported guidance
supersedes the older outline for this task. AI assistance is disclosed; no personal
experience, student review, or student-authored reflection is invented. Nothing has
been pushed, published, deployed or submitted.

## Run locally

Python 3.13 was used for verification. Python 3.11+ is expected but not separately tested.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5054**. The server binds only to loopback and uses an ignored
SQLite database, `provenance.sqlite3`. No credentials are required for offline mode. To use an existing course environment
without copying its key into this repo:

```sh
python run.py --existing-env /absolute/path/to/your/existing/course/.env
```

This reads the key into memory and sends submitted prose to Groq. Use the same existing
account as your earlier projects. The current local preview was started this way.
`requirements-lock.txt` records the full tested dependency set.

```sh
python -m pytest -q
python generate_evidence.py
```

Verification: **41 tests passed**. See [test output](evidence/test-results.txt),
[reproducible examples](evidence/examples.json), [audit sample](evidence/audit-sample.json),
[rate-limit evidence](evidence/rate-limit.json), and [verification notes](docs/VERIFICATION.md).

## Architecture

A request reaches Flask's IP rate limiter, JSON/schema validation and normalization.
Standalone signals measure text structure, lexical evidence, and optionally semantic
origin cues. Structured metadata adds a creation-process signal. The ensemble normalizes
available weights, damps disagreement and applies abstention rules. Label generation
maps the result to plain language. One SQLite transaction stores the decision and audit
event before returning JSON. Appeals append an event and change status without changing
the original attribution. See the diagram in [planning.md](planning.md#architecture).

| Endpoint | Input / response |
|---|---|
| `POST /submit` | `creator_id`, `text`; returns content ID, attribution, confidence, AI evidence index, label, individual scores and normalized weights |
| `POST /submit` metadata mode | `creator_id`, `content_type: "metadata"`, typed `metadata` object; same attribution response |
| `GET /content/<id>` | Stored content, status, original decision and optional certificate |
| `POST /appeal` | `content_id`, `creator_reasoning` (10–3000 chars); returns `under_review` |
| `GET /appeals` | Open appeals with content, signals, original result and creator reasoning |
| `GET /log` | Latest 100 structured audit events |
| `POST /verification/request` | Content ID, distinct earlier draft (20+ chars), process explanation (40+ chars) |
| `GET /verification` | Local review queue |
| `POST /verification/review` | Verification ID, reviewer name, notes (20+ chars), boolean `approved` |
| `GET /analytics` | Verdict distribution, appeal rate, mean confidence, verified count |
| `GET /health` | Mode, configured model and submission limits |

Example:

```sh
curl -s http://127.0.0.1:5054/submit \
  -H 'Content-Type: application/json' \
  -d '{"creator_id":"demo","text":"A short poem about the moon."}'
```

Short text deliberately returns `uncertain`. Use the interface's **Load sample** button
for a longer example. Select **Structured creative-work metadata**, **Human**, then
**Analyze work** to inspect the offline three-signal path.

## Detection signals and blind spots

| Signal | Weight | What it measures / why used | What it misses |
|---|---:|---|---|
| Semantic assessment (optional Groq) | 0.55 | Holistic language coherence, generic explanations and personal grounding; distinct from numerical structure | Prompt injection, edited AI prose, genre and language bias; does not prove authorship |
| Stylometry | 0.25 | Sentence-length coefficient of variation, vocabulary diversity and punctuation density; directly inspectable structural measurements | Humans also write uniformly, and models can imitate irregularity |
| Lexical evidence | 0.20 | Explicit AI disclosures, formal transitions and conversational expressions; measures vocabulary content rather than sentence geometry | Quoted disclosures can falsely trigger; formal human prose and slangy AI prose can mislead |
| Process declaration (metadata only) | 0.35 | Declared creation method and named AI tools; supplies provenance context not present in prose | Self-reports can be dishonest; this is not authenticated provenance |

The first three form the text ensemble when Groq is available. Offline metadata has
three **available** signals: stylometry, lexical evidence and process declaration.
Offline plain text has two available signals and abstains conservatively.

### Semantic service: resolved and verified live

The original handwritten `urllib` client returned HTTP 403 / `error code: 1010`.
Aamori specifically directed a comparison with earlier course projects. Projects 1/2
use the official `groq==0.15.0` SDK with `httpx==0.28.1`, ordinary transport defaults,
and `openai/gpt-oss-120b`. Their documentation also records empty reasoning-model
responses at small token budgets. Project 4 now uses that same SDK and model with
`max_completion_tokens=1600`. No custom identity headers, proxies, TLS changes,
new credentials or account permissions were introduced.

The ordinary SDK successfully listed the model and completed five real classifications
through `POST /submit`. All three **plain-text** labels were reached. See
[live-model.json](evidence/live-model.json), [initial failure evidence](evidence/initial-urllib-failure.json),
and [client comparison](docs/GROQ_DIAGNOSTIC.md). The Mac browser also displayed a real
semantic score of 0.08 and a likely-human label at 0.8313 confidence for the course's
ramen example. The original transport failure is resolved in the tested SDK path;
this does not establish that every client/network will work.

Set `GROQ_API_KEY` in an ignored `.env`, export it, or use `run.py --existing-env`.
`GROQ_MODEL` can override the default. Provider outages, invalid responses and missing
credentials remain explicit unavailable signals; no mock prediction is substituted.
The adapter is tested against invalid types, NaN, booleans, out-of-range scores and
timeouts. No key is committed or copied from earlier projects.

## Confidence scoring and validation

Every signal emits an AI evidence index in `[0,1]`. Available weights are renormalized;
weighted scores are averaged. A spread above 0.55 shrinks the result 35% toward 0.5.
Fewer than three available signals, fewer than 30 English word tokens, or predominantly
non-ASCII letters force abstention. `ai_score >= 0.80` maps to likely AI; `<= 0.25` maps
to likely human; intermediate evidence maps to uncertain. The higher AI threshold is
intentional: falsely accusing a human is especially harmful.

`confidence = max(ai_score, 1-ai_score)` measures strength in the indicated direction;
uncertain cases cap it at 0.69. It is **not an empirically calibrated probability**.
An AI evidence score of 0.60 is uncertain, while 0.95 can produce likely AI only when
sufficient evidence is available. Tests cover exact thresholds and disagreement.

The four course examples were tested: generic AI prose, an informal ramen review,
formal monetary-policy writing, and lightly edited remote-work prose. Plain text in
offline mode correctly communicates insufficient evidence. The following actual
metadata submissions show all three labels (complete inputs and outputs in the
[evidence file](evidence/examples.json)):

| Submission | Declaration | AI index | Confidence | Result |
|---|---|---:|---:|---|
| “Artificial intelligence represents a transformative paradigm shift…” (full course example) | AI | 0.8042 | 0.8042 | likely_ai |
| “ok so i finally tried that new ramen place downtown and honestly? underwhelming…” (full course example) | Human | 0.1909 | 0.8091 | likely_human |
| “The relationship between monetary policy and asset price inflation…” (formal borderline example) | Unknown | 0.5331 | 0.5331 | uncertain |

The live plain-text API now adds independently recorded results:

| Actual text submission | AI evidence index | Confidence | Result |
|---|---:|---:|---|
| Explicit AI disclosure (Codex-generated positive control) | 0.8817 | 0.8817 | likely_ai |
| Course informal ramen review | 0.1688 | 0.8313 | likely_human |
| Course formal monetary-policy prose | 0.5540 | 0.5540 | uncertain |
| Course generic AI example | 0.7399 | 0.6900 | uncertain |
| Course lightly edited AI example | 0.3395 | 0.6605 | uncertain |

The generic AI sample failing to reach the AI cutoff is an honest false-negative/
abstention limitation. No thresholds were changed to force this example into a label.
The explicit disclosure control tests a clear positive route; it is not representative
of undisclosed AI writing. Semantic explanations and individual scores are saved.

These examples validate variation and engineering behavior, **not predictive accuracy**:
the declarations influence the result, and the sample set is tiny. A real deployment
would need a consented, genre-diverse holdout set with known provenance, false-positive
measurement by group and genre, and calibration assessed on unseen data.

## Exact transparency labels

| Case | Verbatim label |
|---|---|
| High-confidence AI | This work shows strong signs of AI generation. This assessment can be wrong; the creator can request a review. |
| High-confidence human | This work shows strong signs of human writing. This is an estimate, not proof of authorship. |
| Uncertain | We cannot confidently tell how this work was made. Please do not treat this assessment as proof of AI use. |

The detector never claims certainty or automatically punishes a creator. These labels
are also written in `planning.md` and defined in one `LABELS` constant in source.

## Appeals and audit log

Submit reasoning through the UI or `POST /appeal`. The original attribution and scores
remain intact; `status` becomes `under_review`. The event stores reasoning alongside
the original decision. Unknown IDs return 404, blank/short reasoning 400 and duplicate
open appeals 409. A write lock prevents two simultaneous appeals being accepted.

The [committed structured audit sample](evidence/audit-sample.json) contains **10 events**,
including classification, appeal and verification events. Every event has timestamp,
content ID, creator ID, attribution, confidence, AI index, individual signals and status.
Appeal events additionally contain `appeal_reasoning` and `original_decision`.
The original classification is retained as a separate event. The example uses only
synthetic input; certificate approvals in the evidence are explicitly test fixtures.

## Rate limiting

`SUBMISSION_LIMIT = '10 per minute;100 per day'` in `app.py`, per remote IP with
Flask-Limiter's `memory://` storage. Ten/minute allows editing experiments but blocks
bursts; 100/day allows a writer's repeated drafts while limiting an automated flood.
Changing `creator_id` cannot reset the IP limit. No untrusted forwarded IP header is used.
Twelve consecutive requests produced:

```text
200 200 200 200 200 200 200 200 200 200 429 429
```

The 429 response is JSON with a retry header. See [recorded output](evidence/rate-limit.json).
Memory storage is suitable only for this single-process local demo: restart resets
limits; multiple workers would need shared storage such as Redis. IP-based limits can
unfairly group users behind NAT, so authenticated account limits would be preferable
for a real platform. Payloads are bounded to 64 KB and text to 10,000 characters.

## All four stretch features

1. **Ensemble (+1):** independently visible structural, lexical and process signals
   run offline for metadata; optional semantic signal provides the third text signal.
   The table documents weighting; normalized weights and conflict damping are returned.
2. **Provenance certificate (+1):** the creator provides a distinct earlier draft and
   process explanation; a reviewer explicitly approves or rejects. The credential is
   bound to the exact content hash and appears separately from the attribution label:
   **Verified human — draft/process reviewed (demo credential; not proof).** Approval
   does not change the statistical decision. The workflow is functional, but local
   reviewer names are not authenticated and test approvals are not real verification.
3. **Analytics (+1):** the dashboard shows detection counts, appeal rate (unique appealed
   content / submissions), mean confidence and verified count. Audit events do not inflate
   submission totals. Empty-state division and duplicate appeals are tested.
4. **Multi-modal support (+1):** structured metadata is a separate validated JSON content
   type with title, description, declared creation method, tools and revision list.
   Description enters text signals; creation method/tools enter process provenance.
   This is the assignment's structured-metadata option, not image-pixel classification.

Example metadata contract:

```json
{"creator_id":"demo","content_type":"metadata","metadata":{"title":"Evening notes","description":"A sufficiently long description of the creative work goes here…","creation_method":"human","tools":["notebook"],"revisions":["An earlier draft…"]}}
```

## Known limitations

* A formal essay by a non-native English speaker may trigger regularity and formal
  transitions. A poem with repeated lines can also look uniform. Neither proves AI use.
* A model can imitate informal language; the lexical signal can then lean human.
* Quoting “as an AI” can trigger the disclosure marker even in human criticism of AI.
* Metadata can be forged. High confidence based partly on a declaration should never
  be interpreted as independent provenance verification.
* No calibrated accuracy claim is supported. Five live examples and four offline
  examples are functional demonstrations, not a scientific evaluation.
* The app has no account or reviewer authentication. All local users can read logs and
  use reviewer controls. It binds to loopback; **do not deploy it as a public service**
  without authentication, authorization, privacy controls, a shared rate-limit store,
  and a real verification program. Appeals do not yet have a resolution endpoint.
* Persistence is SQLite on one machine. Audit events are append-only through this API,
  not cryptographically tamper-proof against someone with database access.

## Spec reflection and actual revisions

The pre-implementation spec made the uncertainty ranges, plain-language labels and
atomic appeal/log update explicit, which gave the tests concrete acceptance criteria.
During testing, adding metadata's title to the analyzed prose changed sentence variance
enough to move the AI example below the intended threshold. The implementation was
revised to analyze only the description, while retaining the title in stored metadata.
This is a real divergence from the initial normalization design, recorded after the
first test failure. Browser testing also found that generic button cleanup re-enabled
the appeal button after an appeal; it now stays disabled when status is under review.

## AI usage disclosure — actual directions and revisions

Aamori asked Codex to identify the overdue assignment and prepare all required and
stretch functionality. **Codex authored the reference plan, code, tests and this
technical documentation.** The following describe actual tool work, not decisions
claimed to have been made by Aamori:

1. Codex used the portal's detection/scoring requirements and the written architecture
   plan to generate standalone signal functions and the Flask API. Its generated
   normalization initially mixed a title into prose. The failing API tests led Codex
   to revise that behavior and retain titles only as metadata.
2. Codex used the appeals/label spec to implement persistence and the UI. Browser
   verification found an appeal-button state problem; Codex revised cleanup logic.
   It also kept certificate badges independent of attribution and labeled synthetic
   approvals honestly, rather than claiming a human had reviewed them.
3. Aamori then specifically directed Codex to inspect how earlier projects handled
   Groq and clarified her professor's current permission for AI to finish the work.
   The previous model-only comparison was insufficient. Comparing the actual SDK,
   transport and dependencies led to replacing the handwritten `urllib` client with
   the earlier projects' official SDK setup. Five real API responses and a live
   browser result verified the fix; the initial failed results were retained.

These entries disclose who did what. They do not claim Aamori personally reviewed
code or recorded experiences she has not reported. A final review checklist is provided
in [STUDENT_REVIEW.md](docs/STUDENT_REVIEW.md); add personal reflections only if true.

## Submission preparation

[Exact rubric coverage](docs/RUBRIC_CHECKLIST.md) · [Course findings](docs/COURSE_FINDINGS.md)
· [Walkthrough outline](demo/WALKTHROUGH.md).

The [AI-narrated technical demo](https://drive.google.com/file/d/1em6m3QMpger95qRKBHb0nO-HF9Qmv8DB/view) replays actual recorded
API evidence and explains design decisions. It is clearly labeled synthetic narration,
not Aamori's voice or a claimed live screen recording. Its [transcript](demo/NARRATION.md)
is included. The video is stored on Google Drive rather than in Git history. **Drive access is currently restricted to its owner; reviewer access is pending sharing approval.** A personal walkthrough outline is also available if the instructor expects
Aamori on camera or narrating; that expectation has not been separately confirmed.

Public repository: https://github.com/aamorifreeman/ai201-project4-provenance-guard.
Course submission remains on hold until separately authorized. The Howard Canvas
assignment links to the same CodePath project. Late-credit eligibility is unconfirmed.
