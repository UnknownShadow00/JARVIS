# Rollback
At clean production HEAD db54d615c3ee023d753e86143860c4efdc251230, run git revert --no-edit db54d615c3ee023d753e86143860c4efdc251230 using the established repository commit identity.
This removes only the new adapter, test modules/corpora and restores the two prerequisite tests exactly to parent 4885c4f7ca35f2395fab3497e6ce009d36b742be.
Expected verification after revert: full suite returns to 5245/11; golden stays 12/20 same eight; legacy probe unchanged. No runtime restart, flag edit or data migration is needed because zero live consumers exist.
Old test blobs and exact diff are in the new evidence bundle. Do not delete historical evidence or reset/squash production history.
Revert the separate workspace docs commit only if the operator wants the documentation removed; preserve loop-log and sealed evidence as history.
