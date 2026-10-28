# Milestone 1 — design notes

Written before any of `/submit`, `/appeal`, or `stylometry.py` exist. The path
and the two signal write-ups live in README.md now; the two pieces below don't
have a README slot yet, so they're parked here until the thresholds
(Milestone 5) and the route (Milestone 3) actually need them.

## Tracing the false positive

A student writes a poem themselves, in plain, simple English — maybe it's
their second language. They submit it through `/submit`.

Signal one reads short, common-word sentences as highly predictable, so it
leans AI. If their sentences also happen to be fairly even in length, signal
two doesn't rescue them either. The combined score lands in the AI range, and
what comes back is a label that flatly says something like "we think this was
AI-generated."

That's wrong, and it costs them something real. Their only recourse is
`POST /appeal` with their reasoning, which moves the item to `under_review`
for a person to look at — nothing reverses the label automatically, and if
nobody ever reviews the queue, the accusation just sits there.

**What this means for later milestones:** the "high-confidence AI" threshold
needs to be hard to reach by accident, and the "unsure" band needs to be wide
enough to catch plain-but-human writing instead of letting it tip into the AI
bucket.

## Endpoint contracts

### POST /submit

```
in:  { "text": string, "creator_id": string }
out: { "content_id": string,
       "guess": "ai" | "human" | "unsure",
       "confidence": float (0.0-1.0),
       "label": string,
       "model_score": float (0.0-1.0),
       "style_score": float (0.0-1.0) }
```

### POST /appeal

```
in:  { "content_id": string, "reasoning": string }
out: { "ok": true,
       "content_id": string,
       "status": "under_review",
       "message": string }
```

404 if `content_id` doesn't match anything in the audit log.
