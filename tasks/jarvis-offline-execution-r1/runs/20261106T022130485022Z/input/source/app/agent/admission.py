"""Bound admission bodies before JSON decoding, including chunked requests."""
from starlette.responses import JSONResponse


class AdmissionBodyLimit:
    def __init__(self, app, max_bytes=262144):
        self.app, self.max_bytes = app, max_bytes

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
        while True:
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
        buffered = b"".join(chunks)
        delivered = False
        async def bounded_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": buffered, "more_body": False}
            return await receive()
        return await self.app(scope, bounded_receive, send)
