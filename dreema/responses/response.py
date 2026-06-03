"""ASGI response builder for Dreema.

This module serializes controller responses into HTTP responses and applies
standard headers and CORS settings.
"""

import json
from dreema.helpers import settings


class Response:
    """Wraps ASGI send behavior to emit HTTP responses."""
    def __init__(self, request, send) -> None:
        self.request = request
        self.send = send

    async def response(self, content):
        """Serialize the controller response and send it as an ASGI HTTP response.

        Args:
            content: The controller response payload, which may be a dict,
                string, bytes, list, set, or other serializable object.

        Returns:
            None: Sends the response via ASGI send.
        """

        # Handle OPTIONS request
        if self.request.method() == "OPTIONS":
            origin = self.request.headers().get("origin", "*")

            await self.send({
                "type": "http.response.start",
                "status": 204,
                "headers": [
                    (b"access-control-allow-origin", origin.encode()),
                    (b"access-control-allow-methods", b"OPTIONS"),
                    (b"access-control-allow-headers", b"Content-Type, Authorization"),
                    (b"access-control-allow-credentials", b"true"),
                    (b"content-length", b"0"),
                ]
            })
            
            await self.send({
                "type": "http.response.body",
                "body": b""
            })
            return

        statuscode = 200
        headers = {}
        body = b""
        contentType = "application/json"

        dictLike = isinstance(content, dict) or (hasattr(content, "get") and hasattr(content, "pop"))

        if dictLike:
            custom = content.get("custom") if isinstance(content, dict) else getattr(content, "custom", None)
            if not custom:
                content = dict(content)
                statuscode = content.pop("statuscode", 200)
                if settings("environment", 'local') not in ["debug", "local"]:
                    content.pop("trace", None)
                headers = content.pop("headers", None) or {}
                body = json.dumps(content).encode("utf-8")
            else:
                statuscode = content.get("statuscode", 200) if isinstance(content, dict) else getattr(content, "statuscode", 200)
                headers = content.get("headers", {}) or {} if isinstance(content, dict) else getattr(content, "headers", {}) or {}
                content = content.get("data", content) if isinstance(content, dict) else getattr(content, "data", content)
                if isinstance(content, bytes):
                    body = content
                    contentType = headers.get("Content-Type", "application/octet-stream")
                    if isinstance(contentType, bytes):
                        contentType = contentType.decode("latin-1")
                elif isinstance(content, str):
                    body = content.encode("utf-8")
                    contentType = "text/plain; charset=utf-8"
                elif isinstance(content, (list, dict)):
                    body = json.dumps(content).encode("utf-8")
                else:
                    try:
                        body = json.dumps(content, default=lambda x: list(x) if isinstance(x, set) else str(x)).encode("utf-8")
                    except Exception:
                        body = json.dumps({"error": "Response serialization failed"}).encode("utf-8")
        else:
            if isinstance(content, bytes):
                body = content
                contentType = "application/octet-stream"
            elif isinstance(content, str):
                body = content.encode("utf-8")
                contentType = "text/plain; charset=utf-8"
            elif isinstance(content, (list, dict)):
                body = json.dumps(content).encode("utf-8")
            else:
                try:
                    body = json.dumps(content, default=lambda x: list(x) if isinstance(x, set) else str(x)).encode("utf-8")
                except Exception:
                    body = json.dumps({"error": "Response serialization failed"}).encode("utf-8")


        # Fetch CORS settings
        cors = settings("CORS", {})
        allowed_origins = cors.get("allowedOrigins", ["*"])
        if "*" in allowed_origins:
            allowed_origins = [self.request.headers().get("origin", "https://unknown.com")]

        allowed_methods = cors.get("allowedMethods", ["GET", "POST", "PUT", "DELETE"])
        allowed_headers = cors.get("allowedHeaders", ["*"])
        allow_credentials = cors.get("allowCredentials", False)

        # Build default headers
        default_headers = [
            (b"content-type", contentType.encode("latin-1")),
            (b"access-control-allow-origin", allowed_origins[0].encode("latin-1")),
            (b"access-control-allow-methods", ", ".join(allowed_methods).encode("latin-1")),
            (b"access-control-allow-headers", ", ".join(allowed_headers).encode("latin-1")),
            (b"access-control-allow-credentials", b"true" if allow_credentials else b"false"),
            (b"content-length", str(len(body)).encode("latin-1")),
        ]


        # Append custom headers safely


        # Append custom headers safely
        for key, value in headers.items():
            if isinstance(value, bytes):
                encoded_value = value
            else:
                encoded_value = str(value).encode("latin-1")
            default_headers.append((key.encode("latin-1"), encoded_value))

         # Send response
        await self.send({
            "type": "http.response.start",
            "status": statuscode,
            "headers": default_headers
        })

        await self.send({
            "type": "http.response.body",
            "body": body
        })