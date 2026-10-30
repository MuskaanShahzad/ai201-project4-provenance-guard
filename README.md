# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

1. A `POST /submit` request comes in with JSON: `text` and `creator_id`.
2. The route pulls `text` and `creator_id` out of the request body.
3. Signal one (`detector.py`) runs a local language model on the text and returns `model_score`, a number from 0 to 1 showing how predictable the text is.
4. Signal two (`stylometry.py`) measures the shape of the text (sentence length spread, vocabulary variety, punctuation) and returns `style_score`, also from 0 to 1.
5. `scoring.combine_signals()` merges `model_score` and `style_score` into one `combined_score`.
6. `scoring.score_to_label()` turns that score into a short `guess` (`ai`, `human`, or `unsure`) and the full label text a reader sees.
7. The decision gets written to the audit log through `audit.log_decision()`, and the response goes back with `content_id`, `guess`, `confidence`, `label`, `model_score`, and `style_score`.

---

## Signals and Scoring

### Signal one — the model signal

**What it measures:** Perplexity, which is how surprised a local language model (gpt2) is by the text. It's checking how predictable each next word is, given what came before it. Low perplexity means the model found the text easy to guess. High perplexity means it didn't.

**Why that might differ between human and AI writing:** A language model writes by repeatedly picking a likely next word, so AI-generated text tends to be exactly what a model would predict, which shows up as low perplexity. Human writing wanders more: odd word choices, abrupt turns, specific details instead of typical phrasing.

**What it can't see:** The difference between plainness and authorship. This signal rewards common words in short, ordinary sentences, and plenty of real people write that way. Someone writing in a second language, a younger writer, or anyone being plain on purpose can score about as machine-like as actual AI writing does. The reverse is true too: dense, rare-word prose often scores as human even when AI wrote it, because rare words are exactly what the model fails to predict. The writers this signal is most likely to accuse are the ones with the least room to argue back.

### Signal two — the style signal

**What it measures:** The shape of the text, not its meaning. That's sentence length variation, how varied the vocabulary is (type-token ratio), and how much and what kind of punctuation shows up.

**Why that might differ between human and AI writing:** Generated prose tends toward even, mid-length sentences and a narrower band of vocabulary, because that's what "most likely next word" produces on average. Human writing is lumpier: a three-word sentence next to a forty-word one, punctuation that's more idiosyncratic.

**What it can't see:** This signal cannot read. It has no idea what the text actually says. Anything that changes the shape without changing the substance moves the score: adding typos, breaking up sentences, pasting in a quotation. That's a cheap thing for someone to do on purpose, which is exactly what next unit's attack set is going to try.

### The combining rule

**The rule:** When the two signals are within 0.3 of each other, they're agreeing enough that I just average them normally. When they split by more than 0.3, I don't average straight down the middle. Instead I weight the combined score 70% toward whichever signal read more human and 30% toward the one reading more AI. A sharp disagreement between two different ways of measuring the same text is real uncertainty, and my false-positive trace from Milestone 1 already decided which way to lean when I'm uncertain: a missed detection costs the site a little, but a wrong accusation costs a real writer a lot.

**The numbers:** Equal weight (0.5 / 0.5) when the signals agree. On disagreement, 0.7 toward the lower (more human-reading) score and 0.3 toward the higher. The threshold and both lean values live in `config.py` (`DISAGREEMENT_THRESHOLD`, `DISAGREEMENT_LEAN_HUMAN`, `DISAGREEMENT_LEAN_AI`) alongside `WEIGHT_MODEL_SIGNAL` / `WEIGHT_STYLE_SIGNAL`.

**Where it lives:** `scoring.py::combine_signals`

**A case where my two signals split, and what my rule does with it:**

I took AI-generated text and riddled it with misspellings ("Teh implemetnation of teh propsed framwork reqiures carefull considerstion..."). The model signal scored it 0.0159, almost confidently human, because misspelled words are exactly what surprises a language model, and surprise reads as human to that signal. But the style signal still scored it 0.6727, leaning AI, because the sentence structure and word count underneath the typos hadn't actually changed. That's a 0.66 split, so my rule kicked in: it leaned 70% toward the human-reading score and landed at 0.2129, confidently human.

I want to be upfront about what that means: my own rule just let a heavily-typoed piece of AI text through as "confidently human." I chose that trade on purpose, fewer false accusations of real writers, but it also means typos are a cheap way to fool this system. That's exactly the kind of thing I expect next unit's attack set to find.

