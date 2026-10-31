# Offline source and public artifact provenance R1

Final bounded observation: **2026-10-30T22:24:45.276878+00:00 through 2026-10-30T22:24:49.706205+00:00**.
Authoritative evidence for this report: [evidence-20261030T222449706209Z.json](evidence-20261030T222449706209Z.json).
Profile: `workspace-write`, with writes confined to this new packet.

## Result

The retained Gate6K release and Gate6L dependency bytes match their documented
identities. The current workspace differs substantially from that historical
release. **The historical 7741 passed / 11 deselected result does not apply to the
current workspace.** No historical suite or inspected package was executed.

- Gate6K: 5,386,240-byte archive, 616 regular members, 615 manifest entries; all
  member hashes and all 615 corresponding loose source files match. The loose
  manifest separately matches the pinned manifest digest.
- Gate6L: 3,189,688,320-byte archive, 658 regular members, 657 manifest entries;
  all member hashes and all 657 corresponding loose bundle files match. The loose
  manifest separately matches its pin. No missing/unmanifested archive entries.
- Existing public evidence packets: Gate6K 124/124 and Gate6L 56/56 manifest files
  match; both manifest digests match their retained sibling seals. These are
  integrity observations, not operator acceptance.
- Dependency record: 131 records, including all 127 exact distribution pins; no
  missing distributions, version mismatch, or missing payload digest. Both
  dependency lockfiles are byte-identical to Gate6K. Python 3.14.4, SQLite 3.46.1,
  and cryptography 46.0.5 record values agree; these runtimes were not launched.
- 345 payload artifacts include 141 wheels (109 target download, 31 verification
  tools, one built GPUtil), 193 Debian packages, seven sdists, and four other
  source/OS inputs. Wheel hashes are listed individually in final evidence.

## Exact retained identities

| Object | Path | SHA-256 |
| --- | --- | --- |
| Gate6K source archive | `/home/nexus/.local/share/jarvis-gate6k-prequalification/gate6k-release-r2.tar` | `ec9cc8ea6705149b0c5b9b4b267f604b81def97af8df1254477f8ee1873a778d` |
| Gate6K source manifest | `release-r2/SOURCE-SHA256SUMS` | `5a68588e2153989e2774a6d58c36a2c25f96fbc343c6522f5377c5618183af03` |
| Gate6L bundle archive | `/home/nexus/.local/share/jarvis-gate6l-offline/gate6l-bundle-r1.tar` | `228b008616db3d00fd35c425b590049fce48bcf8b4a3eee2357b444fbed63e00` |
| Gate6L bundle manifest | `bundle-r1/SHA256SUMS` | `1c598e37c69ec2629fed3a3b30652aaf7ec0d2dbfe7906a810fc7036d1b9d390` |
| Gate6L artifact record | `bundle-r1/locks/gate6k-ARTIFACTS.json` | `9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837` |
| Gate6K historical evidence seal | `tasks/p7-b2-gate6k-disposable-multiuid-qualification/SHA256SUMS` | `5bfba9ba2c371435af72fa16a7bf688d4a5aee7ff97c0723ce3f6b532ef492e6` |
| Gate6L historical evidence seal | `tasks/p7-b2-gate6l-offline-dependency-bundle/SHA256SUMS` | `ff82e29f529e9ba1861747cfabe73edb7ac840036f1a1c2301c65fa361ab6b33` |

## Current workspace comparison

The Gate6K manifest names 600 `repo/` paths and 15 external orchestration,
fixture, guard, and disposable-runner files. All 600 repo paths were compared
against this workspace by public byte hash: **267 same, 17 different, 316 absent**.
All 316 unavailable paths raised FileNotFoundError; none was reported merely as
an unexplained hash mismatch. Complete per-path observations, including timestamps
and hashes, are in final evidence. This is a temporal scan, not an atomic checkout
snapshot. Loose source trees were checked only for manifest-listed files; private
work/state trees and unlisted extras were not traversed.

| Path category | Same | Different | Absent |
| --- | ---: | ---: | ---: |
| `app/` | 71 | 12 | 36 |
| `tests/` | 99 | 0 | 118 |
| `scripts/` | 9 | 0 | 0 |
| `candidate_v3/` | 0 | 0 | 24 |

