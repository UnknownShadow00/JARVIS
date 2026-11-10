"""Read-only verification of recovered R2 evidence and its committed inputs.

Uses only the standard library. Does not import application or test modules,
regenerate inventories, change snapshots, or execute excluded tests.
"""

import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
PACKET = Path(__file__).resolve().parent
BASE = "5c878448a90077ab277430f2b8ab3eec6b60a103"
AUDIT = ROOT.parent / "JARVIS/tasks/jarvis-v2-independent-baseline-audit-r1"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def identities(nodes):
    ordinals = Counter()
    result = set()
    for node in nodes:
        base = node.split("[", 1)[0]
        result.add(hashlib.sha256(f"{base}#{ordinals[base]}".encode()).hexdigest())
        ordinals[base] += 1
    require(len(result) == len(nodes), "identity collision or duplicate")
    return result


def verify_manifest(directory):
    manifest = directory / "SHA256SUMS"
    entries = []
    for line in manifest.read_text().splitlines():
        expected, name = line.split("  ", 1)
        relative = Path(name)
        require(not relative.is_absolute() and ".." not in relative.parts, "unsafe manifest path")
        require(digest(directory / relative) == expected, f"evidence hash: {name}")
        entries.append(name)
    require(len(entries) == len(set(entries)), "duplicate manifest entry")
    return dict(entries=len(entries), sha256=digest(manifest))


