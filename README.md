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

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. A `POST /submit` request arrives with JSON: `text` and `creator_id`.
2. The route pulls `text` and `creator_id` out of the request body.
3. Signal one (`detector.py`) runs a local language model on the text and returns `model_score` — how predictable the text is, as a 0–1 number.
4. Signal two (`stylometry.py`) measures the text's shape — sentence-length spread, vocabulary variety, punctuation — and returns `style_score`, also 0–1.
5. `scoring.combine_signals()` merges `model_score` and `style_score` into one `combined_score`.
6. `scoring.score_to_label()` turns that score into a short `guess` (`ai` / `human` / `unsure`) and the full label text a reader sees.
7. The decision is written to the audit log via `audit.log_decision()`, and the response is returned with `content_id`, `guess`, `confidence`, `label`, `model_score`, and `style_score`.

---

## Signals and Scoring

### Signal one — the model signal

**What it measures:** Perplexity — how surprised a local language model (gpt2) is by the text, i.e. how predictable each next word is given what came before. Low perplexity means the model found the text easy to guess; high perplexity means it didn't.

**Why that might differ between human and AI writing:** A language model writes by repeatedly picking a likely next word, so AI-generated text tends to be exactly what a model would predict — low perplexity. Human writing wanders more: odd word choices, abrupt turns, specific rather than typical phrasing.

**What it can't see:** The difference between plainness and authorship. This signal rewards common words in short, ordinary sentences — which plenty of real people write in. Someone writing in a second language, a younger writer, anyone writing simply on purpose, scores about as machine-like as AI writing does. The reverse is also true: dense, rare-word prose often scores human even when AI wrote it, because rare words are what the model fails to predict. The writers this signal is most likely to accuse are the ones with the least room to argue back.

### Signal two — the style signal

**What it measures:** The shape of the text, not its meaning — how much sentence length varies, how varied the vocabulary is (type-token ratio), and how much/what kind of punctuation is used.

**Why that might differ between human and AI writing:** Generated prose tends toward even, mid-length sentences and a narrower band of vocabulary, because that's what "most likely next word" produces on average. Human writing is lumpier — a three-word sentence next to a forty-word one, more idiosyncratic punctuation.

**What it can't see:** This signal cannot read. It has no idea what the text says. Anything that changes the shape without changing the substance moves it — adding typos, breaking up sentences, pasting in a quotation. That's cheap for someone to do on purpose, which is exactly what next unit's attack set will try.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**

**The numbers:**

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human |  |  |
| unsure |  |  |
| high-confidence AI |  |  |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "The sun was setting behind the hills, and for a moment the whole valley looked like it was on fire.", "creator_id": "muskaan"}'
```

```json
{
  "content_id": "a3e12e29-f008-4909-8546-d3110fe06a7c",
  "guess": "placeholder",
  "confidence": 0.0,
  "label": "placeholder",
  "model_score": 0.8552,
  "style_score": 0.0
}
```

<!-- guess/confidence/label are still placeholders as of Milestone 3 — the
     second signal and the real scoring/labeling land in Milestones 4 and 5. -->

**An appeal**

<!-- TODO — /appeal is built in Milestone 5. -->

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.0,
      "content_id": "a2f8e268-6985-4b4b-aa61-415d4270cf60",
      "creator_id": "muskaan",
      "guess": "placeholder",
      "label": "placeholder",
      "model_score": 0.1412,
      "status": "decided",
      "style_score": 0.0,
      "timestamp": "2026-10-28T08:21:54+00:00"
    },
    {
      "combined_score": 0.0,
      "content_id": "a3e12e29-f008-4909-8546-d3110fe06a7c",
      "creator_id": "muskaan",
      "guess": "placeholder",
      "label": "placeholder",
      "model_score": 0.8552,
      "status": "decided",
      "style_score": 0.0,
      "timestamp": "2026-10-28T08:22:09+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

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
