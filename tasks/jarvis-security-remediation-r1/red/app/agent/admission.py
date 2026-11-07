"""Bound admission bodies before JSON decoding, including chunked requests."""
import asyncio
from starlette.responses import JSONResponse


class AdmissionBodyLimit:
    def __init__(self, app, max_bytes=262144, read_timeout=5):
        self.app, self.max_bytes = app, max_bytes
        self.read_timeout = read_timeout

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"] not in {"/tasks", "/execution/tasks", "/schedule/jobs"}:
            return await self.app(scope, receive, send)
        lengths = [v for k, v in scope.get("headers", []) if k.lower() == b"content-length"]
        try:
            if len(lengths) > 1 or lengths and (not lengths[0].isdigit() or len(lengths[0]) > 10):
                raise ValueError()
            if lengths and int(lengths[0]) > self.max_bytes:
                response = JSONResponse({"error": "admission_body_too_large"}, status_code=413)
                return await response(scope, receive, send)
        except ValueError:
            return await JSONResponse({"error": "invalid_content_length"}, status_code=400)(scope, receive, send)
        chunks, size = [], 0
        try:
            async with asyncio.timeout(self.read_timeout):
                for _ in range(1024):
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    body = message.get("body", b"")
                    size += len(body)
                    if size > self.max_bytes:
                        return await JSONResponse({"error": "admission_body_too_large"}, status_code=413)(scope, receive, send)
                    chunks.append(body)
                    if not message.get("more_body", False):
                        break
                else:
                    return await JSONResponse({"error": "admission_chunk_limit"}, status_code=413)(scope, receive, send)
        except TimeoutError:
            return await JSONResponse({"error": "admission_read_timeout"}, status_code=408)(scope, receive, send)
        buffered = b"".join(chunks)
        from app.agent.ledger import strict_json
        from app.agent.authority import AuthorityError
        try:strict_json(buffered)
        except AuthorityError:
            return await JSONResponse({"error":"invalid_admission_json","automatic_retry":False},status_code=400)(scope,receive,send)
        delivered = False
        async def bounded_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": buffered, "more_body": False}
            return await receive()
        return await self.app(scope, bounded_receive, send)
