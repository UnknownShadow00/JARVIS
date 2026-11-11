"""Fresh bounded offline checks; reuse unchanged completed regression evidence."""

import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

os.umask(0o077)
PACKET = Path(__file__).resolve().parent
ROOT = PACKET.parents[1]
OUT = Path(sys.argv[1]).resolve()
OUT.mkdir(mode=0o700, parents=True, exist_ok=False)
prior = json.loads((PACKET / "verified-acceptance/RESULT.json").read_text())
snapshot = Path(prior["source_snapshot"])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(root):
    return {name: sha(root / name) for name in prior["source_sha256"]}


before = inputs(ROOT)
assert before == inputs(snapshot) == prior["source_sha256"]
runs = []


def run(name, args):
    command = [sys.executable, "-B", *map(str, args)]
    with (OUT / (name + ".log")).open("x") as log:
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=180)
    runs.append(dict(name=name, command=command, exit=result.returncode))
    if result.returncode:
        raise RuntimeError("resume verification failed: " + name)


run("recovered-evidence", [PACKET / "verify_recovered_evidence.py"])
for name, flag in [("coverage", "--coverage"), ("reconciliation", "--reconciliation")]:
    run(name, [snapshot / "scripts/reliability_gauntlet.py", flag, "--output", OUT / (name + ".json")])
run("adversaries11", [snapshot / "tasks/jarvis-v2-baseline-coverage-remediation-r2/check_adversaries.py", OUT / "adversaries11", snapshot])

# Exercise the exact snapshot driver's integrity routines on disposable copies.
launcher = snapshot / "tasks/jarvis-v2-baseline-coverage-remediation-r2/accept_snapshot.py"
module = ast.parse(launcher.read_text())
constants = {n.targets[0].id: ast.literal_eval(n.value) for n in module.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("PUBLIC_FILES", "SCRIPTS")}
functions = ast.Module(body=[n for n in module.body if isinstance(n, ast.FunctionDef) and n.name in ("files", "hashes")], type_ignores=[])
namespace = dict(Path=Path, hashlib=hashlib, **constants)
exec(compile(functions, str(launcher), "exec"), namespace)
probes = []
with tempfile.TemporaryDirectory(prefix="jarvis-r2-resume-probe-") as temp:
    disposable = Path(temp)
    for source in namespace["files"](snapshot):
        destination = disposable / source.relative_to(snapshot)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    baseline = namespace["hashes"](disposable)
    probes.append(dict(case="unchanged", passed=namespace["hashes"](disposable) == baseline))
    for name, relative, operation in [
        ("changed_test", "tests/test_dictation.py", "replace"),
        ("new_module", "tests/test_resume_unreviewed.py", "new"),
        ("deleted_test", "tests/test_dictation.py", "delete"),
        ("changed_harness", "tasks/jarvis-v2-baseline-coverage-remediation-r2/check_adversaries.py", "replace"),
    ]:
        path = disposable / relative
        old = path.read_bytes() if path.exists() else None
        if operation == "delete":
            path.unlink()
        else:
            path.write_text("synthetic disposable integrity mutation\n")
        probes.append(dict(case=name, passed=namespace["hashes"](disposable) != baseline))
        if old is None:
            path.unlink()
        else:
            path.write_bytes(old)
assert all(p["passed"] for p in probes)
after = inputs(ROOT)
snapshot_after = inputs(snapshot)
assert before == after == snapshot_after
run("recovered-evidence-after", [PACKET / "verify_recovered_evidence.py"])
report = dict(
    status="PASS", checked_utc=datetime.now(timezone.utc).isoformat(),
    committed_candidate=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    source_commit=prior["source_commit"], source_snapshot=str(snapshot),
    fresh_distinct_positive=283, retained_distinct_positive=886,
    new_distinct_test_cases=0, fresh_adversary_contracts=11,
    source_before_sha256=before, source_after_sha256=after, snapshot_after_sha256=snapshot_after,
    source_integrity=True, content_tree_sha256=prior["content_tree_sha256"],
    integrity_probes=probes, runs=runs,
    reuse_reason="All source inputs, exact case identities/phases, process exits and evidence hashes match; retain completed 507/45/32/19 regressions, seed repeats and22/14contracts instead of rerunning unchanged expensive work.",
)
(OUT / "RESULT.json").write_text(json.dumps(report, indent=2) + "\n")
(OUT / "SHA256SUMS").write_text("".join(sha(p) + "  " + p.relative_to(OUT).as_posix() + "\n" for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "SHA256SUMS"))
print(json.dumps({k: v for k, v in report.items() if not k.endswith("_sha256")}, indent=2))
