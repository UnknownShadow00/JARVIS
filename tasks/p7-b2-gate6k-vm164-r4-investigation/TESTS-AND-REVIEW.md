# Synthetic validation and review

Run on Nexus only, with standard-library unittest and no dependency installation. Interpreter and command results are retained in `evidence/verification.json`. No synthetic fixture is represented as a raw observation of VM164.

```bash
python3 -B -m unittest discover -s tasks/p7-b2-gate6k-vm164-r4-investigation/tools -p test_proposal.py -v
```

Final new suite: **28 tests passed, zero failures**. Table entries with several values are unittest subtests/loops, not additional independently counted tests. The original 18-test r4 suite is rerun separately as a preservation/regression check; its PASS is not evidence the r4 inheritance bug is fixed in the original file.

| Coverage | Expected result / evidence |
|---|---|
| Blank single correctly identified disk | Prototype final predicates accept; no write authorization emitted |
| Inherited partition serial/short/path | Original r4 exact reported error reproduced; prototype identity passes, installation admission refuses partitions |
| Partitions with empty signature list | Refuse; signature absence cannot override topology |
| Two whole disks: distinct/cloned/partial identity, read-only or writable, partitioned second disk | Refuse even when path matcher would select only sda |
| Optical identity conflict | Refuse for each target identifier |
| Wrong/missing udev, incomplete inventories, duplicate path or major:minor | Refuse |
| Wrong UUID, nonroot, NIC, serial, size, model, target RO/removable | Refuse |
| GPT, PMBR, MBR, ext4, LVM and RAID signatures; malformed/missing report | Refuse |
| Filesystem/partition-table type with no signatures | Refuse |
| Mount, swap, holders, slaves, missing safety metadata | Refuse |
| dm/LVM/RAID/crypt/multipath/zram/unknown types | Refuse |
| Loop device | Require RO and synthetic trusted-backing contract; writable or unknown origin refuses |
| Mislabeled partition, inconsistent parent, orphan, kernel kind mismatch | Refuse |
| Pinned first early failure | Exact startup AST never reaches normal controller startup/full reload and never writes a success stamp |
| Pinned early success | Stamp written after early command and before controller startup |
| Pinned startup with existing success stamp | Early command skipped; controllers start — demonstrates restart limitation |
| Independent writer alongside a failing guard | Inert startup fails while a separate task writes a temporary **regular text file**; demonstrates lack of cancellation boundary only |

The startup tests execute the actual retained `start()` AST inside an inert fake application. API server, cloud-init, controllers, `open`, clock sleeps and command exits are replaced by controlled collaborators. `dry_run=True` avoids the casper marker branch, not the early-command branch. These tests prove local control-flow properties of that method. They do not execute a real server, invoke curtin, exercise a kernel block device, or reproduce actual VM164 partitioning. The independent-writer test is a model of the missing exclusion property, not attribution.

The first test-first record (`tests-red.txt`) is an expected missing-module import error before the prototype existed, **not** a reproduced behavioral failure. The behavioral r4 reproduction is a passing regression assertion in the final suite. No inflated TDD or coverage claim is made.

## Final self-review

- Confirmed the embedded r4 guard/config match the sealed prior packet and retained ISO. Confirmed prior manifest/source hashes before importing read-only parsing helpers. All 33 prior r4 manifest members reverify; no prior artifact is rewritten.
- Reviewed classification before filtering. Whole disks cannot be silently discarded as nonmatching or read-only. Only independently parented partitions are omitted from uniqueness; initialization refusal remains separate. Unsafe/ambiguous graphs refuse.
- Retained optical/loop collision refusal and exact independent UUID/hardware/udev checks. No override/marker/installer entry point or production code change exists.
- Corrected the interpretation of absent target mounts: on-disk formatting precedes extraction/late commands and need not imply a current mount. The first failure is not asserted to be the first invocation; operator-confirmed automatic origin is recorded explicitly.
- Documented the cached-early-stamp limitation, cloud-init/boot exposure, config precedence, transient-job lifetime and explicit curtin stage selection. Did not equate in-memory model changes with disk writes or attribute a writer without logs.
- Reviewed the proposed operator shell block for read-only diagnostics, exact UUID/boot binding, RAM-only output, protected files, memory/file/time bounds, exit records and no lifecycle/storage mutation. It is syntax-checked only and requires separate approval; no guest command was executed.
- The prototype trusts its supplied snapshot contract. Real sysfs collection, cross-namespace usage/openers, authenticated media/config binding, fresh measurement, kernel/backend write protection and exclusive supervision are **not implemented**. That is an explicit deployment blocker, not a qualified safety guarantee.

No dependency audit is needed for this uncommitted standard-library-only isolated proposal; dependencies did not change. No commit/push or production test was performed. The applicable live protection/integration tests in REVISED-DESIGN remain NOT RUN. Independent operator review remains pending.
