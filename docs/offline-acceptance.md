# Qualified offline test entrypoints

Use a clean checkout of the exact candidate and the existing qualified local
environment. Do not install or upgrade packages to make acceptance run.

```sh
python3 -B scripts/offline_acceptance.py --output-dir /NEW/PRIVATE/OUTPUT
# Equivalent supported invocation:
python3 -B -m scripts.offline_acceptance --output-dir /ANOTHER/NEW/OUTPUT
```

Both commands run every pinned positive suite, fixed-seed repeats and the
negative/adversarial matrices. They require exact identities and complete
execution, preserve process exits, check source and historical packet integrity,
and put fault injection in disposable copies. There is no partial-suite option.

For safe inventory discovery without importing tests:

```sh
python3 -B scripts/offline_acceptance.py --list-required
```

This emits `INVENTORY_ONLY_NOT_ACCEPTANCE`, never an acceptance PASS. New tests
need explicit safety/enrollment review and separately promoted node/source/policy
digests. The maintainer proposal utility produces candidate files only and is
never invoked by acceptance.

Direct `pytest`, `python -m pytest`, explicit historical/unsafe module selection
and host collection-only commands fail before test imports. Qualified pytest
execution occurs only inside the gate's read-only namespace. `testpaths` and
directory rules separate archived evidence; the child also checks exact permitted
collector files, including explicitly supplied filenames. Intentionally disabling
configuration/plugins or altering trusted code is outside supported invocation.

The 12 archived test modules are forensic data. Their packets are unchanged and
hashed; do not bulk-run their historical Python tools. The 39 out-of-scope and11
unsafe/live-dependent modules remain visible but excluded. Legacy model-profile
tests rewrite project configuration: a future opt-in port must use a disposable
project with synthetic configuration and explicit enrollment, never a live config.
No live-test override flag is provided.

CI calls the same complete entrypoint, with read-only repository permissions and
no persisted checkout credentials. There is no apt/pip/setup-Python or broad
pytest fallback. The standard hosted image is **not claimed qualified**: absent
the pre-provisioned exact environment it fails nonzero before tests. Runner/image
provisioning and remote orchestration qualification are separate operator work;
do not put untrusted PR code on a trusted self-hosted machine to obtain green CI.
Local execution of the exact job command is the offline qualification evidence.

The launcher requires a clean tracked checkout. Preserve a dirty canonical
administrative log: first verify canonical HEAD and all public source bytes,
then use a new clean detached checkout of that exact HEAD for acceptance. Never
stash/reset/commit unrelated work simply to bypass preflight.

Read-only modes and local hashes are integrity checks, not independent custody
or signing. Retain evidence digests independently for any later merge decision.
Passing this gate authorizes no merge, deployment, provider, VM or privileged work.
