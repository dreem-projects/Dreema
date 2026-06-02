from datetime import datetime
from helpers import Json
from responses import SysCodes, SysMessages
from files import FileParser
from urllib.parse import parse_qs
import json
from dreema.security import authenticate


"""ASGI request helper for Dreema.

Manages request metadata, body parsing, query decoding, and validation.
"""

class Request:
    """Encapsulate an ASGI request and provide reusable request helpers.

    Attributes:
        scope (dict): ASGI scope for the request.
        receive (callable): ASGI receive coroutine.
        send (callable): ASGI send coroutine.
        _body (Json|None): cached parsed request body.
        _pt (dict): stored path parameters.
    """
    def __init__(self, scope, receive, send) -> None:
        """
        Receives the scope, receive and send from the uvicorn server
        """
        self.scope = scope
        self.receive = receive
        self.send = send
        self._body = None
        self._pt = {}

    def setNewBody(self, data: dict):
        """Replace the cached request body with provided data."""
        self._body = Json(data)

    async def user(self, *args, **kwargs):
        """
        Authenticate the request using the registered auth handler.
        
        All args and kwargs are passed to the auth handler.
        
        Example:
            # In your controller
            user = await request.user(types=['admin', 'student'])
            user = await request.user(roles=['manager'], permissions=['read', 'write'])
        
        Returns:
            Json: Authentication result from the handler
        """
        return await authenticate(self, *args, **kwargs)
    
    async def applyRules(self, rules: dict, body: dict = None):
        """
        Use:
            Useful for validating request body checking for
            parameters like required property, and variable types

        Parameters:
            Rules to be checked

        Returns:
            json: A json serialized response containing the body
        """
        body = body if body else await self.body()
        systemrules = ["required", "int", "str", "float", "list", "bool"]

        for key, rule in rules.items():
            indRules = rule.replace(" ", "").split(",")
            for r in indRules:
                if body.get(key, "None") == "None" :
                    return Json(
                        {
                            "data": None,
                            "message": f"{key} is required",
                            "status": SysCodes.ATTR_MISSING,
                        }
                    )

                try:
                    index = systemrules.index(r)
                    match index:
                        case 1:
                            if not isinstance(body.get(key, None), int):
                                return Json(
                                    {
                                        "status": SysCodes.ATTR_MISSING,
                                        "data": None,
                                        "message": f"{key} must be of type int",
                                    }
                                )
                        case 2:
                            if not isinstance(body.get(key, None), str):
                                return Json(
                                    {
                                        "status": SysCodes.ATTR_MISSING,
                                        "data": None,
                                        "message": f"{key} must be of type str",
                                    }
                                )
                        case 3:
                            if not isinstance(body.get(key, None), float):
                                return Json(
                                    {
                                        "status": SysCodes.ATTR_MISSING,
                                        "data": None,
                                        "message": f"{key} must be of type float",
                                    }
                                )
                        case 4:
                            if not isinstance(body.get(key, None), list):
                                return Json(
                                    {
                                        "status": SysCodes.ATTR_MISSING,
                                        "data": None,
                                        "message": f"{key} must be of type list",
                                    }
                                )
                        case 5:
                            if not isinstance(body.get(key, None), bool):
                                return Json(
                                    {
                                        "status": SysCodes.ATTR_MISSING,
                                        "data": None,
                                        "message": f"{key} must be of type bool",
                                    }
                                )
                except Exception as e:
                    return Json(
                        {
                            "status": SysCodes.ATTR_MISSING,
                            "data": None,
                            "message": f"{r} request rule not applicable",
                            "trace": f'An error occurred - {e}',
                        }
                    )

        return Json(
                        {
                            "status": SysCodes.ATTR_FOUND,
                            "data": body,
                            "message": SysMessages.ATTR_FOUND
                        }
                    )

    async def trimApplyRules(self, rules: dict, body: dict = None):
        """
            Use:
                Useful for validating request body checking for 
                parameters like required property, and variable types
                    
            Parameters:
                Rules to be checked
                
            Returns:
                json: A json serialized response containing the body
        """
        body = body if body else await self.body()
        systemrules = ["required",  "int", "str", "float", "list", "bool","nullable",]
        checkedkeys = []

        for key, rule in rules.items():
            checkedkeys.append(key)
            indRules = rule.replace(" ", "").split(",")

            if(not body.get(key, None) and "nullable" in indRules):
                continue

            for r in indRules:
                if body.get(key, "None") == "None" :
                    return Json(
                        {
                            "data": None,
                            "message": f"{key} is required",
                            "status": SysCodes.ATTR_MISSING,
                        }
                    )

                try:
                    index = systemrules.index(r)
                    match (index):
                        case 1:
                            if not isinstance(body.get(key, None), int):
                                return Json(
                                    {
                                        "status": SysCodes.ATTR_MISSING,
                                        "data": None,
                                        "message": f"{key} must be of type int",
                                    }
                                )
                        case 2:
                            if not isinstance(body.get(key, None), str):
                                return Json(
                                    {
                                        "status": SysCodes.ATTR_MISSING,
                                        "data": None,
                                        "message": f"{key} must be of type str",
                                    }
                                )
                        case 3:
                            if not isinstance(body.get(key, None), float):
                                return Json(
                                    {
                                        "status": SysCodes.ATTR_MISSING,
                                        "data": None,
                                        "message": f"{key} must be of type float",
                                    }
                                )
                        case 4:
                            if not isinstance(body.get(key, None), list):
                                return Json(
                                    {
                                        "status": SysCodes.ATTR_MISSING,
                                        "data": None,
                                        "message": f"{key} must be of type list",
                                    }
                                )
                        case 5:
                            if not isinstance(body.get(key, None), bool):
                                return Json(
                                    {
                                        "status": SysCodes.ATTR_MISSING,
                                        "data": None,
                                        "message": f"{key} must be of type bool",
                                    }
                                )
                except Exception as e:
                    return Json(
                        {
                            "status": SysCodes.ATTR_MISSING,
                            "data": None,
                            "message": f"{r} request rule not applicable",
                            "trace": f'An error occurred - {e}',
                        }
                    )

        # make sure you return only what is required by the rules
        result = {}
        for key in checkedkeys:
            value = body.get(key, "None")
            if value != "None":
                result[key] = value

        return Json(
                        {
                            "status": SysCodes.ATTR_FOUND,
                            "data": result,
                            "message": SysMessages.ATTR_FOUND
                        }
                    )

    def server(self):
        """Return the ASGI server host and port for this request."""
        server = self.scope["server"]
        return Json({"host": server[0], "port": server[1]})

    def http(self):
        """Return the HTTP version used by the client."""
        return self.scope["http_version"]

    def scheme(self):
        """Return the request scheme."""
        return self.scope["scheme"]

    def type(self):
        """Return the ASGI connection type."""
        return self.scope["type"]

    def asgi(self):
        """Return the ASGI version and server specification details."""
        return Json(self.scope["asgi"])


    def entryTime(self):
        """Return the timestamp when the request object was accessed."""
        return datetime.now()

    def client(self):
        """Return the client's host and port information."""
        client = self.scope["client"]
        return Json({"host": client[0], "port": client[1]})

    def method(self):
        """Return the HTTP method of the request."""
        return self.scope["method"]

    def path(self):
        """Return the request path."""
        return self.scope["path"]

    def auth(self):
        """Parse the Authorization header and return type and value."""
        try:
            headerAuth = self.headers().authorization
            listAuth = headerAuth.split(" ", 1) if headerAuth is not None else ""
            return Json(
                {
                    "type": None if len(listAuth) != 2 else listAuth[0],
                    "value": None if len(listAuth) != 2 else listAuth[1],
                
                })
        except Exception as e:
            return Json({"type": None ,"value": None})

    def headers(self):
        """Return decoded request headers as a Json object."""
        heads = self.scope["headers"]
        result = Json({})

        for key, value in heads:
            result[key.decode("utf-8")] = value.decode("utf-8")
        return result

    def pathParam(self):
        """Return the stored path parameters."""
        return self._pt

    def queryParam(self):
        """Decode and return query parameters from the request."""
        string = self.scope["query_string"].decode("utf-8")

        # split by &
        queryParam = {
            key: value[0] if len(value) == 1 else value
            for key, value in parse_qs(string).items()
        }
        return Json(queryParam)

    def params(self):
        """Alias for `queryParam` that returns query parameters."""
        string = self.scope["query_string"].decode("utf-8")
        queryParam = {
            key: value[0] if len(value) == 1 else value
            for key, value in parse_qs(string).items()
        }
        return Json(queryParam)

    async def body(self, raw=False):
        """Fetch and parse the request body from ASGI receive.

        Args:
            raw (bool): when True, return the raw body payload instead of Json.
        """
        if self._body:
            return self._body

        body = b""
        more_body = True

        while more_body:
            message = await self.receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        try:
            content = self.headers().get("content-type")

            if not content:
                return Json({})

            # Handle JSON
            if "json" in content:
                body = body.decode("utf-8")
                return body if raw else Json(json.loads(body))

            # Handle multipart
            if "multipart" in content:
                parser = FileParser()
                multipart = await parser.parseMultipart(body, content)
                result = await parser.getMultipartKeys(multipart)
                return result if raw else Json(result)

            # Unsupported content type
            return Json({})

        except Exception:
            return Json({})