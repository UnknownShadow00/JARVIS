# REST candidate capture

Existing validated text is `req.message: str` in `app/server.py::chat` (`:357-380`). A future thin capture site could copy that value after FastAPI validation and the wake check, before `_process(req.message)`, once per accepted REST turn. It must not mutate `req`, alter `_process` input, response or timing, or call downstream control plane. **Not frozen as an executable placement** because authoritative P1 session/turn and P2 request-time state are unavailable at this site. No code change.
