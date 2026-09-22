"""Static, independent corpus-label check; never imports production or a provider."""
import json
import math
from pathlib import Path


def pairs(items):
    assert len(items) == len({key for key, _ in items})
    return dict(items)


def invalid_constant(_):
    raise ValueError("non-JSON constant")


def admissible(value):
    forbidden = {
        "reasoning", "thinking", "chainofthought", "modelchainofthought",
        "hiddenreasoning", "privatehiddenreasoning", "scratchpad",
        "modelinternalreasoning", "internalreasoning", "reasoningcontent",
        "innermonologue",
    }
    if isinstance(value, dict):
        return all(
            "".join(c for c in k.lower() if c.isalnum()) not in forbidden
            and admissible(v) for k, v in value.items()
        )
    if isinstance(value, list):
        return all(map(admissible, value))
    return not isinstance(value, float) or math.isfinite(value)


def inspect(raw):
    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)
        assert type(value) is dict and set(value) == {"text", "proposals"}
        assert type(value["text"]) is str and type(value["proposals"]) is list
        assert admissible(value)
        for proposal in value["proposals"]:
            assert type(proposal) is dict
            assert set(proposal) == {"tool_name", "raw_arguments"}
            assert type(proposal["tool_name"]) is str and proposal["tool_name"].strip()
            assert type(proposal["raw_arguments"]) is dict
        return True, len(value["proposals"])
    except (ValueError, AssertionError):
        return False, 0


if __name__ == "__main__":
    corpus = json.loads(Path(__file__).with_name("contract-corpus.json").read_text())
    identifiers = [case["id"] for case in corpus["cases"]]
    assert len(set(identifiers)) == len(identifiers)
    for case in corpus["cases"]:
        actual = inspect(case["raw"])
        assert actual == (case["valid"], case["proposal_count"]), case["id"]
    print(f"PASS: {len(identifiers)} corpus labels; no production import or execution")
