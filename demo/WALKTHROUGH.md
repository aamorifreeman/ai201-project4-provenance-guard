# Personal walkthrough outline (about 2 minutes)

Optional personal-recording outline. An AI-narrated technical walkthrough is included
in provenance-guard-demo.mp4; it replays real recorded API evidence and does not pretend
to be Aamori. Use this outline if a personal portfolio recording is desired or required.

* 0:00–0:15 — Name Provenance Guard and the problem: show uncertainty, don't claim
  that a writing-style detector can prove cheating or authorship.
* 0:15–0:40 — Load the sample; select structured metadata and Human; analyze.
  Explain the individual scores and weights. Contrast evidence index and confidence.
* 0:40–0:55 — Show AI and uncertain metadata examples from evidence/examples.json.
  Acknowledge metadata is self-reported and affects the score. Show the successful
  live text results; explain offline abstention when a provider is unavailable.
* 0:55–1:15 — Submit a reasoned appeal; show under_review and the unchanged original
  classification next to the new audit event.
* 1:15–1:35 — Show a draft/process verification request and distinct reviewed badge.
  Explain local reviewer names are not authentication and test fixtures aren't real
  human verification. Point out dashboard detection, appeal and confidence metrics.
* 1:35–1:50 — Open evidence/rate-limit.json: ten 200s followed by two 429s. Explain
  why 10/minute and 100/day fit the demo's expected writer usage.
* 1:50–2:00 — State one actual design decision you changed after reviewing the AI
  output, one limitation and what you would improve before deployment.

Keep the technical README evidence visible. Save the recording locally; request
approval before uploading it or adding a public link to a submission.
