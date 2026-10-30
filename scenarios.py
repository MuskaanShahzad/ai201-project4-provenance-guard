"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        # Ten things I actually wrote myself: real emails, texts, and messages
        # pulled from my own correspondence, not generated or borrowed.
        "texts": [
            "While trying to enroll in my benefits, I noticed that my gender is incorrectly listed as male. Could you please update it to female? I've attached a screenshot for your reference. Please let me know if you need any additional information from me to make this correction. Thank you for your help!",
            "i am trying to make a payment for my parking fee and registered for the curb pass account so the administrative fee would be waived as stated on the site but it keeps on adding minimum $5 to add funds to curbpass. I do not want to add any funds and just pay what I owe. Please assist with this, thank you!",
            "Thank you, I'll do that but it also says that it will autofill the wallet if the balance drops and I don't want my credit card to be on file. Can you please advise on this? Thank you!",
            "I've attached screenshots of my selected flights for reference. I may not have a TSA PreCheck/Known Traveler Number or a frequent flyer number. Please let me know if you need any additional information to complete the booking.",
            "I'll see you in San Francisco! I'm looking forward to finally meeting you in person and getting to connect again.",
            "Attached is the speed test result, thank you!",
            "Thank you for your kind message, I really appreciate you taking the time to review my resume. I'm glad to hear my experience aligns with your team's work.",
            "Thank you, Justin! I appreciate it. Looking forward to speaking with you tomorrow!",
            "I hope you've been doing well. I wanted to follow up regarding our conversation from March. I completely understand that things were still being finalised at the time, and I just wanted to check if there have been any updates on the role.",
            "I hope you are well. I was traveling and unable to respond earlier.",
        ],
    },
    {
        "name": "score spread",
        "criterion": 2,
        # One clearly-AI paragraph (the kind of generic, hedge-everything prose
        # a model defaults to) and one clearly-human paragraph (specific,
        # lumpy, nobody would generate this on purpose), to check the gap
        # between them.
        "texts": [
            "The implementation of the proposed framework requires careful consideration of several key factors. First, it is important to note that the system must be able to handle a wide variety of different inputs. Additionally, the overall performance of the solution depends on a number of important variables.",
            "Grandma's kitchen always smelled like burnt cinnamon. She forgot the toast again this morning, muttering at the smoke alarm like it owed her money. I don't think that woman has made a slice of toast without setting something off in thirty years, and honestly? I'd miss it if she ever did.",
        ],
    },
    {
        "name": "label coverage",
        "criterion": 3,
        # Ten varied texts spread across the range: generic AI-sounding
        # paragraphs, genuinely human writing (casual and formal), and a
        # couple of deliberately borderline ones.
        "texts": [
            "The implementation of the proposed framework requires careful consideration of several key factors. First, it is important to note that the system must be able to handle a wide variety of different inputs. Additionally, the overall performance of the solution depends on a number of important variables.",
            "Grandma's kitchen always smelled like burnt cinnamon. She forgot the toast again this morning, muttering at the smoke alarm like it owed her money. I don't think that woman has made a slice of toast without setting something off in thirty years, and honestly? I'd miss it if she ever did.",
            "I went to the store yesterday and bought some milk and bread. It was a quiet afternoon and nothing much happened, just a regular trip to run errands.",
            "I'll see you in San Francisco! I'm looking forward to finally meeting you in person and getting to connect again.",
            "Thank you, Justin! I appreciate it. Looking forward to speaking with you tomorrow!",
            "Utilizing a cloud-based infrastructure enables organizations to achieve significant improvements in scalability, reliability, and overall operational efficiency across distributed systems.",
            "The system works well. It handles most cases correctly and provides good results. Users generally find it easy to use and understand.",
            "Autumn arrived quietly that year, the way it always had, with the maples turning first and the neighborhood kids tracking leaves into every hallway they could find.",
            "Please find attached the requested documentation for your review. Should you require any further information, do not hesitate to contact our support team at your earliest convenience.",
            "honestly idk, today was kind of a mess lol. forgot my keys, missed the bus, then spilled coffee on my shirt right before the meeting. classic tuesday i guess",
        ],
    },
    {
        "name": "bad input",
        "criterion": 5,
        # Raw request bodies, sent exactly as written: empty text, no text
        # field at all, something enormous, and a null.
        "bodies": [
            {"text": "", "creator_id": "eval_bad_empty"},
            {"creator_id": "eval_bad_missing"},          # no text field at all
            {"text": "word " * 50000, "creator_id": "eval_bad_huge"},
            {"text": None, "creator_id": "eval_bad_null"},
            {"text": "   ", "creator_id": "eval_bad_whitespace"},
        ],
    },

    # Criterion 4 (the appeal path) isn't here. run_eval.py only POSTs to
    # /submit, and this criterion needs a submission first and then an appeal
    # against the real content_id that came back, which this file can't
    # express. I tested it by hand with curl instead: three trials, five
    # submit-then-appeal pairs each. See the README for that output.
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
