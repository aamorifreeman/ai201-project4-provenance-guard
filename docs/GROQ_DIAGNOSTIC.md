# Groq client comparison — resolved October 6, 2026

Aamori explicitly asked to compare earlier course projects after the initial 403.
The comparison found an ordinary client difference, not a credential or permission fix.

| Detail | Earlier Projects 1/2 | Initial Project 4 | Final Project 4 |
|---|---|---|---|
| Client | official Groq 0.15.0 | handwritten urllib | official Groq 0.15.0 |
| Transport | httpx 0.28.1, normal defaults | urllib default | httpx 0.28.1, normal defaults |
| Model | openai/gpt-oss-120b | llama-3.3-70b-versatile, then model-only alignment | openai/gpt-oss-120b |
| Token budget | 600 in P2; 1600 in P1 | initially 220 | 1600 completion tokens |
| Key | existing course .env | existing course key | existing course key; read only, never copied |
| Observed outcome | old READMEs document successful work | HTTP 403 / error code: 1010 | model listing, five API classifications and browser inference succeeded |

Project 3's baseline instead uses normal httpx POST requests to the same official
endpoint. No custom user-agent override, proxy, alternate identity or TLS bypass was
found in these project client implementations. Project 2's installed versions were
verified directly: groq 0.15.0, httpx 0.28.1, httpcore 1.0.9, certifi 2026.7.22.
No proxy variables were present in the inspected process. Earlier files were not changed.

The initial error remains preserved in [groq-diagnostic.json](../evidence/groq-diagnostic.json)
and [initial-urllib-failure.json](../evidence/initial-urllib-failure.json). The first
follow-up correctly stopped on the unexplained access denial. After the user's explicit
request, the existing projects' unmodified official SDK setup was tested successfully.
Project 4 now uses that supported setup. No security settings, credentials, account
permissions or payment plan were changed; no access-control bypass was attempted.

## Actual live evidence

[evidence/live-model.json](../evidence/live-model.json) records five actual semantic
responses through the Flask POST /submit route, using the official SDK:

* Explicit AI disclosure: likely_ai, confidence 0.8817.
* Informal course review: likely_human, confidence 0.8313.
* Formal borderline: uncertain, confidence 0.5540.
* Generic course AI example: uncertain, AI index 0.7399; this abstention is retained.
* Edited-AI borderline: uncertain, confidence 0.6605.

The Mac browser separately showed the course review with semantic score 0.08,
all three signals available, and likely_human at 0.8313. No mock response is included
in those live results. Unit tests use explicitly synthetic responses separately.

## Requirements and remaining limitations

Groq is a recommended technology, not a required named provider: the assignment says
at least two distinct signals and “If you're using Groq.” Three live text signals and
all three text labels are now verified. The previous plain-text coverage gap is resolved.
This does not establish scientific detector accuracy or calibrated confidence.
Self-reported metadata and draft-review demo credentials are still not proof of origin.

To reproduce with an existing key without copying it into the repo:

```sh
python run.py --existing-env /absolute/path/to/existing/course/.env
python verify_live_model.py --existing-env /absolute/path/to/existing/course/.env
```

Sources: user's existing `ai201-project1-unofficial-guide/src/config.py`,
`src/generate.py`, and README; `ai201-project2-fitfindr-starter/tools.py`, requirements,
installed package versions, README; TakeMeter `src/takemeter/baseline.py`.
Groq's [official model docs](https://console.groq.com/docs/model/openai/gpt-oss-120b)
confirm JSON-object support for the configured model.
