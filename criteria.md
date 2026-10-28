# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. False positives

Of 10 pieces of plainly-written human text I submit myself, at most 1 is labeled high-confidence AI.

**Why this target:** On a writing site, wrongly accusing a real writer costs more than missing some AI text — a false accusation damages trust in a way a missed detection doesn't.

---

## 2. Score spread

Clearly-AI text (raw model output) scores at least 0.3 higher on the combined score than clearly-human text, in all three trials.

**Why this target:** If obvious cases don't separate clearly, the combined score carries no information — the two signals should at least agree on the easy cases, leaving genuine ambiguity for the hard ones.

---

## 3. Label coverage

Across 10 varied test texts, all three labels (high-confidence human, unsure, high-confidence AI) are each produced at least once.

**Why this target:** My thresholds (0.35 and 0.65 in config.py) only work if all three bands are actually reachable by real scores. If my combining rule or either signal clustered scores into a narrow range, the unsure band could end up empty, and a writer who deserves a cautious "we're not sure" would get a harder verdict instead. That's a specific failure mode of my scoring pipeline, not just a general design worry.

---

## 4. The appeal path

100% of appeals submitted with a valid content_id move that item's status to under_review and appear in the audit log, with no exceptions across testing.

**Why this target:** My combining rule already leans 70% toward the human-reading signal when the two disagree, specifically to cut down on false accusations. That design choice only protects anyone if the one remaining safety net, the appeal, actually works every single time. If even one real appeal silently failed to log or change status, a wrongly-accused writer would have no way to be heard, which is exactly the harm my Milestone 1 false-positive trace was built around.

---

## 5. Bad input

Submitting missing, empty, or oversized text never returns a 500 — each case returns a specific error response instead.

**Why this target:** My first signal (detector.model_signal) raises an error on text shorter than three tokens, so missing or empty text could crash the whole request before a label is ever produced. A crash there doesn't just fail loudly, it leaves a writer with no response at all, which is worse than getting an unsure label or a plain error message telling them what went wrong.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
