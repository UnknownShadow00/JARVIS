# Server attachment finding

Canonical planned point is `app/server.py::_process` at entry (`task13b11a/FEATURE_FLAG_AND_ROLLBACK.md:30-35`). REST `/chat` reaches it, but `/ws` first uses `_process_stream` (`app/server.py:524-529`), which can return a streamed reply without calling `_process`. Thus the planned point is **not an all-ingress capture point**.

Required future behavior: capture only the already-authenticated request text and JARVIS state once per turn, read `execution.mode` once, run legacy unchanged, ignore shadow output for response, and never pass server or registry objects into shadow. A copy before stream selection could cover both transports, but is not prescribed by the one-branch plan. The operator must approve an exact location/coverage strategy before implementation; no server edit is authorized here.
