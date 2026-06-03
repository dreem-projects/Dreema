"""Route definition helpers for Dreema."""

from dreema.helpers import Json


def route(path: str, methods, handler):
    """Return a route descriptor containing path, methods, and handler."""
    return Json({"path": path, "method": methods, "handler": handler})


def routegroup(cls: list, prefix: str = "", postfix: str = ""):
    """Build a grouped route list with an optional prefix and postfix."""
    grouped = []
    for r in cls:
        try:
            grouped.append(
                Json(
                    {
                        "path": f"/{prefix}{r.path}/{postfix}",
                        "method": r.method,
                        "handler": r.handler,
                    }
                )
            )
        except Exception:
            continue

    return grouped
