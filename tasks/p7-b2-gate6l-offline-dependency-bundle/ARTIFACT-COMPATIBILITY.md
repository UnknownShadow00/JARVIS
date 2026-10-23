# Artifact compatibility

Gate 6L — Nexus-only development evidence. No VM, privileged provisioning, production access, provider generation or pilot activity occurred. Historical Gate 6K source remains unchanged.

PASS: Linux x86-64 CPython 3.14 wheel-tag compatibility; exact 127 installed distribution identities; downloaded Python 3.14.4; Python-linked private SQLite 3.46.1; cryptography 46.0.5 Ed25519; private libseccomp 2.6.0; FastAPI/NumPy/Pydantic imports; pip dependency check;191-package Debian Depends/Pre-Depends closure including versioned virtual providers.

The full package inventory includes distro-specific administrative software. Those Python payloads are never invoked, and their maintainer scripts/services are never installed. Metadata compatibility does not establish that every administrative utility works in a private virtualenv. This is sufficient artifact/runtime preparation evidence, not a claim of full OS or V3 application qualification.

Initial failures correctly exposed two nonportable assumptions: a127-line pip inventory is not a wheel-only lock, and matching distribution versions can conceal a missing native CFFI backend. The mixed route preserves all 127 versions and uses the correct distro backend. Root-owned runtime placement and the exact runner invocation under four UIDs still require review on the approved guest. No full application rerun was needed or performed; historical 7741 passed /11 deselected /0 failed remains unchanged.

No virtual machine, distinct-UID test, GPU, live provider, model attestation, Golden evaluation or production check ran. Guest ISO boot and real cross-UID runtime loading remain NOT RUN.

Gate 6K evidence-record interoperability:131 exact records PASS through the unchanged historical verifier, using safe digest aliases. Record SHA256 `9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837`. This does not grant human provenance approval.
