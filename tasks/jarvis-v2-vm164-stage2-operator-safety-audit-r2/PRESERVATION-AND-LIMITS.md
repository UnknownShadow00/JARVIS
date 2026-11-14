# Preservation, custody and audit limits

The initial inventory reads/hashes all files in four reviewed trees:67 R2 files,29 original preparation files,15 rejection-audit files and96 sealed R3 files. evidence/INPUT-INVENTORY.json records every relative name, byte size and SHA256. The final preservation check compares exact file sets and bytes, not only a count. All207 remain unchanged. No reviewed packet was resealed or regenerated.

Verified pins:

| Object | SHA256 |
|---|---|
| R2 source tree | `3a95bf671008ff46e5e45287c3be58076491c6fed6764cd10c18b906f2bcabea` |
| R2 manifest | `9ce5adc1cb8e76e479339efcc73c7f2848f9154bd545258701694e063314e4d6` |
| R3 source tree | `43ea91000e251b9cf34fadf0466cb5135042a3232686c155de1b4ab5ee1ad3d1` |
| Pinned callback | `a0ba1ef999c58c771e679f3765eac41bb52671968930726a2a4de96a98a301fa` |
| Original preparation manifest | `181620771c9d84aa7874af20b30a632d4e0e53e095678ba1001f34cffb38ba32` |
| Original rejection-audit manifest | `6d7d7ba4a7fd1ca9510b9e6520f604e16fdb2b0aa4c82d2e6ebb27e683ef45fb` |
| R3 manifest | `dd03f4fc5c3b7bf0cd7a5a5beebbabdad5e06ffd4397ab114af280d6fcfc15ea` |

Original and R2 integrity verifiers pass; R3 archive reconstruction and its247-file/five-symlink predecessor chain also verify. Those are integrity results, not newly run historical tests. R01's complete JSON equals the original independent audit file byte-for-byte.

Canonical HEAD observed is `4c0f9ff666ac3bbce5f695a6b071e42320911652`. At audit entry the task log was already modified and R2 was untracked. This audit preserves those changes and adds only its new folder plus a mandatory append-only completion entry. Git shows no canonical application-code diff. No reset, clean, checkout, merge, push or package operation was performed.

The independent harness denies mutation outside this audit (including reviewed packets), disables bytecode output and blocks process/network/signaling/NSS/private-host paths. Disposable fixtures stay under its temporary directory. Result logs and failure traces are retained; no reviewed evidence is overwritten. Local source/data reads, Python tests, artifact writing and read-only git inspection comprise this audit's work.

Local hashes protect byte-consistency relative to recorded pins and start inventory. They are not remote attestation, an independently protected historical custody channel or proof of every external action that could have occurred before this audit. Reviewed engineering source, catalogues and retained logs are consistent with offline-only work and contain no live qualification evidence. The supplied historical host facts remain unrefreshed. This audit itself made no host/network/VM/credential/provider call and supplies no authority for one.

The independent replay found semantic counterexamples even when artifact hashes were correctly recomputed. Those results do not imply cryptographic forgery. A separate test demonstrates that the case-only external seal excludes a top-level privilege-review reference; the full result/review envelope needs coverage in a future revision.
