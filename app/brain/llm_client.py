from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.config import settings
from app.logs.audit import audit

class OllamaConnectionError(Exception):
    """Raised when the Ollama service cannot be reached."""


class LLMClient:
    def __init__(self) -> None:
        self._host = settings.models.ollama_base_url

    async def chat(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        stream: bool = False,
    ) -> str | AsyncGenerator[str, None]:
        target_model = model or settings.models.main
        return await self._chat_with_model(target_model, messages, stream=stream)

    async def code(
        self,
        messages: list[dict[str, Any]],
        stream: bool = False,
    ) -> str | AsyncGenerator[str, None]:
        return await self._chat_with_model(settings.models.coder, messages, stream=stream)

    async def vision(
        self,
        messages: list[dict[str, Any]],
        images: list[Any] | None = None,
    ) -> str:
        target_model = settings.models.vision
        payload = self._normalize_messages(messages, images=images)

        audit.log(
            "llm_call",
            {"model": target_model, "message_count": len(payload)},
        )

        try:
            response = await self._call_chat(
                model=target_model,
                messages=payload,
                stream=False,
            )
        except self._connection_exceptions() as exc:
            raise OllamaConnectionError(
                f"Unable to connect to Ollama at {self._host} for model '{target_model}'."
            ) from exc

        content = self._extract_message_content(response)
        audit.log(
            "llm_response",
            {"model": target_model, "response_length": len(content)},
        )
        return content

    def _suppress_thinking(
        self,
        messages: list[dict[str, Any]],
        model: str,
    ) -> list[dict[str, Any]]:
        if not model.startswith("qwen3"):
            return messages
        result = list(messages)
        for i in range(len(result) - 1, -1, -1):
            if result[i].get("role") == "user":
                msg = dict(result[i])
                content = str(msg.get("content", ""))
                if not content.startswith("/no_think"):
                    msg["content"] = f"/no_think\n{content}"
                result[i] = msg
                break
        return result

    async def _chat_with_model(
        self,
        model: str,
        messages: list[dict[str, Any]],
        *,
        stream: bool,
    ) -> str | AsyncGenerator[str, None]:
        payload = self._normalize_messages(messages)
        payload = self._suppress_thinking(payload, model)
        audit.log("llm_call", {"model": model, "message_count": len(payload)})

        if stream:
            return self._stream_response(model, payload)

        try:
            response = await self._call_chat(model=model, messages=payload, stream=False)
        except self._connection_exceptions() as exc:
            raise OllamaConnectionError(
                f"Unable to connect to Ollama at {self._host} for model '{model}'."
            ) from exc

        content = self._extract_message_content(response)
        audit.log("llm_response", {"model": model, "response_length": len(content)})
        return content

    def _build_payload(
        self,
        model: str,
        messages: list[dict[str, Any]],
        stream: bool,
    ) -> dict[str, Any]:
        return {
            "model": model,
            "messages": messages,
            "stream": stream,
            "think": False,
            "options": {"num_predict": 120},
        }

    async def _call_chat(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        stream: bool,
    ) -> Any:
        payload = self._build_payload(model, messages, stream=False)
        url = f"{self._host}/api/chat"
        async with httpx.AsyncClient(timeout=httpx.Timeout(600.0)) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    async def _stream_response(
        self,
        model: str,
        messages: list[dict[str, Any]],
    ) -> AsyncGenerator[str, None]:
        import json as _json

        payload = self._build_payload(model, messages, stream=True)
        url = f"{self._host}/api/chat"
        chunks: list[str] = []

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(600.0)) as client:
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            chunk = _json.loads(line)
                            content = self._extract_message_content(chunk)
                            if content:
                                chunks.append(content)
                                yield content
        except self._connection_exceptions() as exc:
            raise OllamaConnectionError(
                f"Streaming response from Ollama at {self._host} failed for model '{model}'."
            ) from exc
        finally:
            audit.log(
                "llm_response",
                {"model": model, "response_length": len("".join(chunks))},
            )

    def _normalize_messages(
        self,
        messages: list[dict[str, Any]],
        *,
        images: list[Any] | None = None,
    ) -> list[dict[str, Any]]:
        payload: list[dict[str, Any]] = [dict(message) for message in messages]

        if images is not None and payload:
            payload[-1] = dict(payload[-1])
            payload[-1]["images"] = list(images)

        return payload

    def _extract_message_content(self, response: Any) -> str:
        if response is None:
            return ""

        if isinstance(response, dict):
            message = response.get("message")
            if isinstance(message, dict):
                return str(message.get("content", "") or "")
            return str(response.get("response", "") or "")

        message = getattr(response, "message", None)
        if message is not None:
            content = getattr(message, "content", "")
            if content is not None:
                return str(content)

        content = getattr(response, "response", "")
        return str(content or "")

    def _connection_exceptions(self) -> tuple[type[BaseException], ...]:
        return (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadError,
            httpx.ReadTimeout,
            httpx.NetworkError,
            httpx.HTTPStatusError,
            OSError,
        )


llm_client = LLMClient()
