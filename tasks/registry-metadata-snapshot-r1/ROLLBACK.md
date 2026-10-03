# Rollback

Runtime rollback is unnecessary: the module has zero production consumers. Source rollback is `git revert fa8560c943621b9de42aeb5122093b5247c6ccbd`. That removes only the new module and tests; no registry, tool, state, policy or schema cleanup is needed. This task did not perform the revert or push.
