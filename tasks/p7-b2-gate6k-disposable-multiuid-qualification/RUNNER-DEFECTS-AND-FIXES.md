# Concrete corrections

| Finding | Reproduction | Small correction | Final evidence |
|---|---|---|---|
| Historical raw tar policy admits symlinks and unsafe metadata before later mode repair | synthetic symlink retained; attempted follow-write refused by GNU tar | strict full archive+manifest validation and exclusive descriptor-based extraction, explicit fresh modes | archive-before/final and malicious archive tests |
| Approval schema accepts a generic VM label without exact Gate6K authorization | incomplete marker accepted by Gate6J validator | exact VMID/UUID/node/machine/disk/console/scope/preservation and source/archive/artifact digests | prefx-reproductions and approval regressions |
| Shared mount propagation accepted | shared:1 root fixture passed old validator | reject shared/master/propagate_from mount metadata | prefx-reproductions and mount tests |
| Volatile mount can cover protected authority despite ext4 root | old validator accepts tmpfs over /var/lib | refuse mounts covering protected state/code/config/interpreter paths and automounts | volatile-authority-before and three new mount regressions |
| Unbounded/ambiguous approval read could accept duplicate keys or block on special files | code path lstat mode+read_text lacked type/size/link/duplicate checks | regular single-link0600 owner check, bounded no-follow read, duplicate-key refusal | marker FIFO/size/duplicate/mode/hardlink tests |
| Interrupted preparation outside old try block could lack structured result | new fault injection creates fixture then interrupts | outer wrapper emits/seals FAIL after creation; BLOCKED before creation; preserves old evidence | FailureEvidenceTests |
| New extractor inherited restrictive umask for directories | captured test failure:0700 versus0755 | set mode only on newly created directories before publication | extractor-umask-before and final tests |

Additional justified preparation:20GiB capacity gate, immutable-artifact byte validator independent of version strings, explicit x86-64/preexisting-tree refusal, fixed creation umask, future allowed-peer invalid/expired-signature checks and service socket mutation attempts. No application/runtime protocol, experiment semantics or production config changed. All changes and tests are in the complete diff. The revised digest requires renewed human approval; older Gate6J approval cannot cover it.

No newly demonstrated authority bypass was left unfixed. Unexecuted privileged paths and missing dependencies remain qualification blockers, not claimed security PASS. The scope is preparation, not a repeated Gate6J audit.
