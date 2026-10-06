# Provenance Guard — pre-implementation design

Prepared October 6, 2026 by Codex as an AI-assisted reference for Aamori's review.
This is not a claim that Aamori authored or approved these decisions. The course
requires student reasoning and review; record her actual changes before submission.

## Architecture

```text
POST /submit -- validated text or metadata --> normalize
 normalize -- text --> semantic Groq assessment (optional)
 normalize -- text --> structural stylometry
 normalize -- text --> lexical disclosure/register analysis
 normalize -- metadata --> declared creation process (metadata submissions only)
 signals -- scores + availability + weights --> conservative ensemble
 ensemble -- AI evidence score + abstention reasons --> label generator
 label + signals -- atomic decision --> SQLite content + audit event --> JSON

POST /appeal -- content ID + creator reasoning --> validate existing decision
 original decision + reasoning --> SQLite status under_review + audit --> JSON

POST /verification/request -- content ID + draft + process account --> pending review
 POST /verification/review -- review ID + reviewer + verdict --> content-bound badge
 GET /analytics -- aggregate decisions and appeals --> dashboard
```

The submission route validates and normalizes content, collects independently
inspectable signals, and combines available signals conservatively. A SQLite
transaction stores the decision and an immutable structured audit event before
returning the label. Appeals preserve the original decision while changing its
review status and appending a linked event.

## Signals and combination

Each signal returns `score` (0–1 AI evidence), `available`, `weight`, and evidence.
The score is an engineering heuristic, **not a calibrated probability of authorship**.

* Semantic assessment, weight 0.55: optional Groq JSON assessment of holistic
  semantic coherence, generic phrasing, personal grounding and uncertainty.
  It can be fooled by prompts or edited AI text. Timeout, missing credentials,
  unavailable model and invalid scores make it unavailable, never a fake result.
* Structural stylometry, weight 0.25: sentence-length variation, lexical diversity,
  and punctuation density. Regularity can occur in human formal writing, poetry,
  and second-language writing; it cannot establish origin.
* Lexical evidence, weight 0.20: explicit AI disclosures and formal transition
  phrases versus conversational register. This measures actual lexical content,
  unlike structural measurements; quotes and deliberate imitation can fool it.
* Structured metadata adds a process-declaration signal, weight 0.35; other
  weights are renormalized. AI tool names and declared editing process add origin
  context unavailable from prose. These are self-reports, not authenticated proof.

Available weights are renormalized. A signal spread above 0.55 shrinks the score
35% toward 0.5. Text shorter than 30 words, fewer than three available signals,
or all non-ASCII-language tokens abstains regardless of the weighted score.
Without Groq, text-only mode still computes two distinct local signals and
returns uncertainty. Metadata provides a third independent context signal.

## Uncertainty and exact labels

AI evidence >=0.80 gives likely_ai; <=0.25 gives likely_human; intermediate
scores or mandatory abstention give uncertain. The higher AI cutoff reflects the
greater cost of falsely accusing a human. `confidence` is evidence strength in
the chosen direction (`max(score, 1-score)`); uncertainty is always explicit and
confidence is capped at 0.69 for abstentions. `ai_score` always retains direction.
0.60 AI evidence is uncertain; 0.95 AI evidence can be likely_ai if evidence is
adequate. No empirical calibration claim will be made from four examples.

| Result | Exact text |
|---|---|
| likely_ai | This work shows strong signs of AI generation. This assessment can be wrong; the creator can request a review. |
| likely_human | This work shows strong signs of human writing. This is an estimate, not proof of authorship. |
| uncertain | We cannot confidently tell how this work was made. Please do not treat this assessment as proof of AI use. |

## API contracts and appeals

POST /submit accepts creator_id and text, or content_type=metadata and a metadata
object with title, description, creation_method (human/ai/assisted/unknown), tools
(string list), and optional revisions (up to 10 strings). Return content_id,
attribution, confidence, ai_score, label, status, signals, and abstention reasons.
POST /appeal accepts content_id and creator_reasoning. Missing content is 404,
blank reasoning 400, duplicate open appeal 409. It stores reasoning and original
decision in the audit log; GET /content/<id> and GET /appeals show review status.
This loopback-only teaching app treats creator_id as a display identifier, not
authentication. Authentication and reviewer authorization are required before
any real deployment. No external sharing is enabled.

## Anticipated edge cases

1. Repetitive poems may look machine-written statistically: short-text abstention
   and the appeals route protect against forced binary output.
2. Formal second-language prose may trigger lexical formality: the structural
   signal cannot prove origin; disagreement is damped and uncertain results remain.
3. AI output edited to include slang may evade both local signals. Report this
   limitation and show scores rather than claiming detection accuracy.
4. Quotes containing “as an AI” can trigger the disclosure signal incorrectly.
5. Missing Groq key or malformed model JSON: local signals still work, text mode
   abstains; surface unavailability and never log submitted secrets.
6. Forged metadata or fabricated drafts can fool self-reported provenance. A
   reviewer must approve a certificate; label its exact limited scope.

## Safety infrastructure

Flask-Limiter: 10 submissions/minute and 100/day per remote IP, memory storage
for one local process. Ten/minute permits interactive editing while curbing
bursts; 100/day permits sustained drafting but limits automated flooding.
No trusting arbitrary X-Forwarded-For. Limit body to 64 KB, text to 10,000 chars.
SQLite transactions must atomically save content/status plus audit event.
GET /log returns structured events including original scores on appeal entries.
Database is ignored by Git; only synthetic demonstration evidence is committed.

## AI Tool Plan

* M3: provide Signals, API contracts, Architecture to Codex; generate Flask app
  factory and standalone signals; verify valid/invalid payloads and signal ranges.
* M4: provide Signals, Uncertainty, Architecture; generate combination logic;
  verify boundary values, disagreement, short text, unavailable model, and four
  course examples. Never label mock responses as live model validation.
* M5: provide Labels, Appeals, Safety, Architecture; implement persistence,
  appeals, logs and limiter; verify all labels, appeal linkage, rollback behavior,
  and actual 429 responses.

## Stretch plan — recorded before implementation

1. Ensemble: three text signals when Groq is configured, three offline metadata
   signals; record every score and normalized weight, damp conflicts as above.
2. Certificate: additional earlier draft + 40-character process explanation,
   followed by explicit local human reviewer approval. Certificate binds to the
   content's SHA-256 and is visibly distinct: “Verified human — draft/process
   reviewed (demo credential; not proof).” Never auto-approve based on detector.
3. Dashboard: verdict counts, fraction of content appealed, mean confidence,
   verified count. Use textContent/Jinja escaping for untrusted content.
4. Metadata: actual JSON object normalization and process signal; do not just
   rename prose as a new modality. Document that no image pixels are analyzed.

## Verification and planned delivery

Use pytest for API lifecycle, persistence, input failures, scoring and limiter.
Generate reproducible JSON evidence with synthetic input only. Exercise the UI
in the user's Mac browser. README must link evidence and exact labels, explain
limitations, and disclose AI authorship honestly. Prepare a short demo outline.
Do not submit/publish/push/deploy. Aamori must review, revise, and record her own
walkthrough and genuine AI collaboration reflection before submitting.

## Implementation review — recorded after testing

The first integration tests exposed that including a metadata title in prose changes
sentence-length variance and can alter the label. Normalization now sends only the
metadata description to the text signals, retaining title in the metadata record.
The optional live Groq check returned HTTP 403; no successful model result is claimed.
The original offline abstention design remains in force. See README for the test and
browser findings and for the student review work still needed.
