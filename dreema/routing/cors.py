"""CORS validation helper for Dreema routing."""

from helpers import settings
from requests import Request
from responses import SysCodes, SysMessages
from helpers import Json


class Cors:
    """Validate CORS policies for incoming ASGI requests."""

    def __init__(self, request: Request):
        self.request = request
        self.cors = settings("CORS")

        # setting default values
        self.cors = Json(self.cors or {})
        if not getattr(self.cors, "allowedOrigins", None):
            self.cors.allowedOrigins = ["*"]
        else:
            self.cors.allowedOrigins = self.cors.allowedOrigins

        #
        if not getattr(self.cors, "allowedMethods", None):
            self.cors.allowedMethods = ["get", "post", "put", "delete"]
        else:
            self.cors.allowedMethods = [
                method.lower() for method in self.cors.allowedMethods
            ]

        #
        if not getattr(self.cors, "allowCredentials", None):
            self.cors.allowCredentials = False

        #
        if not getattr(self.cors, "notAllowedHeaders", None):
            self.cors.notAllowedHeaders = []
        else:
            self.cors.notAllowedHeaders = [
                header.lower() for header in self.cors.notAllowedHeaders
            ]


    def process(self):
        """Evaluate CORS policy for the current request.

        Returns:
            Json: A result indicating whether the request is allowed.
        """
        method = self.request.method()
        headers = self.request.headers()

        try:
            if (
                "*" not in self.cors.allowedOrigins
                and headers.origin not in self.cors.allowedOrigins
            ):
                return Json(
                    {
                        "data": None,
                        "message": SysMessages.CORS_ORIGIN_NOT_ALLOWED,
                        "status": SysCodes.CORS_ORIGIN_NOT_ALLOWED,
                    }
                )

            if (
                "*" not in self.cors.allowedMethods
                and method.lower() not in self.cors.allowedMethods
            ):
                return Json(
                    {
                        "data": None,
                        "message": SysMessages.CORS_METHOD_NOT_ALLOWED,
                        "status": SysCodes.CORS_METHOD_NOT_ALLOWED,
                    }
                )

            if set(headers) & set(self.cors.notAllowedHeaders):
                return Json(
                    {
                        "data": None,
                        "message": SysMessages.CORS_HEADER_NOT_ALLOWED,
                        "status": SysCodes.CORS_HEADER_NOT_ALLOWED,
                    }
                )

            return Json(
                {
                    "data": None,
                    "message": SysMessages.CORS_NO_ISSUES,
                    "status": SysCodes.CORS_NO_ISSUES,
                }
            )
        except Exception as e:
            return Json(
                {
                    "data": None,
                    "message": f"{SysMessages.CORS_ERRORS} {e}",
                    "status": SysCodes.CORS_ERRORS,
                }
            )