**A second finding from calibration:** `punctuation_density` came back 0.000 for every normal piece of text I tried, clearly-AI and clearly-human alike, because none of them happened to use a semicolon, colon, or dash. At zero, that measure always reads as maximally AI-like, even for totally ordinary human writing, so on its own it barely tells me anything. The style signal's real separating power comes from sentence length spread and vocabulary variety, and punctuation mostly just sits at its ceiling. I kept it in the average anyway, weighted equally with the other two since nothing argues one measure should count more, but it's the weakest of the three, and I'd rather say that than quietly rely on a signal that isn't doing much work.

---

## Label Variants

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.35 | "We think this was probably written by a person." |
| unsure | 0.35 – 0.65 | "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look." |
| high-confidence AI | 0.65 – 1.00 | "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look." |

**Why I worded the "unsure" one this way:**

I wanted it to admit uncertainty without sounding like a quieter version of an accusation. Early drafts of this label said something closer to "human, 0.81 confidence," which means nothing to someone who's never seen a confidence score, and worse, it still sounds like a verdict even when it isn't one. I tested all three labels by reading them back as if I'd gotten one on my own writing. The unsure label still made me uneasy even with "this isn't an accusation" spelled out directly, which told me the discomfort isn't really fixable with softer wording. What I could control was making sure it doesn't claim more certainty than the system actually has, and that it tells the writer there's something they can do about it.

I used the same "we could be wrong" framing on the high-confidence AI label for the same reason: a flat "likely AI-generated" reads as a settled verdict, and this system is never actually that sure.

---

## Sample Run

**A submission**

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "The implementation of the proposed framework requires careful consideration of several key factors. First, it is important to note that the system must be able to handle a wide variety of different inputs. Additionally, the overall performance of the solution depends on a number of important variables.", "creator_id": "muskaan"}'
```

```json
{
  "content_id": "2b17ceb4-d473-4fd3-aea1-24cad6f5be38",
  "guess": "ai",
  "confidence": 0.7831,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "model_score": 0.8864,
  "style_score": 0.6798
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "2b17ceb4-d473-4fd3-aea1-24cad6f5be38", "reasoning": "I wrote this myself for a class assignment. I tend to write in plain, formal sentences because English is my second language."}'
```

```json
{
  "ok": true,
  "content_id": "2b17ceb4-d473-4fd3-aea1-24cad6f5be38",
  "status": "under_review",
  "message": "Your appeal has been recorded and will be reviewed."
}
```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=20"
```

```json
{
  "combined_score": 0.7831,
  "content_id": "2b17ceb4-d473-4fd3-aea1-24cad6f5be38",
  "creator_id": "muskaan",
  "guess": "ai",
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "model_score": 0.8864,
  "status": "decided",
  "style_score": 0.6798,
  "timestamp": "2026-10-28T09:10:11+00:00"
}
{
  "content_id": "2b17ceb4-d473-4fd3-aea1-24cad6f5be38",
  "creator_id": "muskaan",
  "event": "appeal",
  "reasoning": "I wrote this myself for a class assignment. I tend to write in plain, formal sentences because English is my second language.",
  "status": "under_review",
  "timestamp": "2026-10-28T09:10:15+00:00"
}
```
The two entries above share one content_id. The original decision keeps its "decided" status exactly as it was logged, and the appeal sits right after it with status "under_review." Nothing gets overwritten, since the log is append-only.

---

## How I Used AI

**Moment 1**

- *What I asked for:* Right after `/submit` was wired up to the first signal in Milestone 3, I didn't actually understand what had just happened. I asked Claude to explain it to me: what `app.py` was doing, why `curl` was a separate thing from the server, and specifically what `debug=True` meant and where it even came from, since I couldn't find the literal word "True" written anywhere in `config.py`.
- *What came back:* Claude walked through the request/response flow in plain terms (the server as something that just sits there listening, `curl` as the thing knocking on its door), then showed me the live server log so I could watch `Restarting with stat` happen in real time right after a file change. For the `debug=True` question, it broke the line in `config.py` into the two yes/no checks that make it up and then actually ran `python -c "import config; print(config.DEBUG)"` so I could see Python compute `True` on its own instead of just taking it on faith.
- *What I changed:* Nothing in the code changed from this. What changed was how I was reading the rest of the project: I started actually checking the terminal output instead of assuming a command worked, and I stopped treating `debug=True` as boilerplate I could skip past.

**Moment 2**

