# Verification record

Executed October 6, 2026 on the user's Mac with Python 3.13.7.

* `python -m pytest -q`: **40 passed**. Covers three metadata labels, four course
  text examples, eight boundary cases, conflict damping, short/non-English inputs,
  malformed/wrong-type/oversized payloads, appeal persistence and original decision
  preservation, duplicate and concurrent appeals, restart persistence, 429 and retry
  headers, creator-ID bypass resistance, certificate review/rejection/hash binding,
  analytics, optional provider response validation, timeout and UI resources.
* `python generate_evidence.py`: passed assertions. Seven decisions plus one appeal
  and two verification events give 10 structured events. All three label variants
  reached through the actual metadata API. Rate test: ten 200s, two 429s.
* Mac Chrome browser: submitted metadata using Load sample, saw likely_human at
  0.8091 confidence / 0.1909 AI index; submitted an appeal; saw under review and
  original classification plus reasoning in audit trail; submitted an earlier draft
  and process description; used an explicitly synthetic test reviewer to exercise
  approval; saw distinct credential badge and verified count 1. This was not a real
  human authorship verification. No external website was changed.
* Initial tests failed because the title changed prose sentence variance. Fixed by
  excluding title from text statistics. Browser verification found appeal-button
  cleanup re-enabled an already appealed action; corrected the state logic.
* Real Groq attempt: four course examples returned unavailable. Read-only provider
  diagnostic returned **HTTP 403**. Existing key was read only for the call, not
  copied into the repo or printed. No new credentials created. Cause was not proven;
  do not assume invalid key versus provider/network denial without further evidence.
* All certificate approvals in generated evidence are marked automated synthetic
  fixtures. Mock semantic responses only verify adapter behavior.

Not verified: live semantic predictions, scientific calibration/accuracy, authenticated
multi-user access, public deployment, student understanding, recorded personal video,
late-credit eligibility or actual portal submission. No grade is guaranteed.
