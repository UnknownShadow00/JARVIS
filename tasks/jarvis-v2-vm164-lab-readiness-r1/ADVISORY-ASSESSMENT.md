# Fresh advisory verification — findings present

Fresh HTTPS OSV batch queries completed successfully for all31 exact Python wheel
pins and13 unique locked npm package/version pairs. All28 returned advisory IDs
were retrieved in full and retained with hashes under evidence/advisory-records.
The query/result order and full request/response data are preserved in
ADVISORY-RESULTS.json and ADVISORY-DETAILS.json. No package or lockfile changed.

| Component | Exact pin | Returned records | Deployment implication |
|---|---|---:|---|
| Python certifi | 2026.7.22 | 2 alias records for the emSign CA issue | Not cleared for external TLS/networked use; OSV identifies fixed2026.10.18. A separately verified successor lock/release and affected regression are required before that use. |
| Electron | 42.10.1 | 8 GHSA records | Frontend/browser deployment remains blocked; no Electron binary is installed by this headless bundle. |
| undici | 7.29.0 | 18 GHSA records | Frontend/network client deployment remains blocked; npm artifacts are lock metadata only here. |

Certifi records are GHSA-6q48-6c7w-9gw2 and PYSEC-2026-4320. The pinned wheel
still contains the CA data reported affected by OSV. This is a known finding, not
unavailable data or a clean audit. All Python source and package versions remain
exactly Unified RC1; no silent trust-store edit or dependency upgrade invalidates
its identity. The isolated smoke has no external route/credential and does not
qualify this vulnerable CA trust for real connections. Installing dormant data and
running a verified no-network synthetic cage does not waive later deployment gates.

The other queried pins have no returned records in that response snapshot; this
is not proof of absence of vulnerabilities. This check covers the31-wheel minimal
closure and locked13 npm pairs only. Native OS/CPython/OpenSSL/SQLite/bwrap packages,
the full127-package historical tool environment, models, optional desktop/provider
packages, installed binaries and actual VM164 OS advisory state are NOT freshly
qualified. Those unavailable installed facts remain blockers.

Primary API documentation: https://google.github.io/osv.dev/post-v1-querybatch/
Exact machine-readable findings: ADVISORY-RESULTS.json, ADVISORY-DETAILS.json.
No failed/paginated query was treated as a clean result. There was no pagination
in the retained successful batch. No real provider, guest or Proxmox mutation
request was used for advisory work.