- *What I asked for:* While writing the three labels in Milestone 5, my first draft of the high-confidence AI label was flat and final-sounding: "we think this was likely generated by AI, not written by a person." I asked Claude to make it softer and kinder, something closer to "we think this might be AI, and we might be wrong."
- *What came back:* Claude rewrote it as "We think this might have been generated by AI, but we could be wrong," and kept the line about appealing. It also ran an exercise reading all three labels back as if it had received them as the writer, not the engineer, which surfaced something I hadn't thought about: even the unsure label, which explicitly says "this isn't an accusation," would still make someone uneasy about something they wrote themselves, and that discomfort isn't really something softer wording can fix. The honest version of the label was always going to cost the writer something; the only real choice was not making it worse than it had to be.
- *What I changed:* I kept the softened AI label exactly as it came back, since it matched what I actually meant: a guess, not a verdict. I left the unsure label's directness alone, because the reaction to it wasn't really about the wording, it was an honest cost of the trade I'd already chosen in Milestone 1, between missing some AI text and wrongly accusing a real person.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 60 per day

**Why those numbers and not others:**

A real writer revising a piece and submitting a few drafts in one sitting would stay well under 5 a minute without even thinking about it, and even pasting in every paragraph of a long piece separately over an hour would stay nowhere near 60 a day. A script trying to map my thresholds by sending a thousand variations gets throttled hard: at 5 a minute, obeying the limit means it would take over three hours just to send 1000 requests, and the 60-a-day cap means it could never even get there in a single day no matter how patient it is.

**What a caller counts as:**

A caller is identified by `creator_id` when the request includes one, and falls back to the caller's IP address when it doesn't. This is the starter's `rate_limit_key` function, which I didn't modify. Worth being honest about: since it keys on `creator_id` first, a script submitting under many different made-up `creator_id` values from the same address would get a fresh limit bucket for each one. That gap is exactly what the per-creator-vs-per-address stretch feature exists to address, and I left it out since I'm only doing required features this unit.

**The run of status codes when I pushed past it:**

