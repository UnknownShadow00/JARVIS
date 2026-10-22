# Continuous improvement register

Implemented J1–J8 in the new isolated candidate: dispatch capability consumption, sender credentials, terminal truth, runner process/IPC isolation, bounded checkpoint snapshots/SQLite work, protected operation envelope, strict denial classification, source/VM/dependency preflight and retained failure evidence. Tests and source diff are attached. Security assertions were not weakened.

Corrected the new runner module import-path error after its focused regression failure. Tightened only newly created candidate test-directory permissions when immutable-manifest validation correctly rejected group write. Corrected effective dependency version capture where system and venv metadata names overlap. These were ordinary engineering fixes, not reasons to request production permissions.

No redesign, historical reboot investigation, Golden re-evaluation, model lifecycle work, production installation, Git commit or push occurred. Remaining work is actual operator-controlled OS qualification and separately approved infrastructure/release decisions, not another hash inside a service-writable trust domain.
