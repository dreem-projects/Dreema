"""MySQL async connection helper for Dreema."""

import aiomysql
from dreema.helpers import Json
from dreema.responses import SysCodes, SysMessages
import traceback


class Connector:
    """Connector wrapper around aiomysql for Dreema."""

    def __init__(self) -> None:
        pass

    async def connect(
        self, host: str, port: int, user: str, pwd: str, db: str, tls: bool
    ):
        """Open a MySQL connection and return a result wrapper."""
        try:
            # SQL
            conn = await aiomysql.connect(
                host=host, port=port, user=user, password=pwd, db=db
            )
            return Json(
                {
                    "data": {"connection": conn, "db": db},
                    "status": SysCodes.DB_CONNECTION_SUCCESS,
                    "message": SysMessages.DB_CONNECTION_SUCCESS,
                }
            )
        except Exception as e:
            return Json(
                {
                    "data": None,
                    "message": SysMessages.DB_CONNECTION_FAILED,
                    "status": SysCodes.DB_CONNECTION_FAILED,
                    "trace": f"{e} {traceback.format_exc()}",
                }
            )

    async def disconnect(self, conn):
        """Close the provided MySQL connection handle."""
        if conn:
            closeFn = getattr(conn, "close", None)
            if closeFn:
                try:
                    await closeFn()
                except TypeError:
                    closeFn()
            return Json(
                {
                    "data": None,
                    "message": 'Database connection closed successfully',
                    "status": SysCodes.DB_CONNECTION_SUCCESS,
                }
            )
        return Json(
            {
                "data": None,
                "message": 'Database connection not found',
                "status": SysCodes.DB_CONNECTION_FAILED,
            }
        )
