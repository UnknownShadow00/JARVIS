"""Run only the local offline validator against retained synthetic fixtures."""
import json
from pathlib import Path
import subprocess
import sys

TASK = Path(__file__).resolve().parents[1]


def replay():
    index = json.loads((TASK / "fixtures/INDEX.json").read_bytes())
    results = []
    for case in index:
        name = case["file"]
        if Path(name).name != name:
            raise ValueError("FIXTURE_NAME")
        command = [sys.executable, "-I", "-B", "-S", str(TASK / "tools/state_validator.py"),
                   "--bundle", str(TASK / "fixtures" / name),
                   "--as-of", "2026-11-06T18:00:30Z"]
        run = subprocess.run(command, capture_output=True, text=True, timeout=10)
        receipt = json.loads(run.stdout)
        expected_status = "PASS_OFFLINE_CONSISTENCY_ONLY" if case["accept"] else "FAIL_OFFLINE_VALIDATION"
        passed = (run.returncode == (0 if case["accept"] else 1)
                  and receipt["status"] == expected_status and not run.stderr
                  and receipt["live_evidence"] is False
                  and receipt["authorization_granted"] is False
                  and receipt["gate6k_qualified"] is False)
        results.append({"fixture": name, "expected_accept": case["accept"], "pass": passed,
                        "exitcode": run.returncode, "receipt": receipt})
    return {"status": "PASS_SYNTHETIC_CLI_CASES" if all(r["pass"] for r in results) else "FAIL",
            "cases": results, "live_qualification": False}


if __name__ == "__main__":
    result = replay()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "PASS_SYNTHETIC_CLI_CASES" else 1)
