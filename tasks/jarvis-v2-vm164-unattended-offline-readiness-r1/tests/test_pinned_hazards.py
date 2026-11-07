"""Reproduce pinned-packet gaps without changing it; every manager call mocked.

These passing tests CONFIRM hazards, not successful remediation of the old packet.
"""
import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

TASK = Path(__file__).resolve().parents[1]
OLD = TASK.parent / "jarvis-v2-vm164-trusted-bootstrap-r1"


def load(name, path):
    spec = importlib.util.spec_from_file_location(
        name, path, loader=importlib.machinery.SourceFileLoader(name, str(path)))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = load("pinned_boot_for_review", OLD / "payload/BOOT.PY")
H = load("pinned_host_for_review", OLD / "tools/host_guard.py")


def config():
    return {"smbios1": "uuid=" + B.UUID, "scsi0": H.VOLUME + ",serial=" + B.SERIAL + ",size=64G",
            "ide2": "none,media=cdrom", "boot": "order=scsi0", "onboot": 0,
            "agent": "0", "serial0": "socket", "vga": "std", "hotplug": "0",
            "protection": 1, "digest": "a" * 40, "cores": 4, "memory": 6000, "balloon": 0}


def host(c, iso="local:iso/vm164-trusted-bootstrap-fd91b8b07243565e.iso", phase="empty", pending=None):
    return H.validate(c, {"vmid": 164, "status": "stopped"}, pending or [],
                      phase=phase, iso_volume=iso, expect_status="stopped")


class PinnedHazards(unittest.TestCase):
    def test_official_guard_rejects_reported_auto_boot_change(self):
        c = config()
        c["boot"] = "order=scsi0;ide2"
        with self.assertRaisesRegex(ValueError, "DISK_ONLY_MANUAL_BOOT"):
            host(c)

    def test_official_guard_accepts_unpinned_hash_shaped_iso(self):
        c = config()
        iso = "local:iso/vm164-trusted-bootstrap-0000000000000000.iso"
        c["ide2"] = iso + ",media=cdrom"
        self.assertEqual(host(c, iso=iso, phase="attached")["status"], "PASS_HOST_READBACK_ONLY")

    def test_official_guard_defaults_absent_agent_and_vga(self):
        c = config()
        del c["agent"]
        del c["vga"]
        self.assertEqual(host(c)["status"], "PASS_HOST_READBACK_ONLY")

    def test_official_guard_accepts_duplicate_conflicting_disk_serial(self):
        c = config()
        c["scsi0"] += ",serial=unexpected"
        self.assertEqual(host(c)["status"], "PASS_HOST_READBACK_ONLY")

    def test_official_guard_accepts_unchecked_extra_device(self):
        c = config()
        c["efidisk0"] = "unexpected:164/extra"
        self.assertEqual(host(c)["status"], "PASS_HOST_READBACK_ONLY")

    def test_official_guard_accepts_malformed_pending_row(self):
        self.assertEqual(host(config(), pending=[{}])["status"], "PASS_HOST_READBACK_ONLY")

    def test_close_state_read_failure_has_no_poweroff_fallback(self):
        with tempfile.TemporaryDirectory(dir=TASK / "evidence") as tmp:
            with patch.object(B, "RAM", Path(tmp)), patch.object(B, "command") as cmd:
                with self.assertRaises(OSError):
                    B.close_unit()
                cmd.assert_not_called()

    def test_close_facts_failure_has_no_poweroff_fallback(self):
        with tempfile.TemporaryDirectory(dir=TASK / "evidence") as tmp:
            (Path(tmp) / "STATE.JSON").write_text("{}")
            with patch.object(B, "RAM", Path(tmp)), patch.object(B, "facts", side_effect=B.Refusal("fixture")), \
                    patch.object(B, "command") as cmd:
                with self.assertRaises(B.Refusal):
                    B.close_unit()
                cmd.assert_not_called()

    def test_close_snapshot_failure_has_no_poweroff_fallback(self):
        with tempfile.TemporaryDirectory(dir=TASK / "evidence") as tmp:
            (Path(tmp) / "STATE.JSON").write_text("{}")
            with patch.object(B, "RAM", Path(tmp)), patch.object(B, "facts", return_value={}), \
                    patch.object(B, "match_session"), patch.object(B, "snapshot", side_effect=OSError("fixture")), \
                    patch.object(B, "command") as cmd:
                with self.assertRaises(OSError):
                    B.close_unit()
                cmd.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
