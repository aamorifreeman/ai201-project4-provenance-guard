# AI-narrated technical walkthrough

This replays actual recorded API evidence; it is not Aamori’s voice or personal reflection.

## 1. Provenance Guard

This is an AI-narrated technical walkthrough of Provenance Guard. It replays recorded API evidence, not a fabricated live screen recording. The system analyzes creative text, communicates uncertainty, and gives creators a path to appeal. No detector score proves authorship.

## 2. Three signals, one cautious result

A text submission passes through three signals: semantic assessment, structural stylometry, and lexical evidence. Their weights are fifty-five, twenty-five, and twenty percent. Strong disagreement pulls the result toward uncertainty. Short text, unsupported language, or missing evidence triggers abstention.

## 3. Actual live text results

Actual live submissions reached all three labels. The explicitly AI-disclosed positive control scored point eight eight one seven. The informal review received a human label at point eight three one three confidence. Formal prose stayed uncertain. The generic AI example also stayed uncertain, showing why style is not proof.

## 4. Appeal without rewriting history

An appeal records the creator’s reasoning and changes the content status to under review. The original decision stays intact. A separate structured audit event links the explanation to that decision. Duplicate open appeals are rejected, and the tests also check concurrent requests and database persistence.

## 5. All four stretch features

The four stretch features are implemented. The ensemble exposes its individual scores. A draft and process review can issue a content-bound certificate, separate from the detector label. Analytics reports verdict patterns, appeal rate, and mean confidence. Structured metadata adds a creation-process signal. Demonstration approvals are clearly marked synthetic.

## 6. Safety and verification

Rate limiting permits ten submissions per minute and one hundred per day. Twelve consecutive requests produced ten successful responses and two rate-limit errors. Forty-one automated tests passed. Browser checks covered classification, appeals, certificates, and analytics. This local prototype still needs real authentication before any public deployment.

## 7. What changed and what remains

The initial custom HTTP client failed. Comparing prior course projects identified the ordinary official Groq SDK and a larger reasoning-token budget. That setup restored real inference without a proxy or identity workaround. The README records the changes, limitations, and AI assistance. Publication and final submission still require approval.
