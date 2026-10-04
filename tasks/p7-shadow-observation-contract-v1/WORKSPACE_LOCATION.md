# Documentation checkout location

The original documentation workspace filesystem rejected mkdir with OSError errno 28 (No space left on device). Read-only df showed its root filesystem full, while /tmp had available tmpfs space. Canonical Core had ample space and remained clean/unchanged. No files were deleted and no infrastructure, volume, job or service was changed.

The focused documentation checkout is /tmp/jarvis-p7-observation-docs, branch docs/p7-shadow-observation-v1, cloned without hardlinks from the original workspace at exact commit 0b596d7e127f8239596c7152180843e82a15eec7. It has a self-contained git object database and a tasks sparse checkout. Its docs/loop-log changes are committed together in the one focused commit. The original workspace remains clean at its entry commit; no branch/reference there is rewritten. No push is performed.

All final artifacts and the commit are archived in the canonical evidence bundle, including a standalone git bundle, so the tmpfs location is not the sole durable copy. Integration into the original workspace is a later git operation once that filesystem can accept writes; no such operation or disk cleanup is authorized/performed here.
