"""MySQL ORM query implementation for Dreema.

This module provides async CRUD operations that use the MySQL QueryBuilder
and return consistent response wrappers.
"""

from typing import Any
from orm.events import EventsInterface
from helpers.configurations import Json, settings
from responses import SysCodes, SysMessages
from .querybuilder import QueryBuilder


class Queries(EventsInterface):
    """MySQL query handler that executes parameterized CRUD operations."""

    def __init__(self, connector: dict, table: str, db: str = None) -> None:
        self.conn = connector.data.connection
        self.table = table
        self.database = str(db or settings("databases.default.database", settings("DB_NAME", "test_mysql"))) 
        self._tableColumnsCache = None

    async def _getTableColumns(self) -> list:
        """Return list of column names for self.table (cached). Used to resolve exclude."""
        if self._tableColumnsCache is not None:
            return self._tableColumnsCache
        cursor = await self.conn.cursor()
        await cursor.execute(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s ORDER BY ORDINAL_POSITION",
            (self.table,),
        )
        rows = await cursor.fetchall()
        self._tableColumnsCache = [row[0] for row in rows] if rows else []
        return self._tableColumnsCache

    async def create(self, data, params: dict = None):
        if not isinstance(data, dict) and not isinstance(data, list):
            return Json({
                "data": None,
                "status": SysCodes.DB_CONNECTION_FAILED,
                "message": "data must be a dictionary or a list for bulk create",
            })
        try:
            builder = QueryBuilder(self.table)
            resultBuild = builder.createQueryBuilder(data=data, params=params)
            if resultBuild.status < 0:
                return resultBuild
            cursor = await self.conn.cursor()
            await cursor.execute(resultBuild.data.query, resultBuild.data.queryParams)
            await self.conn.commit()
            insertedId = cursor.lastrowid
            if isinstance(data, list) and len(data) > 1:
                insertedId = list(range(
                    cursor.lastrowid - len(data) + 1,
                    cursor.lastrowid + 1,
                ))
            return Json({
                "data": {"lastInsertedId": insertedId},
                "status": SysCodes.CREATE_SUCCESS,
                "message": SysMessages.CREATE_SUCCESS,
            })
        except Exception as e:
            return Json({
                "data": None,
                "status": SysCodes.CREATE_FAILED,
                "message": SysMessages.CREATE_FAILED,
                "trace": f"{type(e).__name__}: {e}",
            })

    async def read(self, filters: dict = None, params: dict = None):
        try:
            readParams = params
            if params and params.get("exclude"):
                excludeList = params.get("exclude")
                if isinstance(excludeList, (list, tuple)):
                    tableColumns = await self._getTableColumns()
                    includeList = params.get("include")
                    base = list(includeList) if includeList else tableColumns
                    excludeSet = set(excludeList)
                    readParams = dict(params)
                    readParams["include"] = [c for c in base if c not in excludeSet]
                    readParams.pop("exclude", None)
            builder = QueryBuilder(self.table)
            resultBuild = builder.buildReadQuery(filters=filters, params=readParams)
            if resultBuild.status < 0:
                resultBuild.message = SysMessages.READ_FAILED
                return resultBuild
            d = resultBuild.data
            cursor = await self.conn.cursor()
            await cursor.execute(d.query, d.queryParams)
            result = await cursor.fetchall()
            desc = cursor.description
            if result is None:
                return Json({
                    "data": [],
                    "status": SysCodes.NO_RECORD,
                    "message": SysMessages.NO_RECORD,
                })
            columns = [x[0] for x in desc]
            outData = [dict[Any, Any](zip(columns, row)) for row in result]
            if len(outData) == 0:
                return Json({
                    "data": outData,
                    "status": SysCodes.NO_RECORD,
                    "message": SysMessages.NO_RECORD,
                })
            out = outData[0] if (d.limit == 1 and len(outData) == 1) else outData
            return Json({
                "data": out,
                "status": SysCodes.READ_SUCCESS,
                "message": SysMessages.READ_SUCCESS,
            })
        except Exception as e:
            return Json({
                "data": None,
                "status": SysCodes.READ_FAILED,
                "message": SysMessages.READ_FAILED,
                "trace": f"{type(e).__name__}: {e}",
            })

    async def delete(self, filters, params: dict = None):
        if not isinstance(filters, dict) and (not params or params.get("limit") != 0):
            return Json({
                "data": None,
                "status": SysCodes.DB_CONNECTION_FAILED,
                "message": "delete require filters. For bulk delete, set limit to 0",
            })
        try:
            builder = QueryBuilder(self.table)
            resultBuild = builder.buildDeleteQuery(filters=filters, params=params)
            if resultBuild.status < 0:
                return resultBuild
            d = resultBuild.data
            cursor = await self.conn.cursor()
            await cursor.execute(d.query, d.queryParams)
            await self.conn.commit()
            return Json({
                "data": None,
                "status": SysCodes.DELETE_SUCCESS,
                "message": SysMessages.DELETE_SUCCESS,
            })
        except Exception as e:
            return Json({
                "data": None,
                "status": SysCodes.DELETE_FAILED,
                "message": SysMessages.DELETE_FAILED,
                "trace": f"{type(e).__name__}: {e}",
            })

    async def update(self, filters=None, data=None, params: dict = None):
        if not isinstance(data, dict):
            return Json({
                "data": None,
                "status": SysCodes.DB_CONNECTION_FAILED,
                "message": "data and filter must be a dictionary",
            })
        try:
            builder = QueryBuilder(self.table)
            resultBuild = builder.updateQueryBuilder(filters=filters, data=data, params=params)
            if resultBuild.status < 0:
                return resultBuild
            d = resultBuild.data
            cursor = await self.conn.cursor()
            await cursor.execute(d.query, d.queryParams)
            await self.conn.commit()
            return Json({
                "data": None,
                "status": SysCodes.UPDATE_SUCCESS,
                "message": SysMessages.UPDATE_SUCCESS,
            })
        except Exception as e:
            return Json({
                "data": None,
                "status": SysCodes.UPDATE_FAILED,
                "message": SysMessages.UPDATE_FAILED,
                "trace": f"{type(e).__name__}: {e}",
            })

    async def count(self, filters: dict = None, params: dict = None):
        try:
            builder = QueryBuilder(self.table)
            resultBuild = builder.buildCountQuery(filters=filters, params=params)
            if resultBuild.status < 0:
                return resultBuild
            d = resultBuild.data
            cursor = await self.conn.cursor()
            await cursor.execute(d.query, d.queryParams)
            row = await cursor.fetchone()
            theCount = row[0] if row else 0
            return Json({
                "data": theCount,
                "status": SysCodes.READ_SUCCESS,
                "message": SysMessages.READ_SUCCESS,
            })
        except Exception as e:
            return Json({
                "data": None,
                "status": SysCodes.READ_FAILED,
                "message": SysMessages.READ_FAILED,
                "trace": f"{type(e).__name__}: {e}",
            })