```
$ python run_attacks.py --flood 15
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

10 of 15 requests were rate limited, right after the 5th request, matching the 5-per-minute limit.

---

## Attack Run — Before

I ran the full 56-attack set (`python run_attacks.py --set attack_set`) against my service before changing anything. The full table with every attack, its result, and my held/broke mark is in `results/attack_run_2026-10-29_1846_before.md`.

**Final tally: 43 held, 13 broke**, by family:

| Family | Attacks | Held | Broke |
|---|---|---|---|
| evasion | 10 | 8 | 2 |
| false_positive | 8 | 2 | 6 |
| prompt_injection | 6 | 6 | 0 |
| malformed | 20 | 15 | 5 |
| flood_same_creator | 12 | 12 | 0 |

The `false_positive` family is the one that actually hurt: 6 of 8 real human writing samples landed on a confident "ai" guess. Every one of those was formal, careful, or rule-following writing (a formal register, a non-native speaker writing carefully, a student essay to a rubric, technical documentation, a formal template, deliberate repetition), which is exactly the blind spot I named for signal one back in Milestone 1 of the last unit. What I didn't expect going in was that signal two agrees with signal one on these texts instead of catching the ones it misses: every false-positive model_score and style_score I checked both landed above 0.6, so my disagreement rule (lean toward human when the two signals split by more than 0.3) never even triggered, because the two signals weren't disagreeing. They were agreeing on the wrong answer.

**Ten audit log entries from the run**

```json
{
  "timestamp": "2026-10-29T23:46:32+00:00",
  "content_id": "e96ff1fc-f76c-410d-98d3-fa4882d43129",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "model_score": 0.1635,
  "style_score": 0.6636,
  "combined_score": 0.3135,
  "label": "We think this was probably written by a person.",
  "status": "decided"
}
{
  "timestamp": "2026-10-29T23:46:34+00:00",
  "content_id": "708dea6d-20f3-4bf6-a88a-436646c98c99",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "model_score": 0.9792,
  "style_score": 0.799,
  "combined_score": 0.8891,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "status": "decided"
}
{
  "timestamp": "2026-10-29T23:46:34+00:00",
  "content_id": "799ebb11-3573-4989-936f-8ad260381ecf",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "model_score": 0.7387,
  "style_score": 0.6986,
  "combined_score": 0.7187,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "status": "decided"
}
{
  "timestamp": "2026-10-29T23:46:34+00:00",
  "content_id": "21e30e8a-3c22-4caf-8a7c-341996f17c88",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "model_score": 0.8051,
  "style_score": 0.6767,
  "combined_score": 0.7409,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "status": "decided"
}
{
  "timestamp": "2026-10-29T23:46:35+00:00",
  "content_id": "d062fda9-ca12-49bd-bd7d-754205a3c371",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "model_score": 0.8005,
  "style_score": 0.7325,
  "combined_score": 0.7665,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "status": "decided"
}
{
  "timestamp": "2026-10-29T23:46:36+00:00",
  "content_id": "1f80f752-c845-4a2d-a335-cb6cecdf2f81",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "model_score": 0.6401,
  "style_score": 0.3488,
  "combined_score": 0.4945,
  "label": "We can't tell whether this was written by a person or generated by AI. This isn't an accusation, we just don't have enough to go on either way. If you wrote this yourself, you can tell us and we'll take another look.",
  "status": "decided"
}
{
  "timestamp": "2026-10-29T23:46:41+00:00",
  "content_id": "7f9aa1cc-40ab-41ec-bdcc-99978f18d5b9",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "model_score": 0.9064,
  "style_score": 1.0,
  "combined_score": 0.9532,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "status": "decided"
}
{
  "timestamp": "2026-10-29T23:46:42+00:00",
  "creator_id": "attacker_RQ01",
  "event": "rejected",
  "status": "rejected",
  "reason": "bad_request",
  "detail": "text is required and can't be empty."
}
{
  "timestamp": "2026-10-29T23:46:43+00:00",
  "creator_id": "attacker_RQ05",
  "event": "rejected",
  "status": "rejected",
  "reason": "bad_request",
  "detail": "text is required and can't be empty."
}
{
  "timestamp": "2026-10-29T23:46:43+00:00",
  "creator_id": "attacker_flood",
  "event": "rejected",
  "status": "rejected",
  "reason": "rate_limited",
  "limit": "5 per 1 minute"
}
```

A quick read of what these show: EV01 is a real evasion win (typos added to AI text dragged it all the way to "human"). EV10 is the opposite, a strongly-caught AI sample, pasted for contrast. FP02, FP03, and FP05 are three of the six false-positive failures, FP03 being the one I pick below as the worst. PI05 is a prompt injection attempt that landed as an ordinary unsure score, since there's nothing in this pipeline for an instruction to hijack. MF07 is right-to-left script scoring 0.9532 "ai", which is a fairness concern I didn't go looking for but found anyway: a whole script being treated as inherently machine-like is its own kind of false-positive risk I hadn't considered when I wrote Milestone 1's blind spots. The last three are rejections: two clean 400s from my own input validation, and one 429 from the rate limiter catching the flood family exactly as designed.

**The single worst outcome**, the one I'd least want to explain to a writer whose work got caught by it:

FP03, "a non-native English speaker writing carefully," scored 0.7409 and came back high-confidence AI. This is not a hypothetical risk anymore. It's the exact blind spot I named for signal one in Milestone 1 of the last unit (careful, plain, correct writing from someone writing in a second language scores as machine-like as actual AI text), now confirmed by an attack I didn't write and couldn't see coming. This is the writer with the least power to push back on an accusation like this, and my system accused them anyway.

One more finding worth stating plainly, separate from any single attack: none of the five crashes (MF02, RQ03, RQ04, RQ07, RQ12) left any trace in the audit log at all, not even a rejection. The crash happens before my code ever reaches an `audit.log_*` call, so a real attacker triggering this same bug repeatedly would be completely invisible in my own records. That's the exact danger this unit's intro warned about: an attack that shows up only as an absence is one I'd never find.

---

## Run Log and Verdicts

I ran `scenarios.py` through `python run_eval.py --label before`, which produced `results/run_2026-10-29_1916_before.md`. Criterion 4 (the appeal path) can't be expressed in `scenarios.py`, since it needs a submission and then an appeal against the real `content_id` that came back, not just a text body. `run_eval.py` only posts to `/submit`, so I tested criterion 4 by hand instead, with a small script that does exactly that: submit, then appeal, three trials of five pairs each. That output is in `results/appeal_test_before.json`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. my own writing | ≤ 1 of 10 flagged high-confidence AI | 4/10 | 4/10 | 4/10 | MISSED |
| 2. score spread | ≥ 0.3 gap between clearly-AI and clearly-human | 0.3455 | 0.3455 | 0.3455 | MET |
| 3. label coverage | all 3 labels reachable across 10 texts | 3/3 | 3/3 | 3/3 | MET |
| 4. appeal path | 5 of 5 appeals change status to under_review | 5/5 | 5/5 | 5/5 | MET |
| 5. bad input | 5 of 5 avoid a 500 | 5/5 | 5/5 | 5/5 | MET |

All three trials came back identical on every criterion. That's expected, not a shortcut I skipped: neither signal has anything random in it, so the same text scores the same way every time.

**Real output from one trial**, pasted as text, naming the file and function that produced it:

*Criterion 1, from `scenarios.py` through `run_eval.py::main` through `app.py::submit`. Two of the four I'd least want to see flagged:*

```json
{
  "status": 200,
  "guess": "ai",
  "confidence": 0.7157,
  "model_score": 0.8241,
  "style_score": 0.6072,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "sent": "While trying to enroll in my benefits, I noticed that my gender is inc"
}
{
  "status": 200,
  "guess": "ai",
  "confidence": 0.7359,
  "model_score": 0.835,
  "style_score": 0.6368,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "sent": "Thank you for your kind message, I really appreciate you taking the ti"
}
```

*Criterion 2, same path, with `scoring.py::combine_signals` producing the gap:*

```json
{
  "status": 200,
  "guess": "ai",
  "confidence": 0.7831,
  "model_score": 0.8864,
  "style_score": 0.6798,
  "sent": "The implementation of the proposed framework requires careful consider"
}
{
  "status": 200,
  "guess": "unsure",
  "confidence": 0.4376,
  "model_score": 0.2914,
  "style_score": 0.5839,
  "sent": "Grandma's kitchen always smelled like burnt cinnamon. She forgot the t"
}
```

*Criterion 3, one of each label it actually reached:*

```json
{
  "status": 200,
  "guess": "ai",
  "confidence": 0.7124,
  "sent": "I went to the store yesterday and bought some milk and bread. It was a"
}
{
  "status": 200,
  "guess": "unsure",
  "confidence": 0.6375,
  "sent": "The system works well. It handles most cases correctly and provides go"
}
{
  "status": 200,
  "guess": "human",
  "confidence": 0.2657,
  "sent": "Autumn arrived quietly that year, the way it always had, with the mapl"
}
```

*Criterion 4, `test_appeal.py::main`, a small script I wrote since `run_eval.py` only reaches `/submit`, calling `app.py::submit` then `app.py::appeal`:*

```json
{
  "content_id": "c6162d28-fa59-4e62-828d-3a48e8c10695",
  "appeal_status_code": 200,
  "appeal_response": {
    "ok": true,
    "content_id": "c6162d28-fa59-4e62-828d-3a48e8c10695",
    "status": "under_review",
    "message": "Your appeal has been recorded and will be reviewed."
  }
}
```

And the matching audit log entries for that same content_id, confirming the original decision wasn't overwritten:

```json
{
  "timestamp": "2026-10-30T00:18:31+00:00",
  "content_id": "c6162d28-fa59-4e62-828d-3a48e8c10695",
  "creator_id": "eval_appeal_t1_1",
  "guess": "ai",
  "model_score": 0.8239,
  "style_score": 0.5764,
  "combined_score": 0.7002,
  "label": "We think this might have been generated by AI, but we could be wrong. If you wrote this yourself, you can appeal this decision and explain how you wrote it, and someone will take another look.",
  "status": "decided"
}
{
  "timestamp": "2026-10-30T00:18:31+00:00",
  "content_id": "c6162d28-fa59-4e62-828d-3a48e8c10695",
  "creator_id": "eval_appeal_t1_1",
  "event": "appeal",
  "status": "under_review",
  "reasoning": "I wrote this myself; testing the appeal path for criterion 4."
}
```

*Criterion 5, from `scenarios.py`'s "bodies" scenario through `app.py::submit`:*

```json
{
  "status": 400,
  "guess": null,
  "sent": "(empty text)"
}
{
  "status": 400,
  "guess": null,
  "sent": "{\"creator_id\": \"eval_bad_missing\"}"
}
{
  "status": 200,
  "guess": "ai",
  "confidence": 0.9988,
  "sent": "word word word word word word word word word word word word word word "
}
{
  "status": 400,
  "guess": null,
  "sent": "{\"text\": null, \"creator_id\": \"eval_bad_null\"}"
}
{
  "status": 400,
  "guess": null,
  "sent": "   "
}
```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
