# Current dependency warning investigation

The final full-application run retains exactly two upstream warnings. Fresh
read-only source inspection of the retained target confirms the previous analysis:
FastAPI re-exports Starlette TestClient; Starlette falls back to httpx0.28.1 when
its preferred httpx2 extra is absent, emitting StarletteDeprecationWarning.
Starlette also references anyio.abc.BlockingPortal, deprecated by retained AnyIO
in favor of anyio.from_thread.BlockingPortal. [DEPRECATIONS.json](DEPRECATIONS.json)
binds exact source hashes and inspection method.

No JARVIS application call uses either deprecated dependency interface directly.
HTTP/websocket regressions retain their existing useful TestClient coverage.
Patching retained packages, filtering warnings, adding an unverified package or
changing the framework merely to silence these warnings would break the verified
dependency identity or expand architecture scope. A separate verified offline
compatibility closure is the next dependency task. No install/download or external
lookup was performed; packages and historical evidence remain unchanged.

The 21 stderr startup lines in the final app run are expected synthetic config
checks: seven each for absent Piper binary, absent Piper model and unreachable
isolated loopback Ollama. They are not model calls. Actual network canaries prove
IPv4/IPv6 unreachable before importing the app. All warnings remain in run output.
