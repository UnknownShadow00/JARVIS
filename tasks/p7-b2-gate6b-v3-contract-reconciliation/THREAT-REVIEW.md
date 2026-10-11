# Revision2 threat and failure decisions

| Threat | Design requirement / remaining qualification |
| --- | --- |
| Quiet change from SHADOW to Granite-visible pilot | Explicit comparison matrix; legacy-only client/history; unresolved legacy resource contract blocks implementation approval |
| Legacy tool/confirmation/TTS/retry leakage | Capability-limited adapter, no unrestricted handler calls, both-lane proposal abort, source-level dispatch tripwires; actual implementation pending |
| Hidden extra router/model calls | Durable named substep accounting, explicit identities/budgets, endpoint-wide serialization; four accepted attempts is not four total generations |
| Same-UID Codex impersonation / writable code | Dedicated identities, protected complete import/dependency tree, human-exclusive signing/authentication; no same-UID human-only claim |
| Source/config/socket substitution or PID reuse | Protected ancestors, no-follow descriptors, exact release hashes, peer UID/PID/start/boot/invocation, runtime revalidation |
| Privileged helper becomes general root control | Fixed verbs/paths/manifests, bounded signed schema, no arbitrary command/URL/module; separate deployment authority |
| Old/new D06 roots become competing authorities | Quiescent fenced transfer, root-pinned active-root manifest, no old-service reuse, byte preservation, known-caller containment; external clients remain independent |
| Credential copied into evidence or broad ACL | Fresh human-only provisioning; systemd private runtime credential loader; metadata-only agent access; no old token migration by Codex |
| UID migration breaks strict validators | New explicit archival reader and versioned V3 validator; preserve original content/metadata, never globally relax live owner checks |
| Crash mints duplicate successor / resets attempts | Durable fixed reservation before initialization; exactly one child; global immutable accepted IDs; partial state stays held |
| Cross-file checkpoint publication falsely called atomic | Journaled PREPARED→INITIALIZED→READY, fsync ordering and explicit recovery only for same reservation; hardware fault testing required |
| Terminal stop repurposed as pause | Old terminal epoch never reopened; narrow approved zero-use retirement; no automatic interrupted-pilot recovery |
| D04 count used as accepted or generation count | Independent accepted ledger and per-provider substeps; exact receipt joins; no refunds for failure or missing receipt |
| AI identity / lifecycle competition unverified | Console public-key provenance then deliberate pin; fresh actor inventory/exclusive window; no trust from Ollama response/GPU idle |
| Root/hypervisor/storage compromise or host loss | Explicit trusted-base and local-only backup exposure; renewal of bounded risk acceptance; no categorical network exclusivity claim |

Task evidence was restricted to reviewed source, hashes, metadata, fixed event categories and dummy test results. No actual secret, request headers, conversation or provider output was collected. The real token was unavailable for a value-based leakage scan and was not read or hashed to perform one. Prior human auth success remains historical evidence; no new protocol interaction occurred.
