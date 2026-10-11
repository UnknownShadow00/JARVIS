# Shared endpoint and lifecycle inventory

Fresh AI-host lifecycle inspection was **skipped because host trust is unresolved**. Current Ollama PID/start/restart count/version, alias identity, runners, endpoint clients and independent lifecycle jobs are unverified. There was no HTTP fallback, generation, /api/ps, warmup, unload, guest SSH or virtualization operation.

| Participant/evidence | Inspected finding | Scope |
| --- | --- | --- |
| Current Core jarvis.service | PID594042, original invocation, no service children; reviewed PILOT source suppresses scheduler, idle/wake/hotkey/voice/startup workers before registration | Fresh Core read-only metadata and unchanged source |
| Qualified pilot driver | Pinned .200 endpoint/model/profile, D06 acquisition before possible dispatch, no retry/fallback, cap4 | Reviewed source; zero live attempts |
| AI Ollama service | Gate4 Oct9 poststart inventory recorded active/running PID3405, NRestarts0, start Oct4 20:26:50 UTC, Restart=always | Historical sealed observation only |
| AI cron/systemd/accessible schedules | Gate4 inspection found no known competing lifecycle timer/cron marker or competing caller in its unprivileged scope | Historical; not fresh exclusivity |
| B1 qualification callers | Historical qualification clients addressed the exact corrected .200 resource; B1-R2 operator inventory identified Ollama0.35.1, fixed24GiB VM200 and qualified alias | Historical, not evidence that a client cannot run now |
| Other local/network clients, administrators, hypervisor and private schedules | Not categorically excluded; current guest placement and activity remain unknown | Outside current verified boundary |

The approved resource is Ollama/http://192.168.0.200:11434/hermes-candidate-granite41-30b-q3km-64k, profile jarvis.p7.ollama.granite41.b1r2.v1, context64000. None was recreated or changed.

D06 is a reviewed **Core-local cooperating ownership protocol**, not an Ollama server admission controller. Its clean current/last state does not prevent an external client, another Unix account, root or hypervisor automation from issuing generation/load/unload operations. Runner absence, empty sockets, GPU idle and elapsed time cannot establish terminal completion or ownership. Historical Ollama Restart=always is an independent lifecycle participant requiring fresh supervision; an unexpected restart during a request cannot be treated as a terminal response.

Before the four-attempt pilot, require an explicitly reviewed exclusive-use arrangement: trusted fresh host/service/runner/client inventory; named operator reservation of this exact endpoint for the whole supervised window; containment of known competing clients and model lifecycle automation through separately authorized procedures; monitoring of observable service identity and conflicting actors. No disabling or firewall change is proposed as an implicit part of Gate6A. If adequate containment cannot be established, block opening.

Even after an inspected absence of known competitors, arbitrary privileged/network actors remain a stated trust assumption. A conflicting actor, process/version drift, unload/warmup/restart or remote uncertainty closes subsequent admissions, preserves D06 evidence and requires review. It never authorizes model force-kill, lease clearing or automatic retry.

Once public-key trust/access is independently established, the narrow fresh check is fixed read-only systemd properties for Ollama, safe process metadata, installed version identity, existing alias metadata and accessible lifecycle/client inventory. No model-capable health check or generation is necessary. Preserve historical and fresh records separately.
