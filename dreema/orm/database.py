"""ORM database gateway for Dreema.

This module routes database operations to the configured MySQL or Mongo
backend, manages shared connection caching, and provides a common CRUD
interface.
"""

from helpers import settings, getenv, Json
from orm.mongo import connection as MongoConnector
from orm.mysql import connection as MySQLConnector
from orm.mongo import queries as MongoQueries
from orm.mysql import queries as MySQLQueries
from responses import SysCodes, SysMessages
from orm.events import EventsInterface


class Database(EventsInterface):
    """Database gateway that selects and forwards operations to a backend driver."""

    _connections = {}

    def __init__(self, connection="default"):
        """Create a database gateway for the named connection."""
        self.connection = connection
        self._credentials()
        

    def _credentials(self):
        """Load credentials and database settings for the configured connection."""
        name = self.connection
        envKey = name.upper().replace("-", "_")
        self.user = getenv("DB_USER") if name == "default" else getenv(f"DB_{envKey}_USER")
        self.pwd = getenv("DB_PASSWORD") if name == "default" else getenv(f"DB_{envKey}_PASSWORD")

        dbConfig = settings("DATABASES") and settings(f"DATABASES.{name}")
        if dbConfig:
            self.type = settings(f"DATABASES.{name}.type")
            self.host = settings(f"DATABASES.{name}.host") or "localhost"
            self.port = int(settings(f"DATABASES.{name}.port", "3306"))
            self.db = settings(f"DATABASES.{name}.database")
            useTls = settings(f"DATABASES.{name}.useTls", False)
            self.tls = bool(useTls) if isinstance(useTls, bool) else (str(useTls).lower() == "true")
        else:
            if name == "default":
                self.type = getenv("DB_TYPE")
                self.host = getenv("DB_HOST", "localhost")
                self.port = int(getenv("DB_PORT", "3306"))
                self.db = getenv("DB_NAME")
                self.tls = str(getenv("DB_USE_TLS", "false")).lower() == "true"
            else:
                self.type = None
                self.host = None
                self.port = 3306
                self.db = None
                self.tls = False

    def setConnection(self, name):
        """Switch the current named connection and reload its credentials."""
        self.connection = name
        self._credentials()

    def setTable(self, tablename):
        """Store the target table/collection name for subsequent queries."""
        self.tablename = tablename

    async def connect(self):
        """Ensure the current connection is open and return its cached client."""
        cached = Database._connections.get(self.connection)
        if cached and cached.status > 0:
            return cached

        if not any([self.host, self.port, self.user, self.pwd, self.db]):
            return Json(
                {"data": None, "message": "Missing credentials", "status": SysCodes.ENV_READ_FAILED}
            )

        if self.type not in ["mysql", "mongo"]:
            return Json(
                {"data": None, "message": "Database type not supported", "status": SysCodes.OP_FAILED}
            )


        if self.type.lower() == "mysql":
            conn = MySQLConnector.Connector()
            Database._connections[self.connection] = await conn.connect(
                host=self.host, port=int(self.port), user=self.user, pwd=self.pwd, db=self.db, tls=self.tls
            )

        if self.type.lower() == "mongo":
            conn = MongoConnector.Connector()
            Database._connections[self.connection] = await conn.connect(
                host=self.host, port=int(self.port), user=self.user, pwd=self.pwd, db=self.db, tls=self.tls
            )

        return Database._connections[self.connection]

    def initDbms(self):
        """Initialize the selected DBMS query helper for the active connection."""
        conn = Database._connections.get(self.connection)
        if not conn or conn.status < 0:
            return False
        if self.type.lower() == "mysql":
            self.dbms = MySQLQueries.Queries(conn, self.tablename, self.db)
        if self.type.lower() == "mongo":
            self.dbms = MongoQueries.Queries(conn, self.tablename, self.db)
        return True

    async def disconnect(self, name=None):
        """Close the named connection and remove it from the cache."""
        key = name if name is not None else self.connection
        conn = Database._connections.get(key)
        if conn and getattr(conn, "disconnect", None):
            await conn.disconnect()
        Database._connections.pop(key, None)
        return Json({"data": None, "message": "Database connection closed", "status": SysCodes.DB_CONNECTION_SUCCESS})

    async def read(self, filters=None, params=None):
        await self.connect()
        conn = Database._connections.get(self.connection)
        if not conn or conn.status < 0:
            return conn or Json({"data": None, "message": SysMessages.DB_ATTR_MISSING if not conn else SysMessages.DB_CONNECTION_FAILED, "status": SysCodes.DB_CONNECTION_FAILED,})
        self.initDbms()
        return await self.dbms.read(filters, params)
 
    async def update(self, filters=None, data=None, params=None):
        await self.connect()
        conn = Database._connections.get(self.connection)
        if not conn or conn.status < 0:
            return conn or Json({"data": None, "message": SysMessages.DB_ATTR_MISSING if not conn else SysMessages.DB_CONNECTION_FAILED, "status": SysCodes.DB_CONNECTION_FAILED,})
        self.initDbms()
        return await self.dbms.update(filters=filters, data=data, params=params)

    async def delete(self, filters=None, params=None):
        await self.connect()
        conn = Database._connections.get(self.connection)
        if not conn or conn.status < 0:
            return conn or Json({"data": None, "message": SysMessages.DB_ATTR_MISSING if not conn else SysMessages.DB_CONNECTION_FAILED, "status": SysCodes.DB_CONNECTION_FAILED,})
        self.initDbms()
        return await self.dbms.delete(filters, params)

    async def create(self, data, params=None):
        await self.connect()
        conn = Database._connections.get(self.connection)
        if not conn or conn.status < 0:
            return conn or Json({"data": None, "message": SysMessages.DB_ATTR_MISSING if not conn else SysMessages.DB_CONNECTION_FAILED, "status": SysCodes.DB_CONNECTION_FAILED,})
        self.initDbms()
        return await self.dbms.create(data, params)

    async def count(self, filters=None, params=None):
        await self.connect()
        conn = Database._connections.get(self.connection)
        if not conn or conn.status < 0:
            return conn or Json({"data": None, "message": SysMessages.DB_ATTR_MISSING if not conn else SysMessages.DB_CONNECTION_FAILED, "status": SysCodes.DB_CONNECTION_FAILED,})
        self.initDbms()
        return await self.dbms.count(filters, params)