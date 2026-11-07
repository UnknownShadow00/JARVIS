# Dependency warning investigation

The retained exact28 dependency target is unchanged and remains read-only.
The independent reviewer inspected its source and METADATA as data:

- FastAPI 0.141.1 re-exports Starlette's TestClient.
- Starlette 1.6.0 testclient.py lines35–51 falls back to retained httpx0.28.1
  because its preferred httpx2 extra is not in the verified target. It emits
  StarletteDeprecationWarning recommending httpx2.
- Starlette testclient.py line53 references anyio.abc.BlockingPortal. In retained
  AnyIO4.15.1 that alias is deprecated in favor of anyio.from_thread.BlockingPortal.

Neither warning originates in JARVIS application code. The regression suite uses
TestClient for HTTP and websocket authentication. Replacing that transport solely
to silence these warnings would discard useful coverage or add unrelated test
architecture. Installing httpx2 or changing Starlette needs a new verified offline
dependency closure and compatibility validation. No such change is included here.

No warning filters were added, no retained package was patched, and no evidence
or dependency manifest was rewritten. The warnings remain visible in full-app
stderr/stdout evidence. They are recorded limitations, not failed security gates
or a claim that optional runtime dependencies were qualified.