The other 231 baseline paths are documentation, frontends, assets, public
configuration, and historical task artifacts. Current public Python discovery was
limited to `app/`, `tests/`, `scripts/`, and `candidate_v3/`; it found these additional
sources absent from the historical source manifest:

- `tests/test_task_queue_persistence.py`: `bcf83dbce735f2692c8236c5e5b373a6196806c3ad016997f997dcdc3981adb4`, observed 2026-10-30T22:24:45.399769+00:00.
- `tests/test_task_queue_store_safety.py`: `b5ae3964a75a8b20f60a64e20f654a888c9353cc0fabff6c80be30414c60e52d`, observed 2026-10-30T22:24:45.399814+00:00.

All 17 differing paths and both byte identities:

| Path | Gate6K SHA-256 | Current observed SHA-256 |
| --- | --- | --- |
| `CLAUDE.md` | `662ab5dddc240248b23c4de21166b64947a4a16b0fcd4f24a5dc121d0706478a` | `9f638b4b4e26dac7031055b95bb4f7d1c1e5be9f676eba0045b7e0b1605adae2` |
| `PROJECT_STATUS.md` | `9a3f4cd702f7f5d8e02dd0b43418c9fc9642d166bc1bcb5a5d9b20d7970bd52b` | `0afde09c6109392eccd236aa81c0c2c4564096e31fe0bc58a4dcccac913290dd` |
| `app/agent/scheduler.py` | `f8c578d5fbe3925b09134756a96c2df9641d7781950fce68d009e25467e5c099` | `2c2f65d843aa07ab2ff313d5c1d417180d0c68ef2e0d6788a060a24aca9a5dfc` |
| `app/agent/task_queue.py` | `e9df1b2f3b5b3ba243778129080d7c9a84037926e272496f98d0b44726a80c38` | `489d026dc4405d01a32331b477bda657043bae020bf5af51e1b5a6379e4ea8ab` |
| `app/boot.py` | `29365358de5d3cbf1bfd513ad2a925e10c7ba897303ed255a81331bdc96be1aa` | `46a54b70338e2dd1b3a408dcda020fc0cbc080c4f33bc5acfe1d6869d6e12b9e` |
| `app/brain/llm_client.py` | `39068dd123c7b126336707c265399f6b11e92591a29319c4e23a1f626f72b87b` | `f3ac97c4d3d2d079446b1da117d24410c6fa1a1ca448b7b7566f526999cf79bf` |
| `app/brain/planner.py` | `1b359025357cc63002bcfe680ce37981cac66504db27b3eb835621677913d4c3` | `1a6bb736c0d7b5ff9705a41af68e0b9f7d5e524d4481f0e7bb8b7f1ce0879fa2` |
| `app/brain/prompts.py` | `fe51f5ab19ff014890dad170c7ea6e151fcab69571c369cf020de139493f2dd0` | `c750a776f0403a6d1380c714ce272493aee2a87b75d199acfa859667ed82c521` |
| `app/brain/router.py` | `dc2856974cc62fdda48dee835a826bf817b69b47a2e8b2dbeb3be104e8a528f2` | `d44ebf3eedda8456d6ea606897dadb83a433b448dd6e2260912cc87d05a3ace3` |
| `app/brain/tool_embeddings.py` | `d14e96dfaafee90eff51578be5322adc401e418a38d9470b2e3e0979d34fa6f6` | `e471be6b38e2073f64c9fbe5b64098389a4b4d8e9b5e40876bb9d618a7a204da` |
| `app/config.py` | `56654ba5081dd1a3151509cef715ede6a4f346aba7b33da50a4c3a34a7d70b97` | `447a1be6a5950f53adbac4d35b6a51ba6bd62207279774e9fa7183561b930cbf` |
| `app/resource_manager.py` | `20316d6039c41a4fb67bb3b6e71340e8af5c243e79bc931cc5d9832b5df5ad48` | `43e293d07aa7ed33b240c45033912d6a7c45658577367244503356825ec58ed6` |
| `app/server.py` | `cb16b2e95729e55e053de3a647905e028859589698abf28870c6fd3dcd59c57d` | `b1448ed13d5e1d8d9a6afdd00630e394f7c330ec25bd1a63a0ce35ecf3797a70` |
| `app/voice/audio_stream.py` | `c24e2428c5d4180a63d59a389636500f2def63a0c993b192a91058e6f786583f` | `60a3026396b204ffc1e905d2f58c34b3f26c9f7bd7b20d39f0d65577ccdc34c8` |
| `config.yaml` | `247633cbd58a6297cbf94e7b293da905fbe521f1f2964b33bfa10d91c41875a3` | `0aef4931aaaea47ecc087194ae59466cbbda7b71277739e3b27d88ddb8ab5fcd` |
| `config.yaml.example` | `8f5b2343b227641be265087f63192bec50827d2b4eac40031161ce243b067b86` | `3842b214c39816a0dc5a36393512b995a59e9e217bacb11f8784b0a8884b0ea2` |
| `tasks/loop-log.md` | `93831b83c6368a62eaaaf406abb88b912ea73f83fe2586b98aef197c0704f2a0` | `db9e4e32b8204e0be418371e33c5198b732c5993e6ef5d4b629387772e2f8aba` |

