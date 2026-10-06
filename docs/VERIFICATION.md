# Verification record — final technical state

October 6, 2026 · user's Mac · Python 3.13.7.

* **41 automated tests passed** after the SDK fix. Scope: three offline metadata
  labels; four text examples; score boundaries; disagreement; short/non-English input;
  malformed/types/size validation; appeals, duplicate/concurrent handling and original
  decision preservation; persistence; real 429s/headers; certificate review and rejection;
  content hash binding; analytics; model JSON validation/timeouts; SDK request contract.
* `generate_evidence.py`: seven decisions, one appeal and two verification events,
  all synthetic. Rate evidence: ten 200s then two 429s. Certificate approvals in
  evidence are explicitly test fixtures, not actual human authorship verification.
* **Five real Groq calls through POST /submit succeeded**, using Groq 0.15.0 +
  httpx 0.28.1 with ordinary defaults, existing key, openai/gpt-oss-120b and a 1600-token
  budget. All three text labels were reached: AI control 0.8817, human review 0.8313,
  formal borderline uncertain 0.5540. Individual scores and responses are recorded.
* **Mac Chrome browser live inference passed:** the course review returned semantic
  score 0.08, likely_human confidence 0.8313 and all three signals available. Earlier
  browser checks also verified metadata, appeals/status/audit linkage, certificate
  request/approval/badge, and dashboard updates. No external site was changed.
* The initial urllib failure (403/1010) and model-only attempt are retained separately.
  Comparing the actual client/dependencies to prior projects identified the ordinary
  official SDK configuration that worked. No header spoofing, proxy/identity switch,
  TLS bypass, new credential, permission change or paid-plan setup was used.
* Other real fixes: title removed from prose statistics after two failed integration
  tests; appeal button remains disabled after an appeal; invalid provider output is
  unavailable rather than converted into a fake prediction.

No scientific calibration/accuracy claim is made. Generic AI prose stayed uncertain
and lightly edited AI text leaned toward human evidence, demonstrating detector limits.
The local prototype has no production authentication or reviewer access control.
No publication, deployment, remote push or portal submission has occurred. Late-credit
eligibility is not established. Any student-specific personal reflection must be true.

## Demo artifact verification

`demo/provenance-guard-demo.mp4`: 165.956 seconds, 1280x720 H.264 video with AAC audio,
1,932,912 bytes. ffmpeg decoded the complete file without errors. A representative
frame was visually inspected for text fit and consistency with live-model.json.
The video is an explicitly AI-narrated replay of recorded API evidence, not a fake
live screen capture or personal student recording. Narration transcript and generator
are included. The temporary render files are ignored by Git.
