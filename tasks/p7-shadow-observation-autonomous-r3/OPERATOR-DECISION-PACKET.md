# Consolidated R3 operator decision packet

JARVIS PASSIVE SHADOW OBSERVATION V1 BLOCKED

TOTAL NEW AUTHORIZATIONS REQUIRED: **1 corpus-revision approval**.
TOTAL NEW PRE-EXISTING STRUCTURAL TEST AUTHORIZATIONS REQUIRED: **0**.

The full sweep found exactly the already-approved ten transitions, not an eleventh. It scanned every one of 151 Python test files, 3,082 AST assertions and 170 candidate functions, including generic production traversals, declarer/consumer sets, absence gates, helpers and the PB04 sealed-corpus callers. Candidate full regression confirms no additional pre-existing test failure.

| Request | Exact conflict | Narrow decision | Security effect |
|---|---|---|---|
| C01: additive correction of this session's frozen corpus | 12 focused and 9 unseen PipelineStop expected records retain candidate_source=MODEL_RAW from the conversation expectation template; D03 requires None | Approve a new versioned corpus with only those 21 expected.record.candidate_source values changed to null. Preserve originals, hashes, absent-module first-fail and first implementation/full scores. Explicitly authorize pre-run addition of the malformed-input hardening cases below. All other frozen expectations remain unchanged; no D03 schema or existing gate change | Restores stopped/candidate distinction and prevents model-source promotion; retains evidence of the erroneous first score |

This was an agent-authored expectation error, not a production requirement or an operator mistake. R3 §23 says “Do not rewrite expectations.” The earlier first-fail requirements also prohibit changing frozen expectations after the implementation run. Therefore the original corpus has not been rewritten, the defective expectation has not been implemented, and no passing implementation/commit is claimed.

Exact affected case IDs, field replacements and proposed JSON are under proposals/corpus-correction-table.json, proposals/corpus-correction.patch and proposals/corrected-corpus/. They are review artifacts, not applied/scored replacements.

Review also identifies authorized implementation hardening before any next score: check primitive map entries before copying a mapping (avoids user-defined key hash execution); check ordinary dataclass metadata type before reading its frozen flag; translate unencodable canonical text into a fixed ValueError rather than expose a UnicodeEncodeError payload. These need no additional existing-test exception or engine/type dependency. Proposed source/patch are archived under proposals/. New pre-run cases should trap malicious key hashes, forged dataclass metadata/property reads and unpaired surrogate canonical text. Strengthen the new structural helper for the reviewed type-metadata read and map.items receiver, and add direct socket/filesystem/clock traps to the existing profile-based runtime guard. Do not weaken any owner-engine call/import budget.

Current outcome: candidate first focused implementation 79 passed / 12 failed / 12 unseen deselected; candidate full regression 5,921 passed / 21 failed / 11 deselected, all failures the same stopped-source expectation defect. Every old test passed under the exact ten authorized transitions. All candidate focused/unseen forbidden-event profile counts were zero. No other implementation pass or authenticity claim is made.

All 12 candidate source/test/corpus files and the complete diff are archived. The eight edited pre-existing test files were restored byte-for-byte; the four task-created candidate files were removed only after byte-identical archive verification. Production HEAD, every tracked entry byte and clean status are restored; observation is absent. Restored regression is 5,839 passed / 11 deselected / 0 failed. No commit or push.

Recommended single operator batch: C01 only, preserving the ten existing authorizations and R3 transitive-import clarification. No canonicalizer/router/permission/binder/pipeline/model/tool execution permission is requested.
