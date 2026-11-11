"""Owned APScheduler cleanup for JARVIS's coroutine callbacks.

APScheduler 3.x's public shutdown only queues cleanup, and its STOPPED state is
set before resources close. Keep per-resource completion instead of using that
state as evidence. This adapter deliberately supports the installed 3.x APIs.
"""
import asyncio
import inspect

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.events import EVENT_SCHEDULER_SHUTDOWN, SchedulerEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.base import STATE_STOPPED

from app.agent.authority import AuthorityError


class OwnedAsyncIOScheduler(AsyncIOScheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cleanup_resources = None
        self._cleanup_done = set()
        self._cleanup_futures = set()
        self._cleanup_complete = False

    def start(self, paused=False):
        if self._cleanup_resources is not None:
            raise AuthorityError('scheduler_backend_closed')
        super().start(paused)

    def shutdown(self, wait=True):
        raise AuthorityError('scheduler_async_cleanup_required')

    async def aclose(self):
        if self._cleanup_complete:
            return
        if self._eventloop is not None and self._eventloop is not asyncio.get_running_loop():
            raise AuthorityError('scheduler_cleanup_wrong_loop')
        # Stop new dispatch first. STOPPED is a fence, not cleanup evidence.
        self.state = STATE_STOPPED
        self._stop_timer()
        if self._cleanup_resources is None:
            with self._executors_lock, self._jobstores_lock:
                self._cleanup_resources = [
                    ('executor', value) for value in self._executors.values()
                ] + [('store', value) for value in self._jobstores.values()]
        for index, (kind, value) in enumerate(self._cleanup_resources):
            if kind != 'executor' or index in self._cleanup_done:
                continue
            if type(value) is not AsyncIOExecutor:
                raise AuthorityError('scheduler_cleanup_unverifiable')
            futures = set(getattr(value, '_pending_futures', ()))
            # JARVIS registers coroutine callbacks only. Cancellation of an
            # executor Future cannot prove an underlying thread has exited.
            if any(not future.done() and not isinstance(future, asyncio.Task) for future in futures):
                raise AuthorityError('scheduler_cleanup_unverifiable')
            self._cleanup_futures.update(futures)
            result = value.shutdown(wait=False)
            if inspect.isawaitable(result):
                await result
            self._cleanup_done.add(index)
        pending = {future for future in self._cleanup_futures if not future.done()}
        if pending:
            # The owner supplies the timeout. Cancellation never discards this
            # inventory; a later close can confirm tasks that finish afterward.
            await asyncio.wait(pending)
        for index, (kind, value) in enumerate(self._cleanup_resources):
            if kind != 'store' or index in self._cleanup_done:
                continue
            if type(value) is not MemoryJobStore:
                raise AuthorityError('scheduler_cleanup_unverifiable')
            result = value.shutdown()
            if inspect.isawaitable(result):
                await result
            self._cleanup_done.add(index)
        self._eventloop = None
        self._cleanup_complete = True
        self._dispatch_event(SchedulerEvent(EVENT_SCHEDULER_SHUTDOWN))
