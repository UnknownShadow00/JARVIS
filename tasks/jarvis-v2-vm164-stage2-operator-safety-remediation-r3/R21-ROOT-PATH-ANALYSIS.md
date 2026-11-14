# R21 root-path analysis — fix blocked

The unchanged independent reproducer fails as reported. In R2 src/inspection.py's METADATA_BODY, `/`.split('/')[1:] produces `['']`. The rule rejecting empty components therefore rejects the mandatory `/` inspection before open/stat.

Only the original pure lexical-validation probe was executed. No host root path was inspected and no future metadata command was run.

Required future correction: handle `/` through an explicitly opened no-follow root-directory descriptor, check its directory type, UID/GID, writable bits and stable filesystem identity, and report its real metadata. Do not bypass custody checks for root. For other paths, retain canonical component rules, descriptor traversal, no-follow policy, ownership/nonwritable ancestry and exact path binding. Preserve callback exclusive-creation and identity checks separately.

Required future tests: `/`; valid ancestors/leaf; symlinked ancestors; writable ancestors; incorrect UID/GID; malformed paths/components; changed filesystem identity; missing leaf versus missing/untrusted ancestry. These new R3 tests and the implementation were not written because source modification is explicitly blocked by missing reviewed-R2 commit identity.
