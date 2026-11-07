"""Independent offline security review tests. No subprocess or host effect."""
import copy
import datetime as dt
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

TASK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TASK / "src"))
import host_adapter as H
import model as M
import store as S
import systemd_codec as C

BOOT = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
SESSION = "1" * 32
SOURCE = "2" * 64


class Clock:
    def __init__(self):
        self.value = 100_000_000
        self.boot_id = BOOT
        self.wall = dt.datetime(2026, 11, 6, 20, 0, tzinfo=dt.timezone.utc)

    def us(self):
        return self.value

    def utc(self):
        return self.wall


def config():
    return {
        "name": "jarvis-g6k-clean-164",
        "smbios1": "uuid=" + M.UUID,
        "scsi0": M.DISK + ",serial=" + M.SERIAL + ",size=64G",
        "ide2": M.ISO + ",media=cdrom",
        "boot": "order=scsi0",
        "hotplug": "0",
        "agent": "0",
        "onboot": "0",
        "protection": "1",
        "serial0": "socket",
        "vga": "std",
        "bios": "seabios",
        "machine": "q35",
        "digest": "3" * 40,
        "cores": 4,
        "sockets": 1,
        "memory": 6000,
        "balloon": 0,
    }


def snapshot(clock, status="stopped"):
    c = config()
    return {
        "node": "pve",
        "vmid": 164,
        "host_boot_id": clock.boot_id,
        "began_us": clock.us() - 100,
        "ended_us": clock.us(),
        "config": c,
        "status": {"vmid": 164, "status": status},
        "pending": [],
        "iso": {
            "volume": M.ISO,
            "sha256": M.ISO_SHA,
            "bytes": 196608,
            "config_digest": c["digest"],
        },
    }


def approval(clock, policy="A"):
    force = None
    if policy == "B":
        force = {
            "policy": "B",
            "vmid": 164,
            "review_sha256": "4" * 64,
            "accepts_disk_loss": True,
            "explicit_forced_termination": True,
        }
    return {
        "format": "vm164-r3-reviewed-authorization",
        "kind": "synthetic",
        "policy": policy,
        "stage": 3,
        "purpose": "non_root_vm164_qualification",
        "operator_reference": "INDEPENDENT-OFFLINE-TEST",
        "review_sha256": "5" * 64,
        "source_sha256": SOURCE,
        "host_boot_id": clock.boot_id,
        "issued_at": "2026-11-06T19:59:00Z",
        "expires_at": "2026-11-06T20:59:00Z",
        "stage2_record_sha256": "6" * 64,
        "command_contract_reviewed": True,
        "forced_stop_authorization": force,
    }


def unit_proof(plan, phase, clock):
    name = plan["names"][phase]
    deadline = plan[phase + "_us"]
    return {
        "host_boot_id": clock.boot_id,
        "observed_us": clock.us(),
        "timer": {
            "id": name + ".timer",
            "load": "loaded",
            "active": "active",
            "sub": "waiting",
            "transient": True,
            "result": "success",
            "trigger": name + ".service",
            "wake": True,
            "accuracy_us": 1,
            "random_us": 0,
            "last_trigger_us": 0,
            "remain": True,
            "on_boot_us": deadline,
            "next_us": deadline,
            "next_boot_min_us": deadline,
            "next_boot_max_us": deadline,
            "readback_clock": "CLOCK_BOOTTIME",
            "readback_offset_low_us": 0,
            "readback_offset_high_us": 0,
        },
        "service": {
            "id": name + ".service",
            "load": "loaded",
            "active": "inactive",
            "sub": "dead",
            "transient": True,
            "result": "success",
            "type": "exec",
            "argv": M.worker_argv(plan["session"], phase),
            "user": "root",
            "group": "root",
            "restart": "no",
            "kill_mode": "control-group",
            "runtime_us": 45_000_000 if phase == "grace" else 30_000_000,
            "stop_timeout_us": 5_000_000,
            "umask": "0077",
            "memory_max": "134217728",
            "tasks_max": "16",
            "send_sigkill": True,
            "stdin": "null",
            "stdout": "journal",
            "stderr": "journal",
            "start_timeout_us": 10_000_000,
            "extra_commands": False,
        },
    }


