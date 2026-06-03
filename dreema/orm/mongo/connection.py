# connect to a database asynchronously
from dreema.helpers import Json
from dreema.responses import SysCodes, SysMessages
import traceback
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote
 
"""
    Use: Primarily to connect and dictionary from the mongodb server
"""


class Connector:
    """
    Connection credentials are injected from the database.py file in the directory above

    Parameters:
        host (str): the host url to the server
        port (int): this specifies which port the server is listening on
        user (str): the database users
        pwd (str) : the password to accessing the connection
        db (str)  : the database name to be used
        tls (bool): true/false depending on whether connection is encrypted

    Returns:
        json: On success the connection object is added onto the data
        json: On failure, information is parsed to the client
    """

    async def connect(
        self, host: str, port: int, user: str, pwd: str, db: str, tls: bool
    ):
        try:
            uri = f"mongodb://{quote(user)}:{quote(pwd)}@{host}:{port}/{db}?tls={str(tls).lower()}&authSource=admin"
            client = AsyncIOMotorClient(uri, minPoolSize=10, maxPoolSize=300, serverSelectionTimeoutMS=5000)

            # Actually verify the connection works by pinging the server
            await client.admin.command('ping')

            return Json(
                {
                    "data": {"connection": client, "db": db},
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

    async def disconnect(self, client):
        if client:
            client.close()
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