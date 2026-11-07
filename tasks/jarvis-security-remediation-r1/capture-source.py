"""Capture only public source already selected for the audit, plus new code/tests."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import sys

OUTPUT = Path(__file__).resolve().parent
ROOT = OUTPUT.parents[1]
name = sys.argv[1]
if name not in {"candidate-1", "candidate-2", "candidate-3", "candidate-4", "candidate-5", "final", "final-2"}:
    raise SystemExit("invalid capture name")
snapshot = OUTPUT / name
snapshot.mkdir(exist_ok=False)
paths = {row["path"] for row in json.loads((OUTPUT / "baseline-source.json").read_text())}
extensions = {".py", ".js", ".cjs", ".html", ".css", ".md", ".json", ".jsonl", ".txt", ".yaml", ".yml", ".toml"}
for root in ("app", "tests", "docs", "frontend", "scripts", "evals"):
    for base, dirs, files in os.walk(ROOT / root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", "node_modules", ".git", ".pytest_cache", "dist", "build"}]
        for item in files:
            source = Path(base) / item
            if not source.is_symlink() and source.suffix in extensions and source.stat().st_size <= 2_000_000:
                paths.add(str(source.relative_to(ROOT)))
if (ROOT / ".dockerignore").is_file():
    paths.add(".dockerignore")
rows = []
for path in sorted(paths):
    source = ROOT / path
    if source.is_symlink():
        raise SystemExit("refusing symlink source: " + path)
    before = source.stat()
    raw = source.read_bytes()
    after = source.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise SystemExit("source changed during capture: " + path)
    destination = snapshot / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    destination.chmod(0o444)
    rows.append(dict(path=path, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
unstable = [row["path"] for row in rows if hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() != row["sha256"]]
for base, dirs, files in os.walk(snapshot, topdown=False):
    Path(base).chmod(0o555)
document = dict(capture_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                consistency="Stable per-file reads and rehash, not an atomic cross-file snapshot",
                unstable_paths=unstable, files=rows)
(OUTPUT / (name + "-manifest.json")).write_text(json.dumps(document, indent=2) + "\n")
if unstable:
    raise SystemExit("capture unstable: " + repr(unstable))
print(json.dumps(dict(snapshot=name, files=len(rows), unstable_paths=unstable)))