class Backend:
    def __init__(self, clock, simulated=True):
        self.clock = clock
        self.simulated = simulated
        self.status = "stopped"
        self.plan = None
        self.created = []
        self.cancelled = []
        self.fail_create = None
        self.snapshot_failures = 0
        self.grace_calls = 0
        self.force_calls = 0

    def snapshot(self):
        if self.snapshot_failures:
            self.snapshot_failures -= 1
            raise OSError("injected snapshot failure")
        return snapshot(self.clock, self.status)

    def unit_exists(self, _name):
        return False

    def canary(self, plan):
        self.plan = plan
        return True

    def create_timer(self, plan, phase):
        self.plan = plan
        if phase == self.fail_create:
            raise OSError("injected timer creation failure")
        self.created.append(phase)

    def unit_proof(self, plan, phase):
        return unit_proof(plan, phase, self.clock)

    def start_vm(self):
        self.status = "running"

    def graceful(self):
        self.grace_calls += 1

    def force(self, _grant):
        self.force_calls += 1
        self.status = "stopped"

    def stop_own_units(self, _plan, phase):
        self.cancelled.append(phase)

    def units_inactive(self, _plan, phase):
        return phase in self.cancelled


def prepared(policy="A", simulated=True):
    clock = Clock()
    backend = Backend(clock, simulated=simulated)
    store = S.MemoryStore()
    engine = M.Engine(backend, store, clock, SOURCE)
    engine.prepare(approval(clock, policy), SESSION)
    return clock, backend, store, engine


