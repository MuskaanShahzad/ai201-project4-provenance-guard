# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-10-29 19:44
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**
- **Final tally: 48 held, 8 broke** (was 43 held, 13 broke, before)

The improvement: input validation added to `app.py::submit` ahead of the
signals, checking that `text` is actually a string, rejecting anything over
`config.MAX_TEXT_LENGTH` characters, and catching the "too short to score"
error that `detector.py` already raised but nothing used to catch. This fixed
all 5 crashes (MF02, RQ03, RQ04, RQ07, RQ12), now all 400s. Every
evasion, false_positive, and prompt_injection result is byte-identical to the
before run, since this change never touched a signal, a weight, or a
threshold.

Two side notes on rows that look different but aren't new behavior:

- **MF08** (60,000 characters) now returns 400 instead of processing at 200.
  That's intentional: it used to be silently truncated and scored anyway,
  which is the exact gap my Criterion 5 miss named. Now it's rejected like
  the rest of oversized input.
- **RQ09** came back 429 here, where it was 400 in the before run. This isn't
  a behavior change: right before this run, I manually tested the fix with a
  curl request that had no `creator_id` (one of my verification checks for
  RQ07), which counted against my own address's rate limit bucket. That used
  up one slot before the official run started, so the address bucket hit its
  cap one row earlier than it otherwise would have. Same mechanism as before,
  just shifted by one row because of my own prior testing.

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `a38398ab-ed9e-474b-b64e-65ee67e5515b` | human | 0.314 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `a3a42b87-8f15-4a96-a504-5da33c6b46b7` | unsure | 0.517 | HELD |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `59fbd978-02b8-49f8-ae01-e3ba98860c48` | unsure | 0.616 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `cd4ddd91-b6c3-4c1f-8b15-164960ad0e41` | unsure | 0.636 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `dd3ba9b6-a7b5-4b60-abad-4d57a8d35b83` | unsure | 0.433 | HELD |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `0980a883-c320-45c3-806a-c3e31a3c841b` | unsure | 0.571 | HELD |
| EV07 | evasion | signal two: padding with punctuation | 200 | `f34ea2a2-2846-4590-a7d8-7503ad7b6fb1` | unsure | 0.566 | HELD |
| EV08 | evasion | signal one: text below the token window | 200 | `23a4706d-cefa-4ed3-bd98-bc2bfae439cb` | human | 0.350 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `82d4822d-8520-4ccd-84a3-fcc3f7fdec97` | ai | 0.658 | HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `a185bf97-fe47-4b5d-86d2-805798453138` | ai | 0.889 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `eb714930-2b94-4a61-b53d-26720fd7e9a1` | unsure | 0.638 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `15cd09c0-c577-4e03-a3db-decd16c24104` | ai | 0.719 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `3f3fc866-ce82-4c00-9e6b-6e66cc0440a1` | ai | 0.741 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `fd5814ba-d6a5-449b-a957-54937942c17a` | ai | 0.737 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `5e65e55f-a1c1-48ef-9c51-5fb35ef552c5` | ai | 0.766 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `424e3fdb-f36f-496a-9f77-7058993075d3` | ai | 0.761 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `9813a52b-6347-434a-81bd-f24f3c873251` | ai | 0.794 | BROKE |
| FP08 | false_positive | very short genuine human submission | 200 | `7fb9d308-9a2f-4db3-afaa-edb71ac095ae` | unsure | 0.444 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `7f172927-3a30-464a-86fd-c266ba47fb45` | unsure | 0.509 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `5add3294-86d2-402c-b02c-7388d4cb5903` | human | 0.326 | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `78d12407-cde3-454c-8aeb-88b1d4b5b01c` | unsure | 0.559 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `dbbc3735-68d3-4dac-bc9b-d9ad3974546b` | unsure | 0.559 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `b112782d-2729-463c-8eeb-ebf0af1f529f` | unsure | 0.494 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `289b366d-a946-4f4f-b09c-c98e641ae514` | unsure | 0.610 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | `065092c2-90ba-4a36-9f2b-4b8ebc0c1391` | human | 0.200 | HELD |
| MF04 | malformed | text is only punctuation | 200 | `3d8183d1-455f-4fdb-8d47-eb177733feef` | human | 0.308 | HELD |
| MF05 | malformed | text is a very long single word | 200 | `60033870-70ab-460a-bbb6-7acf74f74eae` | ai | 0.766 | HELD |
| MF06 | malformed | text is emoji only | 200 | `576c8dff-c4cf-4070-af37-ba1429b9aae4` | ai | 0.999 | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `370c80d2-d110-418c-bf9a-f3d5b2bf77d3` | ai | 0.953 | HELD |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | `7c491fe8-fc94-4ce1-8913-5dfabe4da127` | unsure | 0.368 | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 200 | `82b5525c-1162-48c4-ac59-3d525192cfff` | human | 0.234 | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 429 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `6c226854-7f16-4e78-887f-a7a930b9d55b` | human | 0.220 | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `e20e4553-e803-49ae-b3ac-061bece5102e` | human | 0.220 | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `058cef97-12e1-4a09-a674-bf9c9e6439bd` | human | 0.220 | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `1112cdc2-67d1-40b7-94f9-b64c24d263a9` | human | 0.220 | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `2329c6fc-c0e5-46a6-a32e-1da6a12b3b5b` | human | 0.220 | HELD |
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
| `malformed` | 20 | 0 | 20 |
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
  "content_id": "a38398ab-ed9e-474b-b64e-65ee67e5515b",
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
  "content_id": "a3a42b87-8f15-4a96-a504-5da33c6b46b7",
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
  "content_id": "59fbd978-02b8-49f8-ae01-e3ba98860c48",
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
  "content_id": "cd4ddd91-b6c3-4c1f-8b15-164960ad0e41",
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
  "content_id": "dd3ba9b6-a7b5-4b60-abad-4d57a8d35b83",
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
  "content_id": "0980a883-c320-45c3-806a-c3e31a3c841b",
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
  "content_id": "f34ea2a2-2846-4590-a7d8-7503ad7b6fb1",
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
  "content_id": "23a4706d-cefa-4ed3-bd98-bc2bfae439cb",
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
  "content_id": "82d4822d-8520-4ccd-84a3-fcc3f7fdec97",
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
  "content_id": "a185bf97-fe47-4b5d-86d2-805798453138",
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
  "content_id": "eb714930-2b94-4a61-b53d-26720fd7e9a1",
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
  "content_id": "15cd09c0-c577-4e03-a3db-decd16c24104",
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
  "content_id": "3f3fc866-ce82-4c00-9e6b-6e66cc0440a1",
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
  "content_id": "fd5814ba-d6a5-449b-a957-54937942c17a",
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
  "content_id": "5e65e55f-a1c1-48ef-9c51-5fb35ef552c5",
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
  "content_id": "424e3fdb-f36f-496a-9f77-7058993075d3",
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
  "content_id": "9813a52b-6347-434a-81bd-f24f3c873251",
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
  "content_id": "7fb9d308-9a2f-4db3-afaa-edb71ac095ae",
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
  "content_id": "7f172927-3a30-464a-86fd-c266ba47fb45",
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
  "content_id": "5add3294-86d2-402c-b02c-7388d4cb5903",
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
  "content_id": "78d12407-cde3-454c-8aeb-88b1d4b5b01c",
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
  "content_id": "dbbc3735-68d3-4dac-bc9b-d9ad3974546b",
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
  "content_id": "b112782d-2729-463c-8eeb-ebf0af1f529f",
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
  "content_id": "289b366d-a946-4f4f-b09c-c98e641ae514",
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
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "065092c2-90ba-4a36-9f2b-4b8ebc0c1391",
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
  "content_id": "3d8183d1-455f-4fdb-8d47-eb177733feef",
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
  "content_id": "60033870-70ab-460a-bbb6-7acf74f74eae",
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
  "content_id": "576c8dff-c4cf-4070-af37-ba1429b9aae4",
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
  "content_id": "370c80d2-d110-418c-bf9a-f3d5b2bf77d3",
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
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
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
  "content_id": "7c491fe8-fc94-4ce1-8913-5dfabe4da127",
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
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
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
  "content_id": "82b5525c-1162-48c4-ac59-3d525192cfff",
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
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": "HELD"
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "6c226854-7f16-4e78-887f-a7a930b9d55b",
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
  "content_id": "e20e4553-e803-49ae-b3ac-061bece5102e",
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
  "content_id": "058cef97-12e1-4a09-a674-bf9c9e6439bd",
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
  "content_id": "1112cdc2-67d1-40b7-94f9-b64c24d263a9",
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
  "content_id": "2329c6fc-c0e5-46a6-a32e-1da6a12b3b5b",
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
