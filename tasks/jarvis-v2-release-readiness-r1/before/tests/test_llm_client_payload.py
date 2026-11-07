from __future__ import annotations

from app.brain.llm_client import LLMClient


def test_no_think_payload_defaults() -> None:
    client = LLMClient()

    payload = client._build_payload("qwen3-nothink", [{"role": "user", "content": "hello"}], False)

    assert payload["think"] is False
    assert payload["options"]["num_predict"] == 150


def test_deep_payload_can_enable_thinking() -> None:
    client = LLMClient()

    payload = client._build_payload(
        "qwen3:14b",
        [{"role": "user", "content": "debug this"}],
        False,
        think=True,
        num_predict=700,
    )

    assert payload["think"] is True
    assert payload["options"]["num_predict"] == 700
