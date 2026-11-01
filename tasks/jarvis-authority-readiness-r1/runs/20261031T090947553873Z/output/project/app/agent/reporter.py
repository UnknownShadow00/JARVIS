from __future__ import annotations

import asyncio

import psutil

from app.agent.task_queue import task_queue
from app.comms.discord_bot import discord_bot
from app.comms.telegram_bot import telegram_bot
from app.config import settings
from app.logs.audit import audit


class Reporter:
    def _task_snapshot(self) -> list[object]:
        tasks = getattr(task_queue, "tasks", None)
        if tasks is not None:
            return list(tasks)

        stored_tasks = getattr(task_queue, "_tasks", {})
        if isinstance(stored_tasks, dict):
            return list(stored_tasks.values())

        return []

    def _stats(self) -> tuple[float, float, int, int]:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        tasks = self._task_snapshot()
        pending = len([task for task in tasks if getattr(task, "status", None) == "pending"])
        active = len([task for task in tasks if getattr(task, "status", None) == "in_progress"])
        return cpu, ram, active, pending

    async def build_report(self) -> str:
        cpu, ram, active, pending = self._stats()
        return f"JARVIS status: CPU {cpu}% | RAM {ram}% | Tasks {active} active, {pending} pending."

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
        cpu, ram, active, pending = self._stats()
        return (
            f"Good morning, sir. CPU {cpu}%, RAM {ram}%. "
            f"{active} tasks running, {pending} pending. All systems nominal."
        )


reporter = Reporter()
