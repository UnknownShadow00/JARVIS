from __future__ import annotations

import asyncio

import psutil

from app.agent.authority import AuthorityError
from app.agent.task_queue import task_queue
from app.comms.discord_bot import discord_bot
from app.comms.telegram_bot import telegram_bot
from app.config import settings
from app.logs.audit import audit


class Reporter:
    def _task_snapshot(self) -> list[object]:
        return list(task_queue.tasks)

    def _stats(self) -> tuple[float, float, str]:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        try:
            tasks = self._task_snapshot()
        except AuthorityError:
            return cpu, ram, "Task state unavailable; reconciliation required."
        counts: dict[str, int] = {}
        for task in tasks:
            counts[task.status] = counts.get(task.status, 0) + 1
        summary = (
            f"Tasks {counts.pop('in_progress', 0)} in progress, "
            f"{counts.pop('pending', 0)} pending (admitted, execution held); "
            f"UNKNOWN {counts.pop('unknown', 0)}; "
            f"cancel_requested {sum(task.cancel_requested for task in tasks)}."
        )
        if counts:
            # Preserve actual states, including simulated_completed/simulating.
            # They are never represented as real execution or completed work.
            summary += " Other task states: " + ", ".join(f"{state}={count}" for state, count in sorted(counts.items())) + "."
        return cpu, ram, summary

    async def build_report(self) -> str:
        cpu, ram, tasks = self._stats()
        return f"JARVIS status: CPU {cpu}% | RAM {ram}% | {tasks}"

    async def send_report(self) -> dict:
        report = await self.build_report()
        discord_result = None
        telegram_result = None
        senders: list[asyncio.Future] = []

        if settings.comms.discord_enabled:
            senders.append(discord_bot.send_status(report))
        if settings.comms.telegram_enabled:
            senders.append(telegram_bot.send_status(report))

        if senders:
            results = await asyncio.gather(*senders)
            index = 0
            if settings.comms.discord_enabled:
                discord_result = results[index]
                index += 1
            if settings.comms.telegram_enabled:
                telegram_result = results[index]

        audit.log("status_report_sent", {"report": report})
        return {
            "report": report,
            "discord": discord_result,
            "telegram": telegram_result,
        }

    async def morning_report(self) -> str:
        cpu, ram, tasks = self._stats()
        return (
            f"Good morning, sir. CPU {cpu}%, RAM {ram}%. "
            f"{tasks}"
        )


reporter = Reporter()
