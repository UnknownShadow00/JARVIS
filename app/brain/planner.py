from __future__ import annotations

import asyncio
import inspect
import json
from dataclasses import dataclass
from typing import Any

from app.brain.llm_client import OllamaConnectionError, llm_client
from app.logs.audit import audit


@dataclass
class TaskPlan:
    goal: str
    steps: list[str]
    tool_hints: list[str]
    estimated_turns: int


class Planner:
    def plan(self, goal: str, context: str = "") -> TaskPlan:
        fallback = self._fallback_plan(goal)

        if not goal.strip():
            audit.log("planner_fallback", {"goal": goal, "reason": "empty_goal"})
            return fallback

        prompt = self._build_messages(goal, context)

        try:
            raw_response = self._call_llm(prompt)
        except OllamaConnectionError:
            audit.log("planner_fallback", {"goal": goal, "reason": "ollama_offline"})
            return fallback
        except Exception as exc:
            audit.log(
                "planner_fallback",
                {"goal": goal, "reason": "llm_error", "error": str(exc)},
            )
            return fallback

        try:
            plan = self._parse_plan(raw_response)
        except Exception as exc:
            audit.log(
                "planner_fallback",
                {"goal": goal, "reason": "parse_error", "error": str(exc)},
            )
            return fallback

        audit.log(
            "planner_plan_created",
            {"goal": goal, "step_count": len(plan.steps), "estimated_turns": plan.estimated_turns},
        )
        return plan

    def _call_llm(self, messages: list[dict[str, str]]) -> str:
        result = llm_client.chat(messages)
        if inspect.isawaitable(result):
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                return str(asyncio.run(result))
            raise RuntimeError("event_loop_running")
        return str(result)

    def _build_messages(self, goal: str, context: str) -> list[dict[str, str]]:
        system_prompt = (
            "You are a task planner for JARVIS. Decompose the user's goal into ordered steps. "
            "Respond ONLY with valid JSON, no markdown, no commentary. "
            "Format: {'goal': str, 'steps': [str, ...], 'tool_hints': [str, ...], 'estimated_turns': int}"
        )
        user_prompt = f"Goal: {goal.strip()}\nContext: {context.strip()}"
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _parse_plan(self, raw_response: str) -> TaskPlan:
        data = json.loads(raw_response)
        if not isinstance(data, dict):
            raise ValueError("Planner response must be a JSON object.")

        goal = str(data["goal"])
        steps = data["steps"]
        tool_hints = data["tool_hints"]
        estimated_turns = int(data["estimated_turns"])

        if not isinstance(steps, list) or not all(isinstance(step, str) for step in steps):
            raise ValueError("Planner steps must be a list of strings.")
        if not isinstance(tool_hints, list) or not all(isinstance(hint, str) for hint in tool_hints):
            raise ValueError("Planner tool_hints must be a list of strings.")
        if estimated_turns < 1:
            raise ValueError("Planner estimated_turns must be positive.")

        return TaskPlan(
            goal=goal,
            steps=steps,
            tool_hints=tool_hints,
            estimated_turns=estimated_turns,
        )

    def _fallback_plan(self, goal: str) -> TaskPlan:
        return TaskPlan(
            goal=goal,
            steps=[goal],
            tool_hints=[],
            estimated_turns=1,
        )


planner = Planner()
