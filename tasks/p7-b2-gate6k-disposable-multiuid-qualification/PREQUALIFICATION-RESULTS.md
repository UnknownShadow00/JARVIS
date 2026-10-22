# Unprivileged prequalification

PASS: Gate6J provenance; archive structural review and actual unprivileged revised extraction; syntax; exact version-lock consistency; all84 runner tests (30 inherited,54 new); bounded marker handling; shared-mount refusal; free-space boundary; artifact hash/missing-record checks; preserved failure evidence; unsafe-target simulations. Actual Nexus invocation refused before fixture creation as BLOCKED. It is not counted as a passed kernel isolation test.

The actual target preflight cannot pass here: Nexus is not the approved VM, no exact Phase B authorization exists, and reviewed offline dependencies are absent. The unprivileged positive environment/UID shapes are fixtures. No user-namespace or mock UID is relabeled as real distinct-UID evidence.

An initial extractor umask test failed and was fixed; its failing output is retained. An initial evidence-writing command used the disposable working directory and failed to find the task output path; rerun used the correct workspace destination. No evidence was overwritten or production state changed. A first r2 test invocation used the workspace cwd and failed module discovery; the corrected package-directory invocation passed84. Both outputs are preserved. All final safe checks passed; full regression results are recorded separately when complete.

Phase A engineering checks are complete for the supplied artifacts. Overall prequalification remains PARTIAL because independent dependency artifacts/runtime verification and the exact human execution environment have not been supplied. Do not claim the full real-VM preflight passed.
