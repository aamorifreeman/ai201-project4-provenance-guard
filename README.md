# Provenance Guard

A local attribution-analysis API and review interface for AI201 Project 4.

**Status: working AI-assisted reference implementation, not yet submission-ready student work.**
Codex created this implementation from the authenticated course rubric on October 6,
2026. Aamori must review and revise the design and code, document her actual decisions,
and record her own walkthrough. Nothing has been pushed, published, deployed or submitted.
The course [AI Prompting Guide](https://courses.codepath.org/courses/ai201/pages/ai_prompting_guide)
allows AI-generated components but says AI should never “Write your entire assignment
for you.” This reference must not be presented as independently authored student work.

## Run locally

Python 3.13 was used for verification. Python 3.11+ is expected but not separately tested.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5054**. The server binds only to loopback and uses an ignored
SQLite database, `provenance.sqlite3`. No credentials are required for offline mode.
`requirements-lock.txt` records the full tested dependency set.

```sh
python -m pytest -q
python generate_evidence.py
```

Verification: **40 tests passed**. See [test output](evidence/test-results.txt),
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

### Optional semantic service and actual verification result

Set `GROQ_API_KEY` in your own ignored `.env` to enable semantic inference. The configured
model is `llama-3.3-70b-versatile`; `GROQ_MODEL` can override it. No credential is included
in this repo. A read-only check with an existing course key received **HTTP 403** on
October 6, 2026. Therefore live semantic classification is **not verified**. Four attempts
are recorded in [live-model.json](evidence/live-model.json), all explicitly unavailable.
No key was copied into this project and no new credentials were created.

The adapter is tested with synthetic successful and malformed responses, timeouts,
NaN, booleans, invalid types and out-of-range scores. Those are contract tests, not
proof of real model accuracy. A configured key makes submitted prose leave the local
machine for Groq; offline mode makes no external calls.

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
* No calibrated accuracy claim is supported. Four demonstration inputs are not a
  scientific evaluation; the live model was blocked with HTTP 403.
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

## AI usage disclosure — factual, pending student reflection

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
3. Codex tested the optional Groq adapter with an existing key. The provider returned
   HTTP 403. It retained explicit unavailable-signal behavior and reported the failure
   instead of inventing successful semantic results.

**Still required:** Aamori must understand and review the code, make and record her own
substantive decisions, and write her genuine reflection describing what she revised,
overrode or decided differently. Those student-specific rubric points are not complete.
See [STUDENT_REVIEW.md](docs/STUDENT_REVIEW.md). Do not replace this disclosure with a
fictional first-person account.

## Submission preparation

[Exact rubric coverage](docs/RUBRIC_CHECKLIST.md) · [Course findings](docs/COURSE_FINDINGS.md)
· [Walkthrough outline](demo/WALKTHROUGH.md).

No hosted GitHub URL exists yet. After student review, record the required short
walkthrough, resolve late-credit eligibility, and request approval before creating or
pushing a remote repository or submitting its link through Project 4's Show tab.
