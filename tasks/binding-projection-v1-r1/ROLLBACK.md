# Rollback

Runtime rollback: none, because `binding_projection.py` has zero production consumers. Source rollback: `git revert d3f44e01e7c63b0c2ba6f52f2dc93c48af34b69c`; it removes the passive producer and focused fixtures and returns the four gate tests to their earlier phase state. No registry, tool, confirmation, audit, policy or state cleanup is needed. No rollback or push was performed.
