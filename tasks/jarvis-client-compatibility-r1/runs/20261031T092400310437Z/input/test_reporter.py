"""Focused actual reader tests: real disposable Authority, no external sends."""
import asyncio
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch, AsyncMock
import uuid

from app.agent.authority import Authority
from app.agent import runtime
from app.agent.runtime import SERVICE_ACTOR as A
from app.agent.simulation import Simulator
from app.agent import reporter as module

def rid():return str(uuid.uuid4())


class ReporterCompatibility(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='reader-',dir='/work')
        self.path=Path(self.temporary.name)/'state.sqlite'
        self.authority=Authority(self.path,allow_simulation=True)
        runtime.bind_authority(self.authority)
        self.patches=[patch.object(module.psutil,'cpu_percent',return_value=12.5),patch.object(module.psutil,'virtual_memory',return_value=SimpleNamespace(percent=34.5))]
        for item in self.patches:item.start()

    async def asyncTearDown(self):
        runtime.close_authority()
        for item in reversed(self.patches):item.stop()
        self.temporary.cleanup()

    def pending(self):return self.authority.submit(A,rid(),'synthetic inspect')['result']

    async def test_empty_is_a_snapshot_not_general_health(self):
        report=await module.reporter.morning_report()
        self.assertIn('0 pending (admitted, execution held)',report)
        self.assertIn('UNKNOWN 0',report)
        self.assertNotIn('All systems',report)

    async def test_pending_is_admitted_held_and_reporting_is_read_only(self):
        task=self.pending()
        before=self.authority.list_tasks(A)
        count=self.authority._conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]
        report=await module.reporter.build_report()
        self.assertIn('CPU 12.5',report);self.assertIn('RAM 34.5',report)
        self.assertIn('1 pending (admitted, execution held)',report)
        self.assertEqual(self.authority.list_tasks(A),before)
        self.assertEqual(self.authority._conn.execute('SELECT COUNT(*) FROM events').fetchone()[0],count)
        self.assertEqual(module.reporter._task_snapshot()[0].task_id,task['task_id'])
        self.assertEqual(len(task['task_id']),36)

    async def test_cancelled_keeps_state_and_flag(self):
        task=self.pending();self.authority.cancel(A,rid(),task['task_id'])
        report=await module.reporter.build_report()
        self.assertIn('cancel_requested 1',report)
        self.assertIn('cancelled=1',report)
        self.assertIn('0 pending',report)

    async def test_claimed_cancellation_is_not_confirmed_prevention(self):
        task=self.pending();Simulator(self.authority).claim(A,rid(),task['task_id'])
        self.authority.cancel(A,rid(),task['task_id'])
        report=await module.reporter.morning_report()
        self.assertIn('simulating=1',report);self.assertIn('cancel_requested 1',report)
        self.assertNotIn('cancelled=1',report);self.assertNotIn('tasks running',report)

    async def test_legacy_unknown_cannot_disappear_in_morning_report(self):
        self.authority.import_legacy_snapshot(A,rid(),tasks=[{'task_id':'legacy','goal':'old','status':'completed'}],schedules=[],evidence={})
        report=await module.reporter.morning_report()
        self.assertIn('UNKNOWN 1',report)
        self.assertNotIn('completed=1',report);self.assertNotIn('nominal',report)

    async def test_recovered_unknown_retains_cancellation_uncertainty(self):
        task=self.pending();Simulator(self.authority).claim(A,rid(),task['task_id'])
        self.authority.cancel(A,rid(),task['task_id'])
        runtime.close_authority()
        self.authority=Authority(self.path,allow_simulation=True)
        runtime.bind_authority(self.authority)
        report=await module.reporter.build_report()
        self.assertIn('UNKNOWN 1',report);self.assertIn('cancel_requested 1',report)
        self.assertNotIn('cancelled=1',report)

    async def test_simulation_completion_is_named_without_real_execution_claim(self):
        task=self.pending();sim=Simulator(self.authority)
        claim=sim.claim(A,rid(),task['task_id'])['result']
        sim.apply(A,rid(),**claim);sim.acknowledge(A,rid(),**claim)
        report=await module.reporter.build_report()
        self.assertIn('simulated_completed=1',report)
        self.assertNotIn('tasks running',report)

    async def test_unavailable_never_falls_back_to_empty_legacy_memory(self):
        self.pending();self.authority._poisoned=True
        report=await module.reporter.build_report()
        self.assertIn('Task state unavailable; reconciliation required',report)
        self.assertNotIn('UNKNOWN 0',report);self.assertNotIn('0 pending',report)

    async def test_disabled_comms_send_report_does_not_send_anything(self):
        self.assertFalse(module.settings.comms.discord_enabled)
        self.assertFalse(module.settings.comms.telegram_enabled)
        with patch.object(module.discord_bot,'send_status',new_callable=AsyncMock) as discord,patch.object(module.telegram_bot,'send_status',new_callable=AsyncMock) as telegram:
            result=await module.reporter.send_report()
            self.assertIsNone(result['discord']);self.assertIsNone(result['telegram'])
            discord.assert_not_awaited();telegram.assert_not_awaited()
            self.assertIn('UNKNOWN 0',result['report'])
