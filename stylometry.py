"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies.

    Returns:
        The standard deviation of sentence lengths (in words) divided by the
        mean, so a long text and a short one are comparable. Higher means
        "more human" — sentences of wildly different lengths. A single
        sentence has no spread to measure, so that case returns 0.0, which
        reads as maximally AI-like on this measure alone (it gets outvoted by
        the other two once style_signal combines them).
    """
    lengths = [len(words(s)) for s in sentences(text)]
    if len(lengths) < 2:
        return 0.0
    mean_length = statistics.mean(lengths)
    if mean_length == 0:
        return 0.0
    return statistics.stdev(lengths) / mean_length


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words.

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary — more
        human-like. An empty text has no words to measure, so that returns
        0.0, same "reads as maximally AI-like alone" reasoning as above.
    """
    ws = words(text)
    if not ws:
        return 0.0
    return len(set(ws)) / len(ws)


def punctuation_density(text: str) -> float:
    """
    How much punctuation, relative to length.

    Returns:
        Count of semicolons, colons, and dashes (em dash, en dash, double
        hyphen) per word. Full stops and commas are left out on purpose —
        nearly every writer uses those, so they don't separate anyone.
        Semicolons and dashes are a style choice, so higher means "more
        human" — a writer with a distinctive habit, not a model defaulting to
        the plainest punctuation that works.
    """
    ws = words(text)
    if not ws:
        return 0.0
    marks = re.findall(r"[;:—–]|--", text)
    return len(marks) / len(ws)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.**

    All three raw measures point toward "more human" when they're higher, so
    each gets flipped and squashed onto 0–1 with `1 / (1 + x)`: a raw value of
    0 (no spread, no punctuation variety at all) flips to 1.0 (maximally
    AI-like), and the score falls toward 0 as the raw value grows. That
    squashing also solves the scaling problem — spread and punctuation density
    are unbounded, but `1 / (1 + x)` always lands between 0 and 1, same range
    as type-token ratio, so no measure dominates just by having bigger raw
    numbers.

    The three flipped scores are averaged with equal weight. Nothing here
    argues one measure should count more than the others.
    """
    spread_ai = 1.0 / (1.0 + sentence_length_spread(text))
    vocab_ai = 1.0 - type_token_ratio(text)
    punct_ai = 1.0 / (1.0 + punctuation_density(text) * 20)

    score = (spread_ai + vocab_ai + punct_ai) / 3.0
    return round(min(max(score, 0.0), 1.0), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
