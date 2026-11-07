"""Synthetic JSON and local temporary files only. No host/guest commands."""
import copy
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

TASK = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("state_validator", TASK / "tools/state_validator.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
BASE = V.timestamp("2026-11-06T18:00:00Z")


def stamp(seconds):
    return (BASE + dt.timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


def config(attached=True):
    return {"name": "jarvis-g6k-clean-164", "smbios1": "uuid=" + V.UUID,
            "scsi0": V.DISK + ",serial=" + V.SERIAL + ",size=64G",
            "ide2": (V.ISO if attached else "none") + ",media=cdrom",
            "boot": "order=scsi0", "onboot": 0, "agent": "0", "serial0": "socket",
            "vga": "std", "hotplug": "0", "protection": 1, "digest": "a" * 40,
            "cores": 4, "sockets": 1, "memory": 6000, "balloon": 0}


def replace(snapshot, name, value):
    artifact = snapshot["readbacks"][name]
    artifact["raw"] = json.dumps(value, sort_keys=True)
    artifact["sha256"] = V.sha(artifact["raw"].encode())
    if name == "config" and snapshot["iso_verification"] is not None:
        snapshot["iso_verification"]["config_readback_sha256"] = artifact["sha256"]


def snapshot(state="preflight_attached", second=0, previous=None):
    status, attached = V.STATES[state]
    s = {"id": "synthetic_" + str(second), "state": state, "node": "pve", "vmid": 164,
         "capture_started_at": stamp(second), "capture_finished_at": stamp(second + 3),
         "previous_sha256": V.sha(V.canonical(previous)) if previous else None,
         "readbacks": {}, "config_digest": "a" * 40, "iso_verification": None}
    for name in V.ENDPOINTS:
        s["readbacks"][name] = {"raw": "", "sha256": "", "captured_at": stamp(second + 1),
                                 "endpoint": V.ENDPOINTS[name]}
    if attached:
        s["iso_verification"] = {"volume": V.ISO, "sha256": V.ISO_SHA, "bytes": 196608,
                                 "captured_at": stamp(second), "config_readback_sha256": ""}
    c = config(attached)
    if previous:
        old = json.loads(previous["readbacks"]["config"]["raw"])
        c["digest"] = old["digest"] if old["ide2"] == c["ide2"] else V.sha(V.canonical(
            {k: v for k, v in c.items() if k != "digest"}))[:40]
        s["config_digest"] = c["digest"]
    replace(s, "config", c)
    replace(s, "status", {"vmid": 164, "status": status})
    replace(s, "pending", [])
    return s


def bundle(*snapshots):
    return {"format": V.FORMAT, "kind": "synthetic", "session_reference": "OFFLINE-TEST-ONLY",
            "snapshots": list(snapshots or [snapshot()])}


class ValidatorTests(unittest.TestCase):
    def ok(self, b=None, second=10, **kwargs):
        return V.evaluate(b or bundle(), now=BASE + dt.timedelta(seconds=second), **kwargs)

    def bad(self, b, code=None, second=10, **kwargs):
        with self.assertRaises(V.Refusal) as caught:
            self.ok(b, second, **kwargs)
        if code:
            self.assertEqual(str(caught.exception), code)

    def mutate_config(self, **changes):
        b = bundle()
        c = config()
        c.update(changes)
        replace(b["snapshots"][0], "config", c)
        return b

    def test_attached_disk_only_restored_is_offline_only(self):
        result = self.ok()
        self.assertEqual(result["status"], "PASS_OFFLINE_CONSISTENCY_ONLY")
        for key in ("live_evidence", "origin_authenticated", "atomic_readback_proven",
                    "guest_media_absence_verified", "watchdog_or_cleanup_verified",
                    "authorization_granted", "gate6k_qualified", "mutations_performed"):
            self.assertIs(result[key], False)

    def test_auto_added_ide2(self):
        self.bad(self.mutate_config(boot="order=scsi0;ide2"), "DISK_ONLY_BOOT_REQUIRED")

    def test_other_boot_forms(self):
        for boot in ("order=ide2;scsi0", "order=scsi0;net0", "order=scsi0;scsi1", "c", "", None):
            with self.subTest(boot=boot):
                self.bad(self.mutate_config(boot=boot))

    def test_wrong_iso_and_volume(self):
        for iso in ("local:iso/ubuntu.iso", V.ISO.replace("local:", "downloads:"),
                    V.ISO.replace("fd91b8b07243565e", "0000000000000000")):
            with self.subTest(iso=iso):
                self.bad(self.mutate_config(ide2=iso + ",media=cdrom"), "EXACT_MEDIA_REQUIRED")

    def test_identity_failures(self):
        for field, value in (("name", "other"), ("smbios1", "uuid=wrong"),
                             ("scsi0", V.DISK + ",serial=wrong,size=64G"),
                             ("scsi0", "other:164/disk,serial=" + V.SERIAL + ",size=64G"),
                             ("scsi0", V.DISK + ",serial=" + V.SERIAL + ",size=32G")):
            with self.subTest(field=field, value=value):
                self.bad(self.mutate_config(**{field: value}))

    def test_duplicate_or_unreviewed_disk_options(self):
        for suffix in (",serial=other", ",size=32G", ",file=other", ",bad", ",serial==x"):
            with self.subTest(suffix=suffix):
                self.bad(self.mutate_config(scsi0=config()["scsi0"] + suffix))

    def test_unexpected_channels_and_boot_devices(self):
        for field in ("net0", "scsi1", "efidisk0", "tpmstate0", "sata0", "virtio0", "ide0",
                      "serial1", "hostpci0", "usb0", "virtiofs0", "unused0", "args",
                      "hookscript", "sshkeys", "cipassword", "unknown_future_channel"):
            with self.subTest(field=field):
                self.bad(self.mutate_config(**{field: "unexpected"}), "UNREVIEWED_CONFIG_FIELD")

    def test_agent_not_disabled(self):
        for value in (1, "1", "enabled=1", "enabled=0,type=virtio", False, None, {}):
            with self.subTest(value=value):
                self.bad(self.mutate_config(agent=value), "AGENT_DISABLED_REQUIRED")

    def test_missing_config_fields(self):
        for key in V.REQUIRED_CONFIG:
            b = bundle()
            c = config()
            del c[key]
            replace(b["snapshots"][0], "config", c)
            with self.subTest(key=key):
                self.bad(b, "MISSING_CONFIG_FIELDS")

    def test_resource_and_manual_boot_boundaries(self):
        for key, value in (("cores", 1), ("memory", 5999), ("balloon", 1), ("sockets", 0),
                           ("cores", True), ("hotplug", "disk"), ("protection", 0),
                           ("onboot", 1), ("vga", "serial0"), ("serial0", "/dev/ttyS0"),
                           ("template", 1), ("lock", "backup"), ("smbios", "other")):
            with self.subTest(key=key, value=value):
                self.bad(self.mutate_config(**{key: value}))

    def test_pending_only_cd_ejection(self):
        first = snapshot()
        running = snapshot("debug_attached", 10, first)
        replace(running, "pending", [{"key": "ide2", "value": V.ISO + ",media=cdrom",
                                      "pending": "none,media=cdrom"}])
        self.bad(bundle(first, running), second=20)

    def test_no_pending_or_delete_is_ever_waived(self):
        for row in ({"key": "ide2", "value": "none", "pending": None},
                    {"key": "ide2", "value": "none", "delete": 1},
                    {"key": "ide2", "value": "none", "deleted": 0}, {}, [], None):
            b = bundle()
            replace(b["snapshots"][0], "pending", [row])
            with self.subTest(row=row):
                self.bad(b)

    def test_unchanged_pending_rows_and_mismatched_rows(self):
        b = bundle()
        s = b["snapshots"][0]
        replace(s, "pending", [{"key": "boot", "value": "order=scsi0"}])
        self.ok(b)
        replace(s, "pending", [{"key": "boot", "value": "order=ide2"}])
        self.bad(b, "PENDING_CURRENT_VALUE_MISMATCH")
        replace(s, "pending", [{"key": "boot", "value": "order=scsi0"}] * 2)
        self.bad(b, "PENDING_KEY")

    def test_running_when_stopped_expected_and_missing_status(self):
        for status in ({"vmid": 164, "status": "running"}, {"vmid": 200, "status": "stopped"},
                       {"vmid": "164", "status": "stopped"}, {}, {"vmid": 164}, None):
            b = bundle()
            replace(b["snapshots"][0], "status", status)
            with self.subTest(status=status):
                self.bad(b)

    def test_config_digest_mismatch(self):
        self.bad(self.mutate_config(digest="b" * 40), "CONFIG_DIGEST_MISMATCH")
        self.bad(bundle(), "EXPECTED_CONFIG_DIGEST_MISMATCH", expected_digest="b" * 40)
        self.ok(expected_digest="a" * 40)

    def test_truncated_malformed_duplicate_and_nonfinite_json(self):
        for raw in ('{', '{"a":1,"a":2}', 'NaN', '{"a": Infinity}', '{"a":1e999}', b'\xff'):
            with self.subTest(raw=raw), self.assertRaises(V.Refusal):
                V.parse(raw)
        for raw in ('{', '{"boot":"order=scsi0","boot":"order=ide2"}', 'NaN'):
            b = bundle()
            a = b["snapshots"][0]["readbacks"]["config"]
            a.update(raw=raw, sha256=V.sha(raw.encode()))
            with self.subTest(raw=raw):
                self.bad(b)

    def test_readback_hash_tamper(self):
        for name in V.ENDPOINTS:
            b = bundle()
            b["snapshots"][0]["readbacks"][name]["raw"] += " "
            with self.subTest(name=name):
                self.bad(b, "READBACK_HASH_MISMATCH")

    def test_iso_hash_size_volume_binding_and_age(self):
        for key, value in (("sha256", "0" * 64), ("bytes", 123), ("bytes", True),
                           ("volume", "other.iso"), ("config_readback_sha256", "0" * 64),
                           ("captured_at", "2026-11-06T17:00:00Z"),
                           ("captured_at", stamp(10))):
            b = bundle()
            b["snapshots"][0]["iso_verification"][key] = value
            with self.subTest(key=key):
                self.bad(b)

    def test_missing_evidence_fields(self):
        for key in snapshot():
            b = bundle()
            del b["snapshots"][0][key]
            with self.subTest(key=key):
                self.bad(b)
        for key in ("raw", "sha256", "captured_at", "endpoint"):
            b = bundle()
            del b["snapshots"][0]["readbacks"]["config"][key]
            with self.subTest(key=key):
                self.bad(b)

    def test_stale_future_skew_and_naive_times(self):
        self.bad(bundle(), "LATEST_EVIDENCE_STALE", second=121)
        self.bad(bundle(), second=2)
        for key, value in (("capture_finished_at", stamp(31)),
                           ("capture_started_at", "2026-11-06T18:00:00"),
                           ("capture_started_at", "2026-02-30T18:00:00Z")):
            b = bundle()
            b["snapshots"][0][key] = value
            with self.subTest(key=key):
                self.bad(b)
        with self.assertRaises(V.Refusal):
            V.evaluate(bundle(), now=dt.datetime(2026, 11, 6))

    def test_origin_and_live_label_refusals(self):
        for key, value in (("node", "other"), ("vmid", 200)):
            b = bundle()
            b["snapshots"][0][key] = value
            self.bad(b, "READBACK_ORIGIN_ASSERTION")
        for kind in ("live", "attested", "approved", None):
            b = bundle()
            b["kind"] = kind
            self.bad(b, "OFFLINE_SOURCE_REQUIRED")
        b = bundle()
        b["kind"] = "saved_readback"
        self.assertFalse(self.ok(b)["live_evidence"])

    def test_wrong_endpoint_and_capture_time(self):
        b = bundle()
        a = b["snapshots"][0]["readbacks"]["status"]
        a["endpoint"] = V.ENDPOINTS["config"]
        self.bad(b, "WRONG_ENDPOINT")
        a["endpoint"] = V.ENDPOINTS["status"]
        a["captured_at"] = stamp(4)
        self.bad(b, "READBACK_OUTSIDE_CAPTURE")

    def test_ambiguous_config_view_is_refused(self):
        b = bundle()
        b["snapshots"][0]["readbacks"]["config"]["endpoint"] = "/nodes/pve/qemu/164/config"
        self.bad(b, "WRONG_ENDPOINT")

    def test_full_synthetic_transition_sequence(self):
        snapshots = []
        for i, state in enumerate(V.STATES):
            snapshots.append(snapshot(state, i * 10, snapshots[-1] if snapshots else None))
        self.assertEqual(len(self.ok(bundle(*snapshots), second=70)["snapshots"]), 7)

    def test_valid_then_later_invalid(self):
        first = snapshot()
        self.ok(bundle(first))
        second = snapshot("debug_attached", 10, first)
        c = config()
        c["net0"] = "virtio"
        replace(second, "config", c)
        self.bad(bundle(first, second), second=20)

    def test_protected_change_with_valid_individual_configs(self):
        first = snapshot()
        second = snapshot("debug_attached", 10, first)
        c = config()
        c["memory"] = 7000
        replace(second, "config", c)
        self.bad(bundle(first, second), "PROTECTED_CONFIG_CHANGED", second=20)

    def test_digest_change_without_config_change(self):
        first = snapshot()
        second = snapshot("debug_attached", 10, first)
        c = config()
        c["digest"] = "b" * 40
        second["config_digest"] = c["digest"]
        replace(second, "config", c)
        self.bad(bundle(first, second), "DIGEST_CONTINUITY", second=20)

    def test_digest_unchanged_after_media_change(self):
        first = snapshot()
        running = snapshot("debug_attached", 10, first)
        empty = snapshot("debug_empty", 20, running)
        c = config(False)
        replace(empty, "config", c)
        empty["config_digest"] = c["digest"]
        self.bad(bundle(first, running, empty), "DIGEST_CONTINUITY", second=30)

    def test_skipped_reversed_and_invented_transition(self):
        first = snapshot()
        for state in ("clean_running", "final_empty", "debug_empty", "initial_empty"):
            later = snapshot(state, 10, first)
            with self.subTest(state=state):
                self.bad(bundle(first, later), "UNEXPECTED_STATE_TRANSITION", second=20)
        for state in ("debug_attached", "debug_empty", "final_empty"):
            with self.subTest(entry=state):
                self.bad(bundle(snapshot(state)), "INVALID_CHAIN_ENTRY")

    def test_chain_hash_and_replay_order(self):
        first = snapshot()
        second = snapshot("debug_attached", 10, first)
        second["previous_sha256"] = "0" * 64
        self.bad(bundle(first, second), "CHAIN_HASH_MISMATCH", second=20)
        second = snapshot("debug_attached", 2, first)
        self.bad(bundle(first, second), "NONMONOTONIC_CAPTURE", second=20)

    def test_snapshot_and_size_bounds(self):
        b = bundle()
        b["snapshots"] = []
        self.bad(b, "SNAPSHOT_COUNT")
        with self.assertRaises(V.Refusal):
            V.parse(" " * (V.MAX_BYTES + 1))

    def test_input_special_files_and_no_write(self):
        with tempfile.TemporaryDirectory(dir=TASK / "evidence") as tmp:
            root = Path(tmp)
            regular = root / "input.json"
            raw = V.canonical(bundle())
            regular.write_bytes(raw)
            self.assertEqual(V.read_local(regular), raw)
            link = root / "link"
            link.symlink_to(regular)
            fifo = root / "fifo"
            os.mkfifo(fifo)
            for path in (link, fifo, root):
                with self.subTest(path=path.name), self.assertRaises((OSError, V.Refusal)):
                    V.read_local(path)
            hard = root / "hard"
            os.link(regular, hard)
            with self.assertRaises(V.Refusal):
                V.read_local(regular)
            self.assertEqual(regular.read_bytes(), raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
