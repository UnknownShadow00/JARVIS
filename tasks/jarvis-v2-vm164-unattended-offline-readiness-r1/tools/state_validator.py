"""Validate supplied VM164 evidence only; no transport, subprocess or mutation.

Even an accepted saved readback is neither live evidence nor authorization.
All timestamps, endpoints, hashes and origin labels are untrusted assertions.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import stat
import sys

UUID = "faeb1db8-0df9-482d-b3e4-f6ccc1602193"
SERIAL = "g6k164-12821f6b54a2"
DISK = "downloads:164/vm-164-disk-0.raw"
ISO = "local:iso/vm164-trusted-bootstrap-fd91b8b07243565e.iso"
ISO_SHA = "fd91b8b07243565e41aad3180a6fa569907d0e85edea6f95655b9983e56d8154"
FORMAT = "vm164-offline-evidence-v1"
MAX_BYTES = 2 * 1024 * 1024
MAX_AGE = 120  # Conservative engineering policy, not an approved live window.
STATES = {
    "initial_empty": ("stopped", False),
    "preflight_attached": ("stopped", True),
    "debug_attached": ("running", True),
    "debug_empty": ("running", False),
    "closed_empty": ("stopped", False),
    "clean_running": ("running", False),
    "final_empty": ("stopped", False),
}
EDGES = {
    ("initial_empty", "preflight_attached"),
    ("preflight_attached", "debug_attached"),
    ("debug_attached", "debug_empty"),
    ("debug_empty", "closed_empty"),
    ("closed_empty", "clean_running"),
    ("clean_running", "final_empty"),
}
REQUIRED_CONFIG = {
    "name", "smbios1", "scsi0", "ide2", "boot", "onboot", "agent",
    "serial0", "vga", "hotplug", "protection", "digest", "cores", "sockets",
    "memory", "balloon",
}
# Unrecognized fields fail closed, including future hardware/channel options.
# These optional fields remain byte-semantically bound across every transition.
ALLOWED_CONFIG = REQUIRED_CONFIG | {
    "bios", "machine", "ostype", "scsihw", "cpu", "numa", "meta",
    "description", "tags", "smbios", "lock", "template",
}
ENDPOINTS = {
    "config": "/nodes/pve/qemu/164/config?current=1",
    "status": "/nodes/pve/qemu/164/status/current",
    "pending": "/nodes/pve/qemu/164/pending",
}


class Refusal(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def pairs(rows):
    out = {}
    for key, value in rows:
        need(key not in out, "DUPLICATE_JSON_KEY")
        out[key] = value
    return out


def reject_constant(_value):
    raise Refusal("NONFINITE_JSON")


def finite_float(value):
    number = float(value)
    need(math.isfinite(number), "NONFINITE_JSON")
    return number


def parse(raw):
    need(isinstance(raw, (str, bytes)), "JSON_INPUT_TYPE")
    need(len(raw) <= MAX_BYTES, "JSON_SIZE_BOUND")
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=reject_constant,
                          parse_float=finite_float)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise Refusal("MALFORMED_JSON") from exc


def fields(value, required, optional=frozenset()):
    need(type(value) is dict and required <= value.keys()
         and value.keys() <= required | optional, "MISSING_OR_UNKNOWN_FIELDS")


def timestamp(value):
    need(type(value) is str and re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value) is not None,
        "UTC_TIMESTAMP_REQUIRED")
    try:
        return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except ValueError as exc:
        raise Refusal("INVALID_TIMESTAMP") from exc


def integer(value, minimum, maximum):
    if type(value) is str and re.fullmatch(r"0|[1-9][0-9]{0,8}", value):
        value = int(value)
    need(type(value) is int and minimum <= value <= maximum, "INTEGER_RANGE")
    return value


def config_check(c, status, pending, state, digest):
    need(type(c) is dict and REQUIRED_CONFIG <= c.keys(), "MISSING_CONFIG_FIELDS")
    need(c.keys() <= ALLOWED_CONFIG, "UNREVIEWED_CONFIG_FIELD")
    need(c["name"] == "jarvis-g6k-clean-164" and c["smbios1"] == "uuid=" + UUID,
         "VM_IDENTITY")
    need(c["boot"] == "order=scsi0", "DISK_ONLY_BOOT_REQUIRED")
    need(integer(c["onboot"], 0, 1) == 0, "ONBOOT_DISABLED_REQUIRED")
    need(type(c["agent"]) in (int, str) and c["agent"] in (0, "0", "enabled=0"),
         "AGENT_DISABLED_REQUIRED")
    need(c["serial0"] == "socket" and c["vga"] == "std", "EXISTING_CONSOLE_ONLY")
    need(integer(c["hotplug"], 0, 0) == 0 and integer(c["protection"], 1, 1) == 1,
         "PROTECTED_NO_HOTPLUG")
    need(not c.get("lock") and not c.get("template") and "smbios" not in c,
         "LOCK_TEMPLATE_OR_ALTERNATE_SMBIOS")
    need(type(c["digest"]) is str and re.fullmatch(r"[a-f0-9]{40}", c["digest"])
         is not None and digest == c["digest"], "CONFIG_DIGEST_MISMATCH")
    need(type(c["scsi0"]) is str, "DISK_SCHEMA")
    parts = c["scsi0"].split(",")
    need(parts[0] == DISK, "DISK_VOLUME")
    options = {}
    for part in parts[1:]:
        need(part.count("=") == 1, "DISK_OPTION_SCHEMA")
        key, value = part.split("=")
        need(key not in options, "DUPLICATE_DISK_OPTION")
        options[key] = value
    need(options.get("serial") == SERIAL and options.get("size") == "64G", "DISK_IDENTITY")
    need(options.keys() <= {"serial", "size", "iothread", "cache", "discard",
                            "aio", "backup", "ssd", "detect_zeroes"}, "UNREVIEWED_DISK_OPTION")
    integer(c["cores"], 1, 256)
    integer(c["sockets"], 1, 16)
    need(integer(c["cores"], 1, 256) * integer(c["sockets"], 1, 16) >= 4,
         "CPU_BASELINE")
    integer(c["memory"], 6000, 1048576)
    integer(c["balloon"], 0, 0)
    expected_status, attached = STATES[state]
    need(c["ide2"] == (ISO if attached else "none") + ",media=cdrom", "EXACT_MEDIA_REQUIRED")
    need(type(status) is dict and {"vmid", "status"} <= status.keys(), "STATUS_SCHEMA")
    need(type(status["vmid"]) is int and status["vmid"] == 164
         and status["status"] == expected_status, "VMID_OR_STATE")
    # Proxmox returns unchanged rows too. A pending key (even null/empty) refuses.
    need(type(pending) is list and len(pending) <= 256, "PENDING_SCHEMA")
    seen = set()
    for row in pending:
        need(type(row) is dict, "PENDING_SCHEMA")
        need(not any(key in row for key in ("pending", "delete", "deleted")), "PENDING_OPERATION")
        fields(row, {"key", "value"})
        key = row["key"]
        need(type(key) is str and key in c and key not in seen, "PENDING_KEY")
        need(row["value"] == c[key] and type(row["value"]) is type(c[key]),
             "PENDING_CURRENT_VALUE_MISMATCH")
        seen.add(key)
    return attached


def evaluate(bundle, *, now, expected_digest=None):
    """Pure validation. 'now' must be an explicit aware UTC reference clock."""
    need(isinstance(now, dt.datetime) and now.utcoffset() == dt.timedelta(0), "UTC_CLOCK_REQUIRED")
    fields(bundle, {"format", "kind", "session_reference", "snapshots"})
    need(bundle["format"] == FORMAT and bundle["kind"] in ("synthetic", "saved_readback"),
         "OFFLINE_SOURCE_REQUIRED")
    need(type(bundle["session_reference"]) is str and re.fullmatch(
        r"[A-Za-z0-9_.:-]{1,120}", bundle["session_reference"]) is not None,
        "SESSION_REFERENCE_REQUIRED")
    snapshots = bundle["snapshots"]
    need(type(snapshots) is list and 1 <= len(snapshots) <= 32, "SNAPSHOT_COUNT")
    previous = None
    ids = set()
    receipts = []
    for snapshot in snapshots:
        fields(snapshot, {"id", "state", "node", "vmid", "capture_started_at",
                          "capture_finished_at", "previous_sha256", "readbacks",
                          "config_digest", "iso_verification"})
        sid = snapshot["id"]
        need(type(sid) is str and re.fullmatch(r"[A-Za-z0-9_-]{1,80}", sid)
             is not None and sid not in ids, "SNAPSHOT_ID")
        ids.add(sid)
        state = snapshot["state"]
        need(type(state) is str and state in STATES, "UNKNOWN_STATE")
        need(snapshot["node"] == "pve" and type(snapshot["vmid"]) is int
             and snapshot["vmid"] == 164, "READBACK_ORIGIN_ASSERTION")
        start = timestamp(snapshot["capture_started_at"])
        end = timestamp(snapshot["capture_finished_at"])
        need(start <= end <= now and (end - start).total_seconds() <= 30,
             "CAPTURE_TIME_OR_SKEW")
        need((now - start).total_seconds() <= 3600, "SESSION_EVIDENCE_TOO_OLD")
        fields(snapshot["readbacks"], set(ENDPOINTS))
        decoded = {}
        for name, endpoint in ENDPOINTS.items():
            artifact = snapshot["readbacks"][name]
            fields(artifact, {"raw", "sha256", "captured_at", "endpoint"})
            need(type(artifact["raw"]) is str, "RAW_JSON_TEXT_REQUIRED")
            need(artifact["sha256"] == sha(artifact["raw"].encode("utf-8")),
                 "READBACK_HASH_MISMATCH")
            need(artifact["endpoint"] == endpoint, "WRONG_ENDPOINT")
            need(start <= timestamp(artifact["captured_at"]) <= end,
                 "READBACK_OUTSIDE_CAPTURE")
            decoded[name] = parse(artifact["raw"])
        c = decoded["config"]
        attached = config_check(c, decoded["status"], decoded["pending"], state,
                                snapshot["config_digest"])
        media = snapshot["iso_verification"]
        if attached:
            fields(media, {"volume", "sha256", "bytes", "captured_at", "config_readback_sha256"})
            need(media["volume"] == ISO and media["sha256"] == ISO_SHA
                 and type(media["bytes"]) is int and media["bytes"] == 196608,
                 "ISO_CONTENT_ASSERTION")
            need(media["config_readback_sha256"] == snapshot["readbacks"]["config"]["sha256"],
                 "ISO_CONFIG_BINDING")
            need(0 <= (end - timestamp(media["captured_at"])).total_seconds() <= MAX_AGE,
                 "ISO_OBSERVATION_AGE")
        else:
            need(media is None, "DETACHED_MEDIA_ASSERTION_MUST_BE_NULL")
        if previous is None:
            need(state in ("initial_empty", "preflight_attached")
                 and snapshot["previous_sha256"] is None, "INVALID_CHAIN_ENTRY")
        else:
            old, old_c, old_end = previous
            need(snapshot["previous_sha256"] == sha(canonical(old)), "CHAIN_HASH_MISMATCH")
            need(start > old_end, "NONMONOTONIC_CAPTURE")
            need(state == old["state"] or (old["state"], state) in EDGES,
                 "UNEXPECTED_STATE_TRANSITION")
            protected = lambda cfg: {k: v for k, v in cfg.items() if k not in ("ide2", "digest")}
            need(canonical(protected(c)) == canonical(protected(old_c)), "PROTECTED_CONFIG_CHANGED")
            changed = c["ide2"] != old_c["ide2"]
            need((c["digest"] != old_c["digest"]) == changed, "DIGEST_CONTINUITY")
        previous = (snapshot, c, end)
        receipts.append({"id": sid, "state": state, "snapshot_sha256": sha(canonical(snapshot)),
                         "config_digest": c["digest"], "readback_sha256": {
                             n: a["sha256"] for n, a in snapshot["readbacks"].items()}})
    latest = snapshots[-1]
    need((now - timestamp(latest["capture_started_at"])).total_seconds() <= MAX_AGE,
         "LATEST_EVIDENCE_STALE")
    need(expected_digest is None or expected_digest == previous[1]["digest"],
         "EXPECTED_CONFIG_DIGEST_MISMATCH")
    return {"status": "PASS_OFFLINE_CONSISTENCY_ONLY", "source_kind": bundle["kind"],
            "reference_time_utc": now.isoformat(), "bundle_sha256": sha(canonical(bundle)),
            "snapshots": receipts, "live_evidence": False, "origin_authenticated": False,
            "atomic_readback_proven": False, "guest_media_absence_verified": False,
            "watchdog_or_cleanup_verified": False, "authorization_granted": False,
            "gate6k_qualified": False, "mutations_performed": False}


def read_local(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
             and before.st_size <= MAX_BYTES, "REGULAR_BOUNDED_INPUT_REQUIRED")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            raw = stream.read(MAX_BYTES + 1)
        after = os.fstat(fd)
        identity = lambda st: (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)
        need(identity(before) == identity(after) and len(raw) == before.st_size,
             "INPUT_CHANGED_OR_TRUNCATED")
        return raw
    finally:
        os.close(fd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--as-of", help="Replay clock; never establishes present freshness")
    parser.add_argument("--expected-digest", help="Independent expected latest opaque PVE digest")
    args = parser.parse_args()
    try:
        raw = read_local(args.bundle)
        now = timestamp(args.as_of) if args.as_of else dt.datetime.now(dt.timezone.utc)
        result = evaluate(parse(raw), now=now, expected_digest=args.expected_digest)
        result["input_bytes_sha256"] = sha(raw)
        result["clock_source"] = "explicit_replay" if args.as_of else "local_clock"
    except (ValueError, OSError, TypeError, KeyError, OverflowError, RecursionError) as exc:
        # Never echo potentially sensitive raw configuration or exception text.
        result = {"status": "FAIL_OFFLINE_VALIDATION", "reason": str(exc) if isinstance(exc, Refusal)
                  else type(exc).__name__, "live_evidence": False, "authorization_granted": False,
                  "gate6k_qualified": False, "mutations_performed": False}
        print(json.dumps(result, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
