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

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

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
