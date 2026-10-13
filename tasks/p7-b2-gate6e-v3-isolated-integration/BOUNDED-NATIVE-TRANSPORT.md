# Bounded native transport

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

`transport.py` implements actual httpx native POST /api/chat handling with an explicitly injected AsyncBaseTransport. No default socket transport exists. It validates exact allowlisted Resource and native options, serialized request hash/size, correlation IDs, ownership lease and absolute deadline. The client disables environment proxy inheritance, redirects and automatic retries; no fallback/discovery/lifecycle endpoint exists.

Response bytes are counted while aiter_raw receives them. Unexpected status/MIME/encoding, duplicate or conflicting length/transfer framing, incomplete length, oversize body, malformed/ambiguous JSON, wrong model, nontrue done, nonassistant message and transport failures fail closed. No raw exception or response content escapes the runtime diagnostics. A valid terminal envelope may release ownership even if downstream content is then rejected as a tool/action proposal.

A borrowed transport wrapper prevents per-operation client shutdown from destroying the shared transport; explicit aclose owns its eventual shutdown. Tests cover the previously missing reusable-client lifecycle. Runtime provider failures and cancellations retain uncertain ownership rather than treating local socket completion as proof.

Qualification uses only httpx.MockTransport and controlled AsyncByteStream fixtures, with kernel AF_INET/AF_INET6/connect denial. Connect/write/read/pool timeout and protocol errors are injected, not real wire failures. Actual HTTP server parser, DNS, TCP fragmentation, proxy infrastructure, OS socket cancellation and real Ollama response identity remain unqualified. No real provider transmissions occurred.
