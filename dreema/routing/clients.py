"""Route definition helpers for Dreema."""

from dreema.helpers import Json


class Route:
    """
        Internal route descriptor.
    """

    def __init__(self, path: str, methods: list, handler):
        self.path = path
        self.methods = methods
        self.handler = handler

    def json(self):
        return Json({
            "path": self.path,
            "method": self.methods,
            "handler": self.handler,
        })


class RouteFactory:
    """
    Route builder and helper methods.
    """

    def __init__(self):
        pass

    def __call__(self, path: str, methods:list=[], handler:callable=None):
        if isinstance(methods, str):
            methods = [methods]

        return Route(path, methods, handler)

    def get(self, path: str, handler):
        return Route(path, ["GET"], handler)

    def post(self, path: str, handler):
        return Route(path, ["POST"], handler)

    def put(self, path: str, handler):
        return Route(path, ["PUT"], handler)

    def patch(self, path: str, handler):
        return Route(path, ["PATCH"], handler)

    def delete(self, path: str, handler):
        return Route(path, ["DELETE"], handler)

    def group(self, prefix: str, routes: list):
        """
        Group routes under a common prefix.
        """

        prefix = "/" + prefix.strip("/")

        grouped = []

        for r in routes:
            path = f"{prefix}/{r.path}".replace("//", "/")

            grouped.append(
                Route(
                    path=path,
                    methods=r.methods,
                    handler=r.handler,
                )
            )

        return grouped

route = RouteFactory()