def definitions(source):
    return {
        node.name: ast.unparse(node)
        for node in ast.parse(source).body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def main():
    final = PACKET / "verified-acceptance"
    result = read(final / "RESULT.json")
    manifest = verify_manifest(final)
    snapshot = Path(result["source_snapshot"])
    expected = result["source_sha256"]
    require(result["status"] == "PASS", "previous acceptance did not pass")
    require(expected == result["source_after_sha256"] == result["snapshot_after_sha256"], "before/after mismatch")
    tree = hashlib.sha256(json.dumps(expected, sort_keys=True).encode()).hexdigest()
    require(tree == result["content_tree_sha256"], "input tree digest")
    for name, value in expected.items():
        require(digest(ROOT / name) == digest(snapshot / name) == value, f"input changed: {name}")
        require(not (snapshot / name).is_symlink(), "snapshot symlink")
    launcher = PACKET / "accept_snapshot.py"
    parsed = ast.parse(launcher.read_text())
    constants = {n.targets[0].id: ast.literal_eval(n.value) for n in parsed.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("PUBLIC_FILES", "SCRIPTS")}
    functions = ast.Module(body=[n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name in ("files", "hashes")], type_ignores=[])
    namespace = dict(Path=Path, hashlib=hashlib, **constants)
    exec(compile(functions, str(launcher), "exec"), namespace)
    require(namespace["hashes"](ROOT) == namespace["hashes"](snapshot) == expected, "acceptance input set changed")
    for path in [snapshot, *snapshot.rglob("*")]:
        require(not stat.S_IMODE(path.stat().st_mode) & 0o222, "snapshot is writable")
    tracked = set(subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0"))
    require(set(expected) <= tracked, "untracked acceptance input")

    inventory = read(ROOT / "scripts/required_tests.json")
    policy = read(ROOT / "scripts/test_enrollment.json")["modules"]
    require(digest(ROOT / "scripts/required_tests.json") == result["required_inventory_sha256"], "inventory hash")
    require(digest(ROOT / "scripts/test_enrollment.json") == result["module_policy_sha256"], "policy hash")
    actual_modules = {p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").rglob("*.py") if "__pycache__" not in p.parts}
    require(actual_modules == set(policy), "module inventory changed")
    for name, entry in policy.items():
        require(digest(ROOT / name) == entry["sha256"], f"module source: {name}")
    positive = ("coverage", "reconciliation", "r3", "r2", "new", "existing")
    positive_modules = {n.split("::")[0] for mode in positive for n in inventory["suites"][mode]["nodeids"]}
    require(positive_modules == {p for p, e in policy.items() if e["disposition"] == "required"}, "enrollment disagreement")
    legacy = json.loads(subprocess.check_output(["git", "show", BASE + ":scripts/required_tests.json"], cwd=ROOT))
    for mode, suite in legacy["suites"].items():
        require(suite["nodeids"] == inventory["suites"][mode]["nodeids"], "legacy node inventory changed")

    all_ids = set()
    suites = []
    repeats = 0
    runs = {r["name"]: r for r in result["runs"]}
    for name in ("coverage", "reconciliation", "r3", "r2", "original", "existing", "coverage-seed42", "reconciliation-seed42", "r3-seed42", "r2-seed42", "original-seed42"):
        body = read(final / (name + ".json"))
        mode = name.removesuffix("-seed42")
        mode = "new" if mode == "original" else mode
        required = identities(inventory["suites"][mode]["nodeids"])
        cases = body["scenarios"]
        observed = {c["id"] for c in cases}
        require(observed == required and len(cases) == len(required), f"case inventory: {name}")
        require(body["status"] == "PASS" and body["counts"] == dict(PASS=len(required), FAIL=0, ERROR=0, SKIP=0, INCOMPLETE=0), f"case counts: {name}")
        require(body["gate_exit_code"] == body["child_exit_code"] == runs[name]["exit"] == 0, f"process exit: {name}")
        require(body["required_missing"] == body["unexpected_collected"] == 0, f"missing cases: {name}")
        require(body["inventory_sha256"] == result["required_inventory_sha256"], "report inventory binding")
        require(body["session"]["finished"] and body["session"]["pytest_exit_code"] == 0, "session completion")
        for case in cases:
            require(case["complete"] and case["status"] == "PASS", "incomplete case")
            require([p["phase"] for p in case["phases"]] == ["setup", "call", "teardown"], "missing phase")
            require(all(p["outcome"] == "passed" for p in case["phases"]), "nonpassing phase")
        for path, value in body["source_sha256"].items():
            require(expected[path] == value, "report source binding")
        if name.endswith("-seed42"):
            require(body["seed"] == 42, "repeat seed")
            repeats += len(required)
        else:
            require(not all_ids & required, "cross-suite duplicate")
            all_ids.update(required)
        suites.append(dict(name=name, passes=len(required), failures=0, errors=0, skips=0, incomplete=0, exit=0))
    require(len(all_ids) == 886 and repeats == 379, "distinct count")
    gates = read(final / "gate22/SUMMARY.json")
    negatives = read(final / "negative14/SUMMARY.json")
    adversaries = read(final / "adversaries11/SUMMARY.json")
    require(len(gates) == 22 and all(c["contract_pass"] for c in gates), "gate contracts")
    require(negatives["passed"] == 14 and negatives["failed"] == 0 and len(negatives["checks"]) == 14, "negative contracts")
    require(len(adversaries) == 11 and all(c["passed"] for c in adversaries), "adversaries")
    require(all(r["exit"] == 0 for r in runs.values()), "acceptance job exit")

    audit = read(AUDIT / "EXCLUSION-REVIEW.json")
    decisions = read(PACKET / "MODULE-DECISIONS.json")
    audit_by_path = {a["module"]: a for a in audit}
    require(len(audit) == len(decisions) == 86 and set(audit_by_path) == {d["path"] for d in decisions}, "audit module coverage")
    for entry in decisions:
        require(entry["prior_classification"] == audit_by_path[entry["path"]]["classification"], "prior classification")
        require(entry["decision"] == policy[entry["path"]]["disposition"], "module disposition")
        require(digest(ROOT / entry["path"]) == entry["source_sha256"], "decision content hash")
    relevant = [d for d in decisions if d["prior_classification"] == "Safe and relevant: enroll/port"]
    require(len(relevant) == 30 and all(d["decision"] == "required" for d in relevant), "relevant enrollment")
    unresolved = [d for d in decisions if d["prior_classification"].startswith("Unclear:")]
    require(len(unresolved) == 8 and Counter(d["decision"] for d in unresolved) == dict(required=6, excluded_live_or_hardware=1, excluded_offline_scope=1), "unresolved decisions")
    for entry in read(PACKET / "TEST-PORTS.json"):
        for label, source in [("old", subprocess.check_output(["git", "show", BASE + ":" + entry["file"]], cwd=ROOT, text=True)), ("new", (ROOT / entry["file"]).read_text())]:
            require(definitions(source).get(entry["function"]) == entry[label], "port catalog function mismatch")
    require(not subprocess.check_output(["git", "diff", BASE, "HEAD", "--", "app"], cwd=ROOT), "application source changed")

    before_failure = read(PACKET / "dictation-before.json")
    require(before_failure["counts"]["FAIL"] == 1 and before_failure["counts"]["PASS"] == 0, "dictation reproduction")
    preservation = read(PACKET / "RESUME-PRESERVATION.json")
    protection = preservation["prior_files"]
    # Draft prose is extended later, while all prior evidence must remain exact.
    extensions = {"REPORT.md", "ENROLLMENT-RECONCILIATION.md", "DICTATION-FAILURE-ANALYSIS.md", "TEST-RESULTS.md", "SECURITY-REVIEW.md", "INTEGRITY-EVIDENCE.md", "INTEGRATION-HANDOFF.md"}
    for name, info in protection.items():
        if name in ("CHANGED-FILES.json", "SHA256SUMS") and (PACKET / "resume-preserved" / name).is_file():
            require(digest(PACKET / "resume-preserved" / name) == info["sha256"], "original seal metadata not preserved")
        elif name in extensions:
            relative = (PACKET / name).relative_to(ROOT).as_posix()
            original = subprocess.check_output(["git", "show", preservation["starting_commit"] + ":" + relative], cwd=ROOT)
            require(hashlib.sha256(original).hexdigest() == info["sha256"] and (PACKET / name).read_bytes().startswith(original), "draft report was not preserved by appending")
        else:
            require(digest(PACKET / name) == info["sha256"], f"prior evidence changed: {name}")
    resumed = None
    resume = PACKET / "resume-verification"
    if (resume / "RESULT.json").is_file():
        fresh = read(resume / "RESULT.json")
        require(fresh["status"] == "PASS" and fresh["source_before_sha256"] == fresh["source_after_sha256"] == fresh["snapshot_after_sha256"] == expected, "fresh source integrity")
        for name, count in [("coverage", 217), ("reconciliation", 66)]:
            fresh_suite = read(resume / (name + ".json"))
            previous = read(final / (name + ".json"))
            require(fresh_suite["counts"] == dict(PASS=count, FAIL=0, ERROR=0, SKIP=0, INCOMPLETE=0), "fresh counts")
            require(fresh_suite["status"] == "PASS" and fresh_suite["child_exit_code"] == fresh_suite["gate_exit_code"] == 0, "fresh exits")
            require(fresh_suite["required_missing"] == fresh_suite["unexpected_collected"] == 0, "fresh omissions")
            require({c["id"] for c in fresh_suite["scenarios"]} == {c["id"] for c in previous["scenarios"]}, "fresh identities")
            for case in fresh_suite["scenarios"]:
                require(case["complete"] and [p["phase"] for p in case["phases"]] == ["setup", "call", "teardown"] and all(p["outcome"] == "passed" for p in case["phases"]), "fresh phases")
        require(all(r["exit"] == 0 for r in fresh["runs"]), "fresh process exit")
        require(len(fresh["integrity_probes"]) == 5 and all(p["passed"] for p in fresh["integrity_probes"]), "fresh integrity probes")
        require(len(read(resume / "adversaries11/SUMMARY.json")) == 11 and all(c["passed"] for c in read(resume / "adversaries11/SUMMARY.json")), "fresh adversaries")
        resumed = dict(manifest=verify_manifest(resume), fresh_distinct_positive=283, fresh_adversaries=11, integrity_probes=5, exit=0)
    return dict(status="PASS", checked_utc=datetime.now(timezone.utc).isoformat(), source_commit=result["source_commit"], current_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), acceptance_manifest=manifest, input_files=len(expected), content_tree_sha256=tree, snapshot_readonly=True, source_integrity=True, distinct_positive=len(all_ids), repeats=repeats, suites=suites, relevant_enrolled=30, newly_resolved_enrolled=6, module_counts=dict(Counter(e["disposition"] for e in policy.values())), gate_contracts=22, negative_contracts=14, new_adversaries=11, original_audit_manifest=verify_manifest(AUDIT), original_audit_report_sha256=digest(AUDIT / "REPORT.md"), test_ports_validated=19, prior_evidence_preserved=True, application_unchanged=True, resume_verification=resumed)


if __name__ == "__main__":
    try:
        print(json.dumps(main(), indent=2))
    except (ValueError, OSError, KeyError) as error:
        print(json.dumps(dict(status="FAIL", reason=str(error))))
        sys.exit(1)
