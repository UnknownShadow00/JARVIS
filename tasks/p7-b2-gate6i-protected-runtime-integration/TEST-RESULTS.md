# Actual test results

Final Gate6I release-r2: **7719 passed / 11 deselected / zero failures**, 2 existing warnings, full applicable suite on ext4. **95 new focused tests passed on ext4**. Both final stages match all606 source inventory files and the final candidate inventory. Baseline7624 passing tests retained plus95 new cases; none silently skipped or weakened. Historical Golden12/20 with eight known failures unchanged; potentially real Golden evaluation was not run.

| Run | Revision / actual result |
|---|---|
| initial | Early r1:29 new passed/1 failed; test supplied verb twice, corrected authoring error |
| focused-r2 | r1:488 focused passed |
| runtime-r3 | r1:73 passed/1 failed; real listener worker-start/shutdown race fixed |
| runtime-r4 | r1:82 new passed |
| focused-r5 | r1:538 passed/1 failed/1 setup error; content-reader stat comparison incorrectly included read-induced atime, corrected with regression |
| focused-r6 | r1:incomplete, exit120, disposable /tmp disk I/O errors; partial logs/empty artifacts retained, no passing claim |
| focused-ext4-r7 | r1:548 focused passed on ext4 |
| new-ext4-r8 | r1:93 new passed on ext4 |
| full-final | Earlier r1:7717 passed/11 deselected/zero failed/two existing warnings |
| focused-final | Later r1:552 focused passed including explicit protected-command application |
| new-ext4-final | Later r1:94 new passed on ext4 |
| full-release-final | Later r1:incomplete, exit120, /tmp I/O failure; not relabeled a successful run |
| new-r2-final | Final r2:95 new passed on ext4, including FIFO refusal |
| full-r2-final | Final r2:7719 passed/11 deselected/zero failed/2 existing warnings on ext4 |

The intermediate focused-r5 count is derived from its540 selected cases and retained terminal summary (one failed, one setup error). Final counts come from pytest summaries. Full/r2 selection is the same applicable suite policy as Gate6H. No model endpoints were contacted; httpx.MockTransport supplied all new provider responses. Real AF_UNIX sockets/peer credentials, SQLite/fsync and process os._exit crash boundaries ran. Genuine distinct-UID tests did NOT run; neither user-namespace nor numeric-UID mocks are reported as DAC qualification.

Compilation passed for144 app/candidate/runner modules without bytecode. Existing environment pip check passed; no package installed. Crypto tests use existing system cryptography via explicit fixture path; a production dependency lock/environment still needs approval/qualification. Two existing framework deprecation warnings are preserved.

Collected source verification uses each run's archived source, and final runs additionally match the final inventory. Minimized logs are in evidence/runs/. Raw disposable logs remain in their stages. Intermediate incomplete audit files remain explicitly incomplete; final passing runs have complete enforcement evidence. Test fixtures were not promoted to LIVE or human-attested provenance.
