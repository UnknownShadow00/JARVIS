# Human-only Gate 2B handoff

**GATE 2A COMPLETE — HUMAN GATE 2B ACTION REQUIRED.** The credential parent is0700; p7-b2.env is absent. Codex did not create or read a credential and did not install the drop-in.

1. In a private interactive terminal on Core, as jarvis UID1000, disable shell tracing and terminal transcription/HTTP debug logging. Confirm you are on Core, all credential ancestors are real directories with expected ownership, parent0700, and the target is absent. Stop on a symlink, ownership drift or existing/partial target.
2. Independently generate a cryptographically strong URL-safe token with at least32 random bytes of entropy using your trusted password manager outside Codex. The routine validates text shape and equality, not entropy; the independent generation method must supply the entropy.
3. Run the exact reviewed hidden-input routine from the committed documentation text:

~~~sh
cd /home/jarvis/JARVIS
.venv/bin/python -B tasks/p7-b2-gate2-security-preparation/HUMAN-ONLY-ROUTINE.txt
~~~

This is a HUMAN command in your private terminal, not a Codex action. Paste the secret only into the two hidden prompts. No token in shell arguments, commands, URLs, stdin redirection, chat, Git, logs or evidence. The routine imports secrets only for constant-time equality; it does not generate a token. The existing target causes exclusive creation to fail; preserve partial/failed files for review rather than replacing them.

The routine below is byte-for-byte extracted from the reviewed AUTH-PROVISIONING-GUIDE.md (guide SHA25632b5c948ebe15ebbb38d2917507772667bafd91b27b91ce59039c404dcd566b7):

~~~python
import getpass, os, re, secrets, stat
from pathlib import Path
parent = Path('/home/jarvis/.config/jarvis')
assert not parent.is_symlink()
assert parent.stat().st_uid == os.geteuid()
assert stat.S_IMODE(parent.stat().st_mode) == 0o700
token = getpass.getpass('Private deployment token: ')
confirm = getpass.getpass('Confirm privately: ')
assert re.fullmatch(r'[A-Za-z0-9_-]{43,256}', token)
assert secrets.compare_digest(token, confirm)
os.umask(0o077)
fd = os.open(parent/'p7-b2.env', os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW, 0o600)
try:
    with os.fdopen(fd, 'w', closefd=False) as stream:
        stream.write('JARVIS_API_TOKEN=' + token + '\n')
        stream.flush()
        os.fsync(stream.fileno())
finally:
    os.close(fd)
directory = os.open(parent, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
try:
    os.fsync(directory)
finally:
    os.close(directory)
~~~

On success, report only that the private human step completed. Do not send the token, file contents, length, hash or environment output. Codex can then recheck regular-file/no-symlink/UID1000/mode0600/no-ACL metadata and the existing unit before conditionally installing the already approved drop-in.

Do not reload systemd or start/stop/restart JARVIS. Do not perform auth probes, provision D06 or activate SHADOW. File presence is not evidence that the service loaded the credential.
