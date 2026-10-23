# Acquisition and authenticity results

Gate 6L — Nexus-only development evidence. No VM, privileged provisioning, production access, provider generation or pilot activity occurred. Historical Gate 6K source remains unchanged.

345 artifact files totaling3,151,074,186 bytes were acquired or built:109 target public wheels,7 target sdists,193 Ubuntu debs,31 verification-tool wheels, one GPUtil upstream archive, one GPUtil built wheel, one CPython source, one SQLite source and one server ISO. The source release archive and public metadata are additional bundle inputs. The byte catalog records actual URL, size and SHA256 for every artifact.

All 193 debs verify through signed Ubuntu repository metadata; the ISO and CPython source have independent signature verification.43/116 acquired PyPI target release artifacts expose attestations, and all 43 signatures verify; 73 expose no attestation. Of the selected127 distributions,60 have cryptographic publisher/repository provenance:42 selected PyPI wheels plus18 Ubuntu payloads.67 selected distributions have integrity/source-review evidence only. This distinction is preserved in the inventory; TLS and same-index checksums alone are not independent publisher authentication.

Expected publishing repositories were compared to project metadata. NumPy's release repository was checked against its [official release tooling](https://github.com/numpy/numpy-release); Pluggy's identity against its [project documentation](https://pluggy.readthedocs.io/en/stable/). These public identity references are not an operator-approved supplier policy. The [PyPI Integrity API](https://docs.pypi.org/api/integrity/) provenance records and verifier outcomes are retained.

Six interrupted/failed deb transfers were quarantined as zero-byte files outside the deliverable and successfully retried in a new directory. An initial verifier download hit a /tmp quota; a private TMPDIR and disabled cache resolved it. No TLS bypass, private feed, credential or alternate package version was used. Original failure records remain available. The selected source and installation records never reference those incomplete files.
