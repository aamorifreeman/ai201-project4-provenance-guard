# Groq follow-up: exact blocker and smallest next step

A read-only authenticated `GET https://api.groq.com/openai/v1/models` with the existing
Project 1 key returned:

```text
HTTP 403
Content-Type: text/plain; charset=UTF-8
error code: 1010
```

No credential or private submission is included in this evidence. This does not prove
the API key is invalid, exhausted, or lacks model permissions. It is not a JSON
`model_not_found` error. [Cloudflare's official 1010 documentation](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-1xxx-errors/error-1010/)
identifies this as access denied based on a client signature and directs the caller
to the website owner. We stopped this network path: no signature spoofing, proxy
switch, security weakening, key rotation, new account or paid service was attempted.

## Existing configuration found

The user's Project 1 `src/config.py` and Project 2 `tools.py` already use
`openai/gpt-oss-120b`. Their comments/READMEs say course staff confirmed that replacement
for the starter's Scout model. This is an existing local record, not a new instructor
confirmation. Groq's [current model documentation](https://console.groq.com/docs/model/openai/gpt-oss-120b)
independently lists the model and JSON-object support. Existing Project 1 config uses
1600 output tokens because reasoning consumes the budget. The new reference now uses
this model and `max_completion_tokens=1600`; its request contract is tested locally.
No new live request was made after discovering the access denial. Historical
`live-model.json` correctly retains the originally attempted model name.

## Smallest next step

Aamori should ask the course instructor or Groq support to resolve the API access
block for her existing setup, providing the endpoint, date, HTTP 403 and code 1010
(**never the API key**). No communication has been sent. Once access is restored,
run `verify_live_model.py` with the existing env file and review the four actual
responses. This reference must continue to say live semantic inference is unverified
until successful results are recorded. Do not create/rotate credentials or pay for
service as a workaround without separate approval.

## Is semantic inference required by the assignment?

The project's Required Features section requires **at least two distinct signals**;
it does not mandate Groq or an LLM. Its Tools and Setup table is labeled
**Recommended stack**, and the first-signal milestone says **“If you're using Groq”**.
Thus an LLM is optional as a technology, while a multi-signal pipeline, meaningful
score variation and reachable labels remain required behavior.

The current reference has two local text signals but deliberately abstains for
plain text without a third available signal. The three labels and high/low confidence
variation were verified through the structured-metadata API, not through plain-text
live inference. The offline metadata ensemble uses structural, lexical and declared
process evidence. Whether that alone satisfies the instructor's expected text demo
is not established; **do not claim the plain-text label-reachability milestone is
verified**. A student-reviewed design revision or restored semantic service is needed
before making that claim.