The final queue observations agree at 2026-10-30T22:24:45.277019+00:00 and
2026-10-30T22:24:49.700777+00:00: `489d026dc4405d01a32331b477bda657043bae020bf5af51e1b5a6379e4ea8ab` (12,282 bytes).
Each read was stable. Earlier packet observations show parent work in progress
(`e134bb…`, then `c1ce13…`); those values are not described as the final queue source.
The queue is a different identity from historical `e9df1b…`. Neither historical
suite coverage nor historical dependency compatibility transfers to it by hashing.

## Method, safety limits, and corrections

`inspect_provenance.py` uses only the current interpreter's standard library.
Inspected payloads are never imported, run, installed, unpacked, or extracted.
Regular tar members are streamed directly from bounded uncompressed archive byte
ranges. Every source/loose artifact path is opened component-by-component with
no-follow flags, requires a regular final file, and records before/after metadata
and observation times. Archive bytes must first match independently retained pins.
Captured JSON/manifests are limited to 1 MiB; archives and per-archive/loose total
payloads to 4 GiB; members to 3 GiB; current source files to 8 MiB; counts to 2048;
read chunks to 1 MiB. Nonregular, link, sparse, duplicate, unsafe-path and unrelated
PAX metadata entries are rejected.

The approved bundle uses 15 PAX path headers for long public wheel filenames.
Only an exact, safe, bounded `path` override is accepted. The first inspection
conservatively rejected those headers; its evidence is preserved. The second
inspection verified all bytes but initially counted dependency-document metadata
keys rather than the nested `packages` map; that intermediate four-pin result is
superseded. Later evidence fixes the schema and verifies all 127 pins. The final
run above is authoritative. No historical artifact was modified to accommodate
these inspector corrections.

Nine new synthetic inspector tests pass, including no-follow/bounds enforcement,
unsafe/private names, duplicate manifests, actual payload disagreement, pre-parser
archive-pin rejection, link/PAX rejection, and nested distribution-pin counting.
Source-only compile checks pass. See `inspector-tests-20261030T222455234902Z.txt`.

## Blockers and limits

No final artifact hash mismatch or missing sealed file was found. The 17 changed
and 316 absent current workspace paths prevent treating this checkout as Gate6K
release-r2. The 24 historical `candidate_v3/` source paths and the external sealed
runner are not this workspace's runtime; no transplant or runtime setup occurred.
A future regression scope must name its own exact source, harness, dependency,
and interpreter identity. This packet does not run or authorize that regression.

No publisher signature, wheel-internal RECORD, installed-library origin, OS boot,
application integration, cross-UID boundary, power-loss behavior, or VM readiness
was newly qualified. Gate6L's historical 60 signature-backed / 67 weaker-provenance
selected-distribution distinction remains a historical claim; matching retained
hashes adds no publisher signature or operator approval. VM163, Proxmox, guests,
credentials, services, provider/model endpoints, and network were not accessed.
No seals/history/loop logs were edited and no commit was made. Parent owns the
canonical project completion entry after reviewing this packet.
