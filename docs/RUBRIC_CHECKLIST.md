# Project 4 rubric coverage

Source: [authenticated course rubric](https://courses.codepath.org/courses/ai201/pages/grading#heading-project-4-provenance-guard), October 6, 2026.
**This records implementation evidence, not an awarded grade.** Student review and AI
collaboration reflection remain required. The walkthrough and remote submission are pending.

| Criterion | Points | Coverage and evidence |
|---|---:|---|
| Text submission returns structured JSON | 1 | Implemented: POST /submit; API tests and evidence/examples.json |
| Response contains attribution and confidence | 1 | Implemented: all examples; scoring tests |
| Response contains transparency label text | 1 | Implemented: LABELS and API tests |
| README explains 2+ signals, properties and blind spots | 1 | Documented: Detection signals table |
| Individual signal results visibly reflected | 1 | Implemented: JSON normalized weights/scores and browser signal breakdown |
| Noticeably different high/lower confidence submissions | 1 | Verified metadata: 0.8042 vs 0.5331; offline text abstains; live text unverified |
| Combination and meaningfulness validation explained | 1 | README scoring section; four course samples; no calibration claim |
| All three exact label texts in README | 1 | Documented verbatim |
| Plain-language labels | 1 | Implemented; actual nontechnical-person usability review pending |
| Different high/low label text | 1 | Verified all three through metadata API; threshold tests |
| Appeal captures reasoning | 1 | Implemented and browser verified |
| Under-review status and audit appeal | 1 | Implemented; duplicate/concurrent and persistence tests |
| Rate limit actually reached | 1 | Verified 10 successful then two 429 responses |
| Specific limits and realistic rationale | 1 | README: 10/minute, 100/day per IP; configuration in app.py |
| 3+ log entries with attribution, confidence, timestamp | 1 | evidence/audit-sample.json contains 10 events |
| Structured log format | 1 | SQLite JSON events and GET /log |
| Appeal alongside original classification | 1 | Immutable classification plus appeal event with original_decision |
| planning.md signals and combination | 1 | Written before implementation; student adoption/revision pending |
| planning.md specific uncertainty thresholds | 1 | 0.80 / 0.25, abstention and conflict damping |
| planning.md all three label variants | 1 | Written verbatim |
| planning.md appeals, 2+ edge cases, AI Tool Plan | 1 | Six concrete edge cases, M3/M4/M5 inputs and verification plan, architecture diagram |
| README specific signal-related limitations | 1 | Formal prose, repeated poetry, quoted disclosure, slangy AI, forged metadata |
| README real spec divergence | 1 | Title normalization changed after failing tests; documented as Codex's revision |
| Two specific AI uses, instructions and outputs | 1 | Factual Codex authorship disclosed; student-specific directed collaboration not yet complete |
| Student revised/overrode/decided differently | 1 | **Pending Aamori's genuine review and decisions. Not claimed complete.** |
| Stretch: 3+ distinct weighted signals/conflict resolution | +1 | Verified offline metadata ensemble; optional text semantic signal blocked by HTTP 403 |
| Stretch: certificate verification + distinct content badge | +1 | Implemented draft/process request, explicit local review, content hash binding; synthetic workflow tested, not real verification |
| Stretch: dashboard 3+ metrics | +1 | Browser verified verdict distribution, appeal rate, mean confidence, verified count |
| Stretch: second content type | +1 | Validated structured metadata through pipeline; documented type-specific process signal |

## Deliverables beyond rubric rows

- [x] Root planning.md with architecture and AI tool plan.
- [x] Runnable local source, dependency files, 41 passing tests, reproducible evidence.
- [x] README technical sections and honest AI disclosure.
- [x] Demo outline and student review checklist.
- [ ] Student's substantive review, revisions and genuine reflection.
- [ ] Required personal walkthrough video (outline supplied, no recording fabricated).
- [ ] Working live semantic provider (HTTP 403 currently; offline mode is functional).
- [ ] Late-credit eligibility clarified (portal policies conflict).
- [ ] GitHub remote creation/push approved and performed; no hosted repo URL yet.
- [ ] Project 4 portal submission approved and performed.

## Follow-up clarification

Groq is recommended, not required by name. The two-signal minimum works offline.
However, all three categories and the high/lower confidence demonstrations currently
use **metadata**, so plain-text end-to-end label reachability remains **unverified**.
This is a substantive limitation, not merely an optional provider checkbox.
Exact access response: HTTP 403 / plain text `error code: 1010`; no bypass attempted.
See [Groq diagnostic](GROQ_DIAGNOSTIC.md). Configuration is aligned with existing
Project 1/2 (`openai/gpt-oss-120b`, 1600-token budget); live access is still blocked.
