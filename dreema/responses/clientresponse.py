"""Client response helper for Dreema.

Builds consistent JSON responses for HTTP clients and supports custom
payload mode when `custom=True`.
"""

from dreema.helpers import Json, settings
from .codes import SysCodes, SysMessages


def response(
    message=SysMessages.OP_COMPLETED,
    status: int = SysCodes.OP_COMPLETED,
    data=None,
    trace=None,
    custom=False,
    statuscode: int = 200,
    headers = {}
) -> dict:
    """Build a JSON response wrapper for client delivery.

    Args:
        message: Standard message text or custom payload when custom=True.
        status: Internal Dreema status code.
        data: Standard response data payload.
        trace: Optional trace information for debugging.
        custom: If True, emit a custom response structure.
        statuscode: HTTP status code for the response.
        headers: Optional response headers.

    Returns:
        Json: A JSON serializable response container.
    """

    val = settings("customResponse")
    envCustom = val is True or (isinstance(val, str) and "true" in (val or "").lower())

    if envCustom or custom:
        return Json(
            {
                "data": message,
                "custom": True,
                "headers": headers,
                'statuscode': statuscode
            }
        )

    return Json(
        {
            "data": data,
            "message": message,
            "status": status,
            "trace": trace,
            "statuscode": statuscode,
            "headers": headers
        }
    )
