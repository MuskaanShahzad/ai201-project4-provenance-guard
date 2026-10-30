# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-10-29 18:46
- Auto-marked BROKE (5xx, crash, no response): **5**
- Left for you to judge: **51**
- **Final tally: 43 held, 13 broke**

My standard for judging the ones the script left blank:

- **Evasion** — BROKE only if the AI text made it all the way to a `human`
  guess. Landing on `unsure` counts as HELD, since the system is being
  honestly uncertain rather than giving a false assurance; that's a different
  outcome from being fooled.
- **False positive** — BROKE if real human writing landed on `ai`. Landing on
  `unsure` counts as HELD for the same reason as above: no false accusation
  was made.
- **Prompt injection** — this pipeline has no instruction-following surface
  for these to land on. Signal one scores perplexity, not meaning, and the
  three label strings are fixed text chosen by score threshold, never built
  from the input. So these were HELD by construction, and I'm saying so
  rather than pretending the defense "caught" something that was never a
  reachable attack surface here.
- **Malformed** — HELD if the service handled it without crashing, even if
  the resulting score looks strange. BROKE means a 500.
- **Flood** — HELD if the limiter did what it was supposed to (let the first
  few through, rejected the rest).

One subtlety worth calling out: RQ10 and RQ11 came back 429, but not because
of anything in their own content. Both carry no usable `creator_id` (one is
form-encoded, the other has the wrong content-type), so the rate limiter
counted them against my own IP address instead, and by the time the run
reached them that address bucket was already used up by earlier malformed
rows. Those two requests never reached `/submit` at all. I'm still marking
them HELD, since nothing crashed and the limiter behaved exactly as designed,
but it's a different mechanism than "the route handled this input," and I
don't want that difference to disappear into one word.

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `e96ff1fc-f76c-410d-98d3-fa4882d43129` | human | 0.314 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `e13e74f1-c0c7-4ee7-8cf2-025cabde1525` | unsure | 0.517 | HELD |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c803ccc4-378c-44dc-aad8-0a1c4a3a5c2a` | unsure | 0.616 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `a28f39b2-078e-4494-a0da-9e067f21aea1` | unsure | 0.636 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `7daaeb3d-78da-4a49-84c5-f6b467e5ed85` | unsure | 0.433 | HELD |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c02696e7-5d1e-4f0e-8e02-ddefe0fd370d` | unsure | 0.571 | HELD |
| EV07 | evasion | signal two: padding with punctuation | 200 | `d132ff52-4b96-47c0-b627-e90dd03710fb` | unsure | 0.566 | HELD |
| EV08 | evasion | signal one: text below the token window | 200 | `aa411d95-5959-49d4-ac4d-853e9d8c207e` | human | 0.350 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `a9a3a1c5-a1d8-48c8-a4ad-fa6ea30555ae` | ai | 0.658 | HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `708dea6d-20f3-4bf6-a88a-436646c98c99` | ai | 0.889 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `30ca8d9d-b1b8-4164-866e-f2fef61cedca` | unsure | 0.638 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `799ebb11-3573-4989-936f-8ad260381ecf` | ai | 0.719 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `21e30e8a-3c22-4caf-8a7c-341996f17c88` | ai | 0.741 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `4c4ee4f3-14ba-4da8-9006-1d711ed18c6e` | ai | 0.737 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `d062fda9-ca12-49bd-bd7d-754205a3c371` | ai | 0.766 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `bc2235d5-795d-479e-9c5e-e04e2b673f73` | ai | 0.761 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `6a21a14e-71b7-4808-927c-2a7a5dae4c5a` | ai | 0.794 | BROKE |
| FP08 | false_positive | very short genuine human submission | 200 | `1f2b1a32-5b5b-4fb7-9137-a7d00df6a1ea` | unsure | 0.444 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `7c0ca9c1-dd7c-4ee8-9872-67bcd48fcb99` | unsure | 0.509 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `723bbf66-9767-48c7-bf31-9cea2e17aee1` | human | 0.326 | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `7d4be228-12e2-483b-9d08-b1ec065de88f` | unsure | 0.559 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `b588c4e8-a7ba-423b-8814-8651f5f8d5cb` | unsure | 0.559 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `1f80f752-c845-4a2d-a335-cb6cecdf2f81` | unsure | 0.494 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `b01e047d-db41-4e6a-8ae2-1fdfb77e7de9` | unsure | 0.610 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 500 | `—` | — | — | BROKE |
| MF03 | malformed | text is control characters | 200 | `bd2801f0-cfe1-4e82-a8b0-db520a230ce6` | human | 0.200 | HELD |
| MF04 | malformed | text is only punctuation | 200 | `fb0d3fe7-46b2-449b-b330-a394a4ca830c` | human | 0.308 | HELD |
| MF05 | malformed | text is a very long single word | 200 | `0e7ead99-4191-489e-be50-8e199062f219` | ai | 0.766 | HELD |
| MF06 | malformed | text is emoji only | 200 | `b36cc45f-b8b4-46a8-9d67-3515e2bd1253` | ai | 0.999 | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `7f9aa1cc-40ab-41ec-bdcc-99978f18d5b9` | ai | 0.953 | HELD |
| MF08 | malformed | text is 60,000 characters | 200 | `45c79c41-edbf-4d7e-8ac5-4c60a088e545` | ai | 0.943 | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | `76add599-4dc5-435c-a41e-710d7cb4a77e` | unsure | 0.368 | HELD |
| RQ03 | malformed | text is a number | 500 | `—` | — | — | BROKE |
| RQ04 | malformed | text is a list | 500 | `—` | — | — | BROKE |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 200 | `ba8f0e41-19b5-47c9-ad3f-a34205af78de` | human | 0.234 | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 500 | `—` | — | — | BROKE |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `58b72581-8010-441f-a110-8a4f1ae4e6fc` | human | 0.220 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `7cc90457-e94c-424f-a928-00ceb43427e0` | human | 0.220 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `847c7d16-d8e4-44d4-875f-35eb36c4d04f` | human | 0.220 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `df183572-b643-45cf-a526-a3ef5203343e` | human | 0.220 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `36797d24-f7fa-4a50-ace8-cc8862771d1a` | human | 0.220 | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 5 | 15 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "e96ff1fc-f76c-410d-98d3-fa4882d43129",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.3135,
  "model_score": 0.1635,
  "style_score": 0.6636,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "e13e74f1-c0c7-4ee7-8cf2-025cabde1525",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.5171,
  "model_score": 0.5943,
  "style_score": 0.4398,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "c803ccc4-378c-44dc-aad8-0a1c4a3a5c2a",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.6155,
  "model_score": 0.6662,
  "style_score": 0.5648,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "a28f39b2-078e-4494-a0da-9e067f21aea1",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.6357,
  "model_score": 0.6114,
  "style_score": 0.6599,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "7daaeb3d-78da-4a49-84c5-f6b467e5ed85",
  "creator_id": "attacker_EV05",
  "guess": "unsure",
  "confidence": 0.4327,
  "model_score": 0.3212,
  "style_score": 0.5442,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "c02696e7-5d1e-4f0e-8e02-ddefe0fd370d",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.571,
  "model_score": 0.5727,
  "style_score": 0.5692,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "d132ff52-4b96-47c0-b627-e90dd03710fb",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.5658,
  "model_score": 0.5862,
  "style_score": 0.5454,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "aa411d95-5959-49d4-ac4d-853e9d8c207e",
  "creator_id": "attacker_EV08",
  "guess": "human",
  "confidence": 0.3496,
  "model_score": 0.2452,
  "style_score": 0.5932,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "BROKE"
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "a9a3a1c5-a1d8-48c8-a4ad-fa6ea30555ae",
  "creator_id": "attacker_EV09",
  "guess": "ai",
  "confidence": 0.6579,
  "model_score": 0.7042,
  "style_score": 0.6115,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "708dea6d-20f3-4bf6-a88a-436646c98c99",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.8891,
  "model_score": 0.9792,
  "style_score": 0.799,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "30ca8d9d-b1b8-4164-866e-f2fef61cedca",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.6383,
  "model_score": 0.6175,
  "style_score": 0.6591,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "799ebb11-3573-4989-936f-8ad260381ecf",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.7187,
  "model_score": 0.7387,
  "style_score": 0.6986,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "21e30e8a-3c22-4caf-8a7c-341996f17c88",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.7409,
  "model_score": 0.8051,
  "style_score": 0.6767,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "4c4ee4f3-14ba-4da8-9006-1d711ed18c6e",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.7369,
  "model_score": 0.8329,
  "style_score": 0.641,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "d062fda9-ca12-49bd-bd7d-754205a3c371",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.7665,
  "model_score": 0.8005,
  "style_score": 0.7325,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "bc2235d5-795d-479e-9c5e-e04e2b673f73",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.7613,
  "model_score": 0.8814,
  "style_score": 0.6413,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "6a21a14e-71b7-4808-927c-2a7a5dae4c5a",
  "creator_id": "attacker_FP07",
  "guess": "ai",
  "confidence": 0.7942,
  "model_score": 0.8816,
  "style_score": 0.7067,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "error": null,
  "verdict": "BROKE"
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "1f2b1a32-5b5b-4fb7-9137-a7d00df6a1ea",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.4441,
  "model_score": 0.3223,
  "style_score": 0.5659,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "7c0ca9c1-dd7c-4ee8-9872-67bcd48fcb99",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.5092,
  "model_score": 0.4625,
  "style_score": 0.556,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "723bbf66-9767-48c7-bf31-9cea2e17aee1",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.3259,
  "model_score": 0.2044,
  "style_score": 0.4474,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "7d4be228-12e2-483b-9d08-b1ec065de88f",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.5586,
  "model_score": 0.5943,
  "style_score": 0.5229,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "b588c4e8-a7ba-423b-8814-8651f5f8d5cb",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.5588,
  "model_score": 0.4998,
  "style_score": 0.6177,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "1f80f752-c845-4a2d-a335-cb6cecdf2f81",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.4945,
  "model_score": 0.6401,
  "style_score": 0.3488,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "b01e047d-db41-4e6a-8ae2-1fdfb77e7de9",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.6098,
  "model_score": 0.5583,
  "style_score": 0.6613,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 500,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>ValueError: Text is too short to score \u2014 a few sentences at least.\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=yes&a",
  "verdict": "BROKE"
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "bd2801f0-cfe1-4e82-a8b0-db520a230ce6",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.2,
  "model_score": 0.0,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "fb0d3fe7-46b2-449b-b330-a394a4ca830c",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.3078,
  "model_score": 0.0112,
  "style_score": 1.0,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "0e7ead99-4191-489e-be50-8e199062f219",
  "creator_id": "attacker_MF05",
  "guess": "ai",
  "confidence": 0.766,
  "model_score": 0.9976,
  "style_score": 0.6667,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "b36cc45f-b8b4-46a8-9d67-3515e2bd1253",
  "creator_id": "attacker_MF06",
  "guess": "ai",
  "confidence": 0.9985,
  "model_score": 0.9969,
  "style_score": 1.0,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "7f9aa1cc-40ab-41ec-bdcc-99978f18d5b9",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.9532,
  "model_score": 0.9064,
  "style_score": 1.0,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "45c79c41-edbf-4d7e-8ac5-4c60a088e545",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.9427,
  "model_score": 0.9876,
  "style_score": 0.8979,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 200,
  "content_id": "76add599-4dc5-435c-a41e-710d7cb4a77e",
  "creator_id": null,
  "guess": "unsure",
  "confidence": 0.3677,
  "model_score": 0.2395,
  "style_score": 0.6667,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "error": null,
  "verdict": "HELD"
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 500,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>AttributeError: &#39;int&#39; object has no attribute &#39;strip&#39;\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=ye",
  "verdict": "BROKE"
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 500,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>AttributeError: &#39;list&#39; object has no attribute &#39;strip&#39;\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=y",
  "verdict": "BROKE"
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 200,
  "content_id": "ba8f0e41-19b5-47c9-ad3f-a34205af78de",
  "creator_id": {
    "id": "x"
  },
  "guess": "human",
  "confidence": 0.2344,
  "model_score": 0.0492,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 500,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>AttributeError: &#39;list&#39; object has no attribute &#39;get&#39;\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=yes",
  "verdict": "BROKE"
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 500,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>AttributeError: &#39;dict&#39; object has no attribute &#39;strip&#39;\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=y",
  "verdict": "BROKE"
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "58b72581-8010-441f-a110-8a4f1ae4e6fc",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2201,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "7cc90457-e94c-424f-a928-00ceb43427e0",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2201,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "847c7d16-d8e4-44d4-875f-35eb36c4d04f",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2201,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "df183572-b643-45cf-a526-a3ef5203343e",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2201,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "36797d24-f7fa-4a50-ace8-cc8862771d1a",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2201,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": "HELD"
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```
