"""Read repository artifacts, verify pinned bytes, summarize offline dependencies.

Never invokes predecessor CLI entry points, external executables or VM helpers.
Outputs JSON to stdout only. No extraction, package installation or payload execution.
"""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat

TASK = Path(__file__).resolve().parents[1]
PROJECT = TASK.parents[1]
OLD = PROJECT / "tasks/jarvis-v2-vm164-trusted-bootstrap-r1"
LAB = PROJECT / "tasks/jarvis-v2-vm164-lab-readiness-r1"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def review():
    manifest_raw = (OLD / "MANIFEST.json").read_bytes()
    seal = json.loads((OLD / "SEAL.json").read_bytes())
    if sha(manifest_raw) != seal["manifest_sha256"]:
        raise ValueError("BOOTSTRAP_MANIFEST_SEAL")
    manifest = json.loads(manifest_raw)
    files, links = {}, {}
    for path in sorted(OLD.rglob("*")):
        name = str(path.relative_to(OLD))
        if name in {"MANIFEST.json", "SEAL.json"}:
            continue
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            links[name] = os.readlink(path)
        elif stat.S_ISREG(info.st_mode):
            raw = path.read_bytes()
            files[name] = {"sha256": sha(raw), "bytes": len(raw)}
            if path.suffix.lower() == ".py":
                ast.parse(raw, filename=name)
        elif not stat.S_ISDIR(info.st_mode):
            raise ValueError("PACKET_SPECIAL_FILE")
    if files != manifest["files"] or links != manifest["symlinks"]:
        raise ValueError("BOOTSTRAP_INVENTORY")
    entry = json.loads((OLD / "evidence/entry.json").read_bytes())
    if sha((PROJECT / "tasks/loop-log.md").read_bytes()[:entry["log_prefix_bytes"]]) != entry["log_prefix_sha256"]:
        raise ValueError("ORIGINAL_LOG_PREFIX")
    media = load("offline_review_media", OLD / "tools/check_media.py")
    delivery = json.loads((OLD / "delivery-r4/DELIVERY.json").read_bytes())
    result = media.check(OLD / "delivery-r4/vm164-trusted-bootstrap-fd91b8b07243565e.iso", delivery)
    image = (OLD / "delivery-r4/vm164-trusted-bootstrap-fd91b8b07243565e.iso").read_bytes()
    if any((OLD / build / "probe-data.iso").read_bytes() != image for build in ("media-build-9", "media-build-10")):
        raise ValueError("MEDIA_REPRODUCIBILITY_BYTES")
    lab = load("offline_review_lab", LAB / "tools/lab_package.py")
    binding = json.loads((LAB / "BUNDLE.json").read_bytes())
    metadata, installed = lab.load_bundle(LAB / binding["bundle"], binding["bundle_sha256"])
    if sha(installed["INSTALL-MANIFEST.json"]) != binding["installed_manifest_sha256"]:
        raise ValueError("INSTALL_MANIFEST_PIN")
    sbom = json.loads(installed["SBOM.cdx.json"])
    prerequisites = json.loads(installed["RUNTIME-PREREQUISITES.json"])
    wheels = json.loads((LAB / "WHEEL-PROVENANCE.json").read_bytes())
    # Select metadata already public in the sealed packet. Do not query advisories.
    return {"status": "PASS_REPOSITORY_ARTIFACT_INTEGRITY_ONLY",
            "bootstrap_manifest_sha256": seal["manifest_sha256"],
            "bootstrap_files_verified": len(files), "bootstrap_symlinks_verified": len(links),
            "original_log_prefix_preserved": True, "approved_media": result,
            "builds_9_10_byte_identical": True,
            "bundle_sha256": binding["bundle_sha256"], "bundle_bytes": binding["bundle_bytes"],
            "installed_manifest_sha256": binding["installed_manifest_sha256"],
            "installed_files_verified_in_memory": len(installed),
            "source_revision": metadata["source_git_revision"],
            "wheels_verified_with_RECORD": len(metadata["dependencies"]),
            "wheel_provenance_without_publisher_attestation": [w["name"] for w in wheels
                if "PEP740 signature verified" not in w["provenance_scope"]],
            "missing_license_expression": [w["name"] for w in wheels if not w.get("license_expression")],
            "native_wheels": [w["filename"] for w in wheels if not w["filename"].endswith("-none-any.whl")],
            "sbom_components": len(sbom["components"]),
            "sbom_components_without_licenses": [c["name"] for c in sbom["components"] if not c.get("licenses")],
            "runtime_prerequisites": prerequisites,
            "full_predecessor_verifier_rerun": False,
            "external_home_pins_read_or_executed": False,
            "vm_access_or_payload_execution": False, "live_qualification": False}


if __name__ == "__main__":
    print(json.dumps(review(), indent=2, sort_keys=True))
