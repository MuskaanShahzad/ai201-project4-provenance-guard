#!/usr/bin/env python3
"""
Criterion 4 (the appeal path), tested by hand. ← UNIT 8, MILESTONE 3

`run_eval.py` only posts to /submit, so it can't test the appeal path: that
needs a real submission first, then an appeal against the content_id that
came back. This script does exactly that, three trials of five pairs each,
and writes results/appeal_test_<label>.json.

    python app.py                        # in one terminal
    python test_appeal.py before         # in another
"""

import json
import sys

import requests

import config

URL = f"http://{config.HOST}:{config.PORT}"

TEXTS = [
    "Thank you, Justin! I appreciate it. Looking forward to speaking with you tomorrow!",
    "I hope you are well. I was traveling and unable to respond earlier.",
    "Attached is the speed test result, thank you!",
    "I'll see you in San Francisco! I'm looking forward to finally meeting up again.",
    "I hope you've been doing well. I wanted to follow up regarding our conversation.",
]


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else ""

    all_trials = []
    for trial in range(1, 4):
        results = []
        for i, text in enumerate(TEXTS, 1):
            creator_id = f"eval_appeal_t{trial}_{i}"
            submit_resp = requests.post(f"{URL}/submit", json={"text": text, "creator_id": creator_id})
            content_id = submit_resp.json().get("content_id")

            appeal_resp = requests.post(f"{URL}/appeal", json={
                "content_id": content_id,
                "reasoning": "I wrote this myself; testing the appeal path for criterion 4.",
            })
            appeal_json = appeal_resp.json()

            results.append({
                "content_id": content_id,
                "appeal_status_code": appeal_resp.status_code,
                "appeal_response": appeal_json,
            })

        held = sum(
            1 for r in results
            if r["appeal_status_code"] == 200 and r["appeal_response"].get("status") == "under_review"
        )
        print(f"trial {trial}: {held}/5 appeals changed status to under_review")
        all_trials.append(results)

    config.RESULTS_DIR.mkdir(exist_ok=True)
    suffix = f"_{label}" if label else ""
    path = config.RESULTS_DIR / f"appeal_test{suffix}.json"
    path.write_text(json.dumps(all_trials, indent=2), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
