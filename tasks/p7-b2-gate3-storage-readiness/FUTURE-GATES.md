# Gate 4 and Gate 5 — exact remaining prerequisites

This is a review packet, not executable authority. Gate3 completed only D06/storage/local-backup readiness. Service remains inactive/LEGACY; private drop-in is on disk and has not been loaded.

## Gate 4 operator decision

1. Review Gate3 STATUS.md, final canonical documentation HEAD and evidence SHA256SUMS, current source/config/unit/drop-in hashes and the new baseline manifest.
2. Separately authorize the exact approved PROPOSED-SHADOW.json mapping (SHA256876adf8971894b00c6ef77659671575bea2546bac5fe19935a052a64d449b660), exact staged configuration diff, execution.mode=shadow, shadow_sample_rate=1.0 and hermes_brain=false. Preserve all other policy, confirmation, provenance, audit and Hermes flags.
3. Name the permitted supervisor sequence explicitly: whether systemctl --user daemon-reload and systemctl --user start jarvis.service are authorized, and what separately supervised evidence-preserving stop is allowed if startup fails. No automatic restart; approved drop-in sets Restart=no and UMask0077.
4. Before any authorized change, reverify service inactive/MainPID0, same installed unit/drop-in, credential metadata only, D06 pinned scope with no current/unknown lease, participating Core callers quiescent, absent controller/epoch, capacity and verified new baseline. Any drift/partial/unknown state requires review; do not repair/reset.
5. If authorized, install only the reviewed configuration change while stopped; revalidate schema/source fingerprints and preserve a fresh secret-free baseline for the applied configuration before startup. Loading the drop-in or starting the service remains forbidden until named in the authorization.
6. Credential content/entropy/authentication remain unverified. Codex must never read the real credential. Any future authenticated probe requires a separately reviewed operator/secret-safe route; do not read the file or pass its value into Codex, arguments, logs, Git or evidence.

## Gate 5 separate zero-generation verification scope

After explicitly approved startup, follow ../p7-b2-supervised-deployment-staging/ZERO-GENERATION-STARTUP-VERIFICATION.md. Verify real MainPID/loaded Restart=no/UMask0077/drop-in paths, eligible PILOT runtime and installed SIGUSR1 handler without sending a signal. Verify a fresh zero-attempt D09 epoch, exact resource/profile/cap4, no receipts/accepted attempts, idle managed D06 and the required verified startup/initialized-epoch checkpoint.

The live zero-attempt epoch belongs to this future startup sequence. Gate3 intentionally did not create it. Credential file presence is not credential load or successful authentication. Operator-private authenticated nonexistent-path and WS handshake/close-without-frames probes need separate explicit scope; health is auth-exempt and insufficient. Avoid model/tool/readiness/voice endpoints, invalid-auth active-pilot probes and all message frames.

Any unknown state, missing handler/checkpoint, auth mismatch, unexpected epoch/PID/restart or resource drift is NO-GO. Preserve partial evidence and use only an explicitly authorized stop action; no automatic restart/reconciliation.

Gate5 verification grants zero traffic authority. Gate6 requires a new explicit first-four-attempt approval (2 REST + 2 WS, sequential, no retries/backlog/tools/voice), plus per-settled-attempt verified checkpoints. Measurement, CT-001/CT-013 and Formal P7 exit remain unapproved.
