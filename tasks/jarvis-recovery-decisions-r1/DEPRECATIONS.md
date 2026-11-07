# Retained upstream warnings

Final full-app run `20261106T061036551040Z` reports 58 passed with two warnings:
Starlette TestClient deprecates its httpx integration, and its BlockingPortal alias
uses a deprecated AnyIO import. These originate in the retained verified offline
dependency closure and remain visible in stdout. No warning was suppressed, no
vendor source was patched, and no replacement package was installed or downloaded.
The 30 stderr startup config-check lines concern deliberately unavailable synthetic
Piper/model/Ollama readiness; no real provider/model call or production startup is
claimed. Exact stdout/stderr and dependency versions remain in that run.

A future offline compatibility milestone should verify a new dependency closure
and rerun complete supported application scenarios before changing these packages.
