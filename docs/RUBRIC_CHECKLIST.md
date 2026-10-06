# Project 4 rubric coverage

Source: [authenticated course rubric](https://courses.codepath.org/courses/ai201/pages/grading#heading-project-4-provenance-guard), October 6, 2026.
**This records implementation evidence, not an awarded grade.** Aamori reports updated instructor permission for AI to complete the work.
AI authorship and actual user directions are disclosed; no personal review is invented.
Remote publication and submission still await approval.

| Criterion | Points | Coverage and evidence |
|---|---:|---|
| Text submission returns structured JSON | 1 | Implemented: POST /submit; API tests and evidence/examples.json |
| Response contains attribution and confidence | 1 | Implemented: all examples; scoring tests |
| Response contains transparency label text | 1 | Implemented: LABELS and API tests |
| README explains 2+ signals, properties and blind spots | 1 | Documented: Detection signals table |
| Individual signal results visibly reflected | 1 | Implemented: JSON normalized weights/scores and browser signal breakdown |
| Noticeably different high/lower confidence submissions | 1 | Verified live plain text: 0.8817 AI vs 0.5540 uncertain; 0.8313 human; evidence/live-model.json |
| Combination and meaningfulness validation explained | 1 | README scoring section; four course samples; no calibration claim |
| All three exact label texts in README | 1 | Documented verbatim |
| Plain-language labels | 1 | Implemented; actual nontechnical-person usability review pending |
| Different high/low label text | 1 | Verified all three through real live text API and offline metadata; boundary tests |
| Appeal captures reasoning | 1 | Implemented and browser verified |
| Under-review status and audit appeal | 1 | Implemented; duplicate/concurrent and persistence tests |
| Rate limit actually reached | 1 | Verified 10 successful then two 429 responses |
| Specific limits and realistic rationale | 1 | README: 10/minute, 100/day per IP; configuration in app.py |
| 3+ log entries with attribution, confidence, timestamp | 1 | evidence/audit-sample.json contains 10 events |
| Structured log format | 1 | SQLite JSON events and GET /log |
| Appeal alongside original classification | 1 | Immutable classification plus appeal event with original_decision |
| planning.md signals and combination | 1 | Written before implementation, then updated with actual fixes and new user guidance |
| planning.md specific uncertainty thresholds | 1 | 0.80 / 0.25, abstention and conflict damping |
| planning.md all three label variants | 1 | Written verbatim |
| planning.md appeals, 2+ edge cases, AI Tool Plan | 1 | Six concrete edge cases, M3/M4/M5 inputs and verification plan, architecture diagram |
| README specific signal-related limitations | 1 | Formal prose, repeated poetry, quoted disclosure, slangy AI, forged metadata |
| README real spec divergence | 1 | Title normalization changed after failing tests; documented as Codex's revision |
| Two specific AI uses, instructions and outputs | 1 | README records actual user directions, AI outputs, fixes and full Codex authorship |
| Student revised/overrode/decided differently | 1 | User-directed correction documented: compare prior projects beyond the initial model-only attempt; no invented personal code review |
| Stretch: 3+ distinct weighted signals/conflict resolution | +1 | Verified three live text signals and three offline metadata signals; weights and conflict rule documented |
| Stretch: certificate verification + distinct content badge | +1 | Implemented draft/process request, explicit local review, content hash binding; synthetic workflow tested, not real verification |
| Stretch: dashboard 3+ metrics | +1 | Browser verified verdict distribution, appeal rate, mean confidence, verified count |
| Stretch: second content type | +1 | Validated structured metadata through pipeline; documented type-specific process signal |

## Deliverables beyond rubric rows

- [x] Root planning.md with architecture and AI tool plan, written before implementation.
- [x] Runnable local source, pinned dependencies, 41 passing tests, reproducible evidence.
- [x] Real live semantic inference and all three plain-text label paths.
- [x] README technical sections and honest AI disclosure.
- [x] AI-narrated technical walkthrough video and transcript, explicitly a replay of recorded evidence.
- [x] Personal walkthrough outline, if an instructor specifically requires Aamori's own voice/camera.
- [ ] User final review of the deliverables; no personal experience or review is claimed on her behalf.
- [ ] Late-credit eligibility clarified (portal policies conflict; Canvas confirms the deadline only).
- [ ] GitHub remote creation/push approved and performed; no hosted repo URL yet.
- [ ] Project 4 portal submission approved and performed.

## Resolved follow-up

Groq is recommended rather than required by name. The previous plain-text verification
gap is now resolved: the official SDK configuration used by Projects 1/2 completed five
real calls and reached all three labels. The initial 403/1010 remains historical evidence;
no security controls or identity were changed. See [client comparison](GROQ_DIAGNOSTIC.md).

The online guide's older AI prohibition was superseded for this task by Aamori's report
of current in-class instructor permission. The docs disclose exactly what was authored
by AI and what Aamori directed. A strict grader's treatment of student-specific reflection
language is ultimately an instructor decision; no score is guaranteed.
