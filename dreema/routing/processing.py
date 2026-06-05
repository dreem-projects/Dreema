"""Routing dispatcher for Dreema.

This module matches ASGI requests against view-defined routes, applies
CORS checks, and forwards requests to the appropriate handler.
"""

from dreema.requests import Request
from dreema.responses import response
from dreema.responses import SysCodes, StatusCodes, SysMessages
from dreema.security import Encrypt
import traceback
from dreema.helpers.serialization import Json
from .cors import Cors


class Dispatcher:
    """Dispatches incoming requests to registered view routes."""
    ROUTES = None
    ROUTEMAPS = {}

    def __init__(self, request: Request = None) -> None:
        self.request = request

    @staticmethod
    def getRoute(route):
        """Normalize a route descriptor and identify dynamic path parameters."""
        route = route.json()
        path = route.path.rstrip("/").replace('//','/')
        parts = path.strip('/').split('/')
        params = {'pathParams':[], 'handler': route.handler, 'method':route.method, 'parts': [],  'id' : Encrypt.generateRandom(16,1) }

        for index,part in enumerate(parts):
            if part.startswith(":"):
                name = part[1:]
                params['pathParams'].append({
                    'name': name,
                    'position': index,
                })
                params['parts'].append(f'{part}')
            else:
                params['parts'].append(part)
        
        return path, params
    
    def matchRoute(self, routeParts, pathParts):
        """Compare route pattern parts to a real request path and extract params."""
        params = {}

        if len(routeParts) != len(pathParts):
            return False, {}

        for r, p in zip(routeParts, pathParts):
            if r.startswith(":"):
                params[r[1:]] = p
                continue

            if r != p:
                return False, {}
            
        return True, params


    @classmethod
    def initRoutes(cls, routes=[]):
        """Build and cache the route registry from configured view routes."""
        if cls.ROUTES:
            return cls.ROUTES
        
        statics = {}
        dynamics = {}
        for route in routes:
            # if it is a route group
            if isinstance(route, list):
                for r in route:
                    key, value = Dispatcher.getRoute(r)
                    if value.get('pathParams', False):
                        dynamics[key] = value
                    else: 
                        statics[key] = value
            else:
                key, value = Dispatcher.getRoute(route)
                if value.get('pathParams', False):
                    dynamics[key] = value
                else: 
                    statics[key] = value

        cls.ROUTES = {'statics': statics, 'dynamics': dynamics}
        return cls.ROUTES

    async def dispatchRoute(self):
        """Match the current request to a route, execute it, and return the response."""

        try:
            path = self.request.path().rstrip("/")
            method = self.request.method()
            pathData = path.strip('/').split('/')

            # checking for CORS
            cors = Cors(self.request)
            cors = cors.process()
            if cors.status < 0:
                return response(cors, statuscode=StatusCodes.FORBIDDEN, custom=True)

            # Initialize routes if not already done
            if not Dispatcher.ROUTES:
                Dispatcher.initRoutes()

            # search for the route
            router = Dispatcher.ROUTEMAPS[path] if path in Dispatcher.ROUTEMAPS else None
            if not router:
                _staticMatch = Dispatcher.ROUTES['statics'].get(path)
                if _staticMatch:
                    router = _staticMatch
                    Dispatcher.ROUTEMAPS[path] = _staticMatch
                else:
                    for _,details in Dispatcher.ROUTES['dynamics'].items():
                        matched, param = self.matchRoute(routeParts=details.get('parts',[]), pathParts=pathData)

                        if not matched:
                            continue

                        # cache the route that does not have path params
                        router = details
                        self.request._pt = param

            # use the maper to
            if router:
                handler = router.get('handler', None)
                if method not in router.get('method',[]):
                            return response(
                                statuscode=StatusCodes.METHOD_NOT_ALLOWED,
                                message=SysMessages.UNALLOWED_METHOD,
                                status=SysCodes.UNALLOWED_METHOD,
                            )
                
                if not callable(handler):
                    return response(
                        message=SysMessages.ENDPOINT_FUNC_FAIL,
                        status=SysCodes.ENDPOINT_FUNC_FAIL,
                        statuscode=StatusCodes.BAD_REQUEST,
                    )

                try:
                    return await handler(self.request)
                except TypeError as e:
                    return await handler()

            # Send a 404 response if no matching route is found
            return response(
                message=SysMessages.ENDPOINT_NOT_FOUND,
                status=SysCodes.ENDPOINT_NOT_FOUND,
                statuscode=StatusCodes.NOT_FOUND,
            )

        except Exception as e:
            return response(
                message=SysMessages.UNKNOWN_ERROR,
                status=SysCodes.UNKNOWN_ERROR,
                statuscode=StatusCodes.INTERNAL_SERVER_ERROR,
                trace=f"{e} {traceback.format_exc()}",
            )