class IndependentSecurityReview(unittest.TestCase):
    PACKAGE_VERSIONS = {
        "pve-manager": "9.2.5",
        "qemu-server": "9.fixture",
        "pve-qemu-kvm": "10.fixture",
        "systemd": "257.13-1~deb13u1",
    }

    def _authorize_fixture(self, prereq, review, grant, host_clock=None):
        host_clock = host_clock or Clock()
        records = {
            str(H.AUTH): M.canonical(grant),
            str(H.PREREQ): M.canonical(prereq),
            str(H.REVIEW): M.canonical(review),
        }

        def read(path, _limit=0):
            return records.get(str(path), b"reviewed-binary")

        package_raw = "".join(
            name + "=" + self.PACKAGE_VERSIONS[name] + "\n" for name in H.PACKAGES
        ).encode()

        with patch.object(H.os, "getuid", return_value=0), \
             patch.object(H.os, "geteuid", return_value=0), \
             patch.object(H.os, "uname", return_value=SimpleNamespace(release=H.EXPECTED["kernel"])), \
             patch.object(H, "protected", side_effect=lambda path, **_kw: Path(path)), \
             patch.object(H, "bounded_read", side_effect=read), \
             patch.object(H, "source_digest", return_value=SOURCE), \
             patch.object(H, "Clock", return_value=host_clock), \
             patch.object(H, "assess", return_value={"missing": []}), \
             patch.object(H.Path, "lstat", return_value=SimpleNamespace(st_uid=0, st_mode=0o100755)), \
             patch.object(H.Path, "resolve", lambda self, strict=False: self), \
             patch.object(H.Path, "read_text", return_value="pve\n"), \
             patch.object(H.Runner, "run", return_value=package_raw) as run, \
             patch.object(H.subprocess, "Popen", side_effect=AssertionError("Popen tripwire")), \
             patch.object(H.os, "killpg", side_effect=AssertionError("killpg tripwire")):
            result = H.authorize(H.BASE + "/cli.py")
            run.assert_called_once_with(H.PACKAGE_COMMAND, timeout=2)
            return result

    def test_authorization_binds_stage2_and_review_records_and_scope(self):
        clock = Clock()
        prereq = {
            "kind": "reviewed_stage2_host_evidence",
            "source_sha256": SOURCE,
            "package_versions": copy.deepcopy(self.PACKAGE_VERSIONS),
            "binaries": {
                path: {"sha256": M.sha(b"reviewed-binary")} for path in H.BINARIES
            },
        }
        review = {
            "kind": "reviewed_candidate_authorization_record",
            "source_sha256": SOURCE,
            "scope": "stage3_non_root_policy_A_only",
            "stage2_record_sha256": M.sha(M.canonical(prereq)),
        }
        grant = approval(clock)
        grant.update(
            kind="reviewed_host_root",
            stage2_record_sha256=M.sha(M.canonical(prereq)),
            review_sha256=M.sha(M.canonical(review)),
        )
        self.assertIsInstance(self._authorize_fixture(prereq, review, grant), H.Permit)

        changed_prereq = copy.deepcopy(prereq)
        changed_prereq["unexpected"] = True
        with self.assertRaisesRegex(M.Refusal, "stage2_record_hash_mismatch"):
            self._authorize_fixture(changed_prereq, review, grant)

        wrong_scope = copy.deepcopy(review)
        wrong_scope["scope"] = "stage4_root_boot"
        scope_grant = copy.deepcopy(grant)
        scope_grant["review_sha256"] = M.sha(M.canonical(wrong_scope))
        with self.assertRaisesRegex(M.Refusal, "review_record_scope_or_binding"):
            self._authorize_fixture(prereq, wrong_scope, scope_grant)

        synthetic_prereq = copy.deepcopy(prereq)
        synthetic_prereq["kind"] = "synthetic"
        synthetic_review = copy.deepcopy(review)
        synthetic_review["stage2_record_sha256"] = M.sha(M.canonical(synthetic_prereq))
        synthetic_grant = copy.deepcopy(grant)
        synthetic_grant["stage2_record_sha256"] = M.sha(M.canonical(synthetic_prereq))
        synthetic_grant["review_sha256"] = M.sha(M.canonical(synthetic_review))
        with self.assertRaisesRegex(M.Refusal, "synthetic_records_cannot_enable_host_execution"):
            self._authorize_fixture(synthetic_prereq, synthetic_review, synthetic_grant)

        changed_packages = copy.deepcopy(prereq)
        changed_packages["package_versions"]["qemu-server"] = "changed.fixture"
        package_review = copy.deepcopy(review)
        package_review["stage2_record_sha256"] = M.sha(M.canonical(changed_packages))
        package_grant = copy.deepcopy(grant)
        package_grant["stage2_record_sha256"] = M.sha(M.canonical(changed_packages))
        package_grant["review_sha256"] = M.sha(M.canonical(package_review))
        with self.assertRaisesRegex(M.Refusal, "host_package_versions_changed"):
            self._authorize_fixture(changed_packages, package_review, package_grant)

        finite_lease = copy.deepcopy(grant)
        finite_lease["issued_at"] = "2026-11-06T20:00:00Z"
        finite_lease["expires_at"] = "2026-11-06T20:11:00Z"
        callback_clock = Clock()
        callback_clock.wall = dt.datetime(2026, 11, 6, 20, 9, tzinfo=dt.timezone.utc)
        self.assertIsInstance(
            self._authorize_fixture(prereq, review, finite_lease, callback_clock), H.Permit
        )
        with self.assertRaisesRegex(M.Refusal, "stale_or_short_approval"):
            M.validate_approval(
                finite_lease, callback_clock.utc(), callback_clock.boot_id, SOURCE
            )
        expired_clock = Clock()
        expired_clock.wall = dt.datetime(2026, 11, 6, 20, 11, tzinfo=dt.timezone.utc)
        with self.assertRaisesRegex(M.Refusal, "stale_or_short_approval"):
            self._authorize_fixture(prereq, review, finite_lease, expired_clock)

    def test_runtime_policy_b_is_rejected_before_any_backend_action(self):
        clock = Clock()
        backend = Backend(clock, simulated=False)
        engine = M.Engine(backend, S.MemoryStore(), clock, SOURCE)
        with self.assertRaisesRegex(M.Refusal, "B_runtime_disabled"):
            engine.prepare(approval(clock, "B"), SESSION)
        self.assertEqual(backend.created, [])

    def test_active_session_rejects_changed_source_generation_before_action(self):
        clock, backend, store, _engine = prepared("A")
        changed = M.Engine(backend, store, clock, "9" * 64)
        with self.assertRaisesRegex(M.Refusal, "session_source_changed"):
            changed.start()
        stale_worker = M.Engine(
            backend, store, clock, SOURCE, expected_session="2" * 32
        )
        with self.assertRaisesRegex(M.Refusal, "stale_worker_session"):
            stale_worker.start()
        changed_grant = M.Engine(
            backend, store, clock, SOURCE, expected_approval_sha256="f" * 64
        )
        with self.assertRaisesRegex(M.Refusal, "session_approval_changed"):
            changed_grant.start()
        self.assertEqual(backend.status, "stopped")

    def test_file_store_pins_generation_and_worker_idle_barrier(self):
        clock, backend, memory, _engine = prepared("A")
        plan = memory.plan()
        with tempfile.TemporaryDirectory(prefix="jarvis-r3-independent-") as raw:
            os.chmod(raw, 0o700)
            root = Path(raw)
            store = S.FileStore(root)
            with store:
                store.create(plan)

            reopened = S.FileStore(root)
            bound = M.Engine(
                backend,
                reopened,
                clock,
                SOURCE,
                expected_session=SESSION,
                expected_approval_sha256=plan["approval_sha256"],
            )
            self.assertEqual(bound._plan()["session"], SESSION)

            # Simulate an external active-pointer generation change after the
            # exact plan has been authenticated and bound.
            (root / "active.json").write_bytes(M.canonical({"session": "2" * 32}))
            self.assertEqual(reopened.plan()["session"], SESSION)

            self.assertTrue(reopened.claim("grace"))
            with self.assertRaisesRegex(M.Busy, "worker_still_in_flight"):
                reopened.assert_workers_idle()
            reopened.release("grace", False)
            reopened.assert_workers_idle()

    def test_native_adapter_has_no_qm_stop_allowlist_or_force_path(self):
        permit = object.__new__(H.Permit)
        runner = H.Runner(permit, clock=Clock())
        self.assertFalse(runner.allowed(["/usr/sbin/qm", "stop", "164"]))
        backend = object.__new__(H.NativeBackend)
        with self.assertRaisesRegex(M.Refusal, "FORCED_STOP_BUILD_DISABLED"):
            backend.force("4" * 64)

    def test_wrong_vmid_uuid_disk_serial_and_extra_network_refuse(self):
        clock = Clock()
        for mutation in (
            lambda s: s.update(vmid=163),
            lambda s: s["config"].update(smbios1="uuid=" + BOOT),
            lambda s: s["config"].update(scsi0="other:164/disk,serial=" + M.SERIAL + ",size=64G"),
            lambda s: s["config"].update(scsi0=M.DISK + ",serial=wrong,size=64G"),
            lambda s: s["config"].update(net0="virtio"),
        ):
            with self.subTest(mutation=mutation):
                s = snapshot(clock)
                mutation(s)
                with self.assertRaises(M.Refusal):
                    M.validate_snapshot(s, clock.us(), clock.boot_id)

    def test_wrong_iso_agent_boot_pending_and_digest_refuse(self):
        clock = Clock()
        cases = []
        a = snapshot(clock); a["config"]["ide2"] = "none,media=cdrom"; cases.append(a)
        a = snapshot(clock); a["config"]["agent"] = "1"; cases.append(a)
        a = snapshot(clock); a["config"]["boot"] = "order=scsi0;ide2"; cases.append(a)
        a = snapshot(clock); a["pending"] = [{"key": "boot", "pending": "order=scsi0"}]; cases.append(a)
        a = snapshot(clock); a["config"]["digest"] = "7" * 40; cases.append(a)
        for s in cases:
            with self.assertRaises(M.Refusal):
                M.validate_snapshot(s, clock.us(), clock.boot_id, digest="3" * 40)

    def test_timer_inactive_late_wrong_deadline_and_wrong_argv_refuse(self):
        clock, backend, store, _engine = prepared()
        plan = store.plan()
        for mutate in (
            lambda p: p["timer"].update(active="inactive"),
            lambda p: p["timer"].update(next_us=p["timer"]["next_us"] + 1),
            lambda p: p.update(observed_us=clock.us() - 3_000_001),
            lambda p: p["service"].update(argv=["/usr/sbin/qm", "stop", "163"]),
        ):
            proof = unit_proof(plan, "grace", clock)
            mutate(proof)
            with self.assertRaises(M.Refusal):
                M.verify_unit(plan, "grace", proof, clock.us())

    def test_timer_clock_conversion_accepts_historical_suspend_but_rejects_unknown_or_skew(self):
        clock, _backend, store, _engine = prepared()
        plan = store.plan()
        deadline = plan["grace_us"]
        # Legitimate cumulative suspend can greatly exceed the <=1 ms paired
        # sample uncertainty while remaining below this fixture's boot uptime.
        offset_low = 50_000_000
        offset_high = offset_low + 500
        raw = deadline - offset_low
        converted = C.normalize_deadline(
            {"next_us": raw}, "CLOCK_MONOTONIC", offset_low, offset_high
        )
        self.assertEqual(converted["next_boot_min_us"], deadline)
        self.assertEqual(converted["next_boot_max_us"], deadline + 500)

        proof = unit_proof(plan, "grace", clock)
        proof["timer"].update(converted)
        M.verify_unit(plan, "grace", proof, clock.us())

        with self.assertRaisesRegex(M.Refusal, "qualified_readback_clock_required"):
            C.normalize_deadline({"next_us": raw}, "CLOCK_TAI", offset_low, offset_high)
        with self.assertRaisesRegex(M.Refusal, "clock_sample_skew_or_suspend"):
            C.normalize_deadline(
                {"next_us": raw}, "CLOCK_MONOTONIC", offset_low, offset_low + 1001
            )

    def test_weakened_resource_or_stdio_unit_properties_refuse(self):
        clock, _backend, store, _engine = prepared()
        plan = store.plan()
        mutations = (
            lambda service: service.update(umask="0022"),
            lambda service: service.update(memory_max="infinity"),
            lambda service: service.update(tasks_max="infinity"),
            lambda service: service.update(send_sigkill=False),
            lambda service: service.update(stdin="tty"),
            lambda service: service.update(stdout="null"),
            lambda service: service.update(stderr="null"),
            lambda service: service.update(start_timeout_us=0),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                proof = unit_proof(plan, "grace", clock)
                mutate(proof["service"])
                with self.assertRaisesRegex(M.Refusal, "service_resource_or_stdio_contract"):
                    M.verify_unit(plan, "grace", proof, clock.us())

    def test_failed_setup_cancels_every_created_unit_and_verifies_inactive(self):
        clock = Clock()
        backend = Backend(clock)
        backend.fail_create = "deadline"
        engine = M.Engine(backend, S.MemoryStore(), clock, SOURCE)
        with self.assertRaises(OSError):
            engine.prepare(approval(clock), SESSION)
        self.assertEqual(backend.created, ["grace"])
        self.assertIn("grace", backend.cancelled)

    def test_transient_deadline_read_failure_is_retryable(self):
        clock, backend, store, engine = prepared("B")
        backend.status = "running"
        clock.value = store.plan()["deadline_us"]
        backend.snapshot_failures = 1
        with self.assertRaises(OSError):
            engine.expire("deadline")
        result = engine.expire("deadline")
        self.assertEqual(backend.force_calls, 1)
        self.assertEqual(result["status"], "STOPPED_OBSERVED")

    def test_policy_a_never_forces_or_promises_expiration(self):
        clock, backend, store, engine = prepared("A")
        backend.status = "running"
        clock.value = store.plan()["deadline_us"]
        result = engine.expire("deadline")
        self.assertEqual(backend.force_calls, 0)
        self.assertEqual(result["status"], "POLICY_A_NO_EXPIRATION_GUARANTEE")
        self.assertFalse(result["expiration_guaranteed"])

    def test_natural_poweroff_race_needs_fresh_stopped_snapshot(self):
        clock, backend, store, engine = prepared("A")
        backend.status = "running"
        clock.value = store.plan()["grace_us"]

        def race():
            backend.grace_calls += 1
            backend.status = "stopped"

        backend.graceful = race
        result = engine.expire("grace")
        self.assertEqual(result["status"], "STOPPED_OBSERVED")

    def test_duplicate_cleanup_after_closed_performs_no_snapshot_or_unit_action(self):
        clock, backend, _store, engine = prepared("A")
        engine.cleanup()
        backend.snapshot_failures = 1
        before = list(backend.cancelled)
        result = engine.cleanup()
        self.assertEqual(result["status"], "ALREADY_CLOSED_NO_ACTION")
        self.assertEqual(backend.cancelled, before)

    def test_closed_is_absorbing_for_late_expiration_callback(self):
        clock, backend, store, engine = prepared("A")
        engine.cleanup()
        backend.status = "running"
        backend.snapshot_failures = 1
        clock.value = store.plan()["deadline_us"]
        before_events = copy.deepcopy(store.events)
        result = engine.expire("deadline")
        self.assertEqual(result["status"], "ALREADY_CLOSED_NO_ACTION")
        self.assertEqual(store.phase(), "CLOSED")
        self.assertEqual(store.events, before_events)
        self.assertEqual(backend.grace_calls, 0)
        self.assertEqual(backend.force_calls, 0)

    def test_evidence_failure_before_expiration_action_fails_closed(self):
        class FailAfterClaimStore(S.MemoryStore):
            def claim(self, phase):
                result = super().claim(phase)
                self.fail_write = True
                return result

        clock = Clock()
        backend = Backend(clock)
        store = FailAfterClaimStore()
        engine = M.Engine(backend, store, clock, SOURCE)
        engine.prepare(approval(clock), SESSION)
        backend.status = "running"
        clock.value = store.plan()["grace_us"]
        with self.assertRaises(OSError):
            engine.expire("grace")
        self.assertEqual(backend.grace_calls, 0)

    def test_closed_session_has_explicit_evidence_preserving_retirement_path(self):
        clock, _backend, store, engine = prepared("A")
        engine.cleanup()
        with self.assertRaisesRegex(M.Refusal, "new_finite_approval_required"):
            engine.retire(approval(clock))
        new_grant = approval(clock)
        new_grant["operator_reference"] = "INDEPENDENT-OFFLINE-RETIRE"
        result = engine.retire(new_grant)
        self.assertEqual(result["status"], "RETIRED_REGISTRY_EVIDENCE_PRESERVED")
        self.assertIsNone(store.p)
        self.assertEqual(len(store.history), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
