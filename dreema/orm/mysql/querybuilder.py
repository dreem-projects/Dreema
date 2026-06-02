"""MySQL query builder for Dreema.

This module generates parameterized SQL for safe CRUD operations on a
single table. Identifiers are validated to prevent injection.
"""

import re
from helpers.configurations import Json
from responses import SysCodes, SysMessages

# Only allow safe identifiers: letters, digits, underscore (no $, ., space, or SQL)
_safeIdentifierPattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _safeIdentifier(name: str) -> bool:
    """True if name is safe for table/column (no injection)."""
    return isinstance(name, str) and bool(_safeIdentifierPattern.match(name)) and "$" not in name


def _escapeIdentifier(name: str) -> str:
    """Escape for use in SQL; only call after _safeIdentifier check."""
    if not _safeIdentifier(name):
        raise ValueError("Invalid identifier")
    return "`" + name.replace("`", "``") + "`"


class QueryBuilder:
    def __init__(self, table: str) -> None:
        if not _safeIdentifier(table):
            raise ValueError("Invalid table name")
        self._table = table
        self.validOps = [">", "=", "!=", "<", "<=", ">=", "in", "nin"]
        self.booleans = ["OR", "AND"]
        self.booleanSql = {"OR": " OR ", "AND": " AND "}

    def _tableSql(self) -> str:
        return _escapeIdentifier(self._table)

    def _validateColumn(self, key: str) -> bool:
        if not _safeIdentifier(key):
            return False
        if key.startswith("$") or "." in key:
            return False
        return True

    def _safeLimitSkip(self, val, default: int) -> int:
        """Coerce to non-negative int."""
        try:
            n = int(val) if val is not None else default
            return max(0, n)
        except (TypeError, ValueError):
            return default

    def readQueryBuilder(self, filters=None, params=None):
        """
        Build WHERE clause and read options. Returns Json with data:
        {whereClause, queryParams, limit, sort, sortField, skip, columns}.
        """
        whereParts = []
        queryParams = []

        try:
            if filters is not None and filters:
                #READ: Boolean params joining 
                
                for key, val in filters.items():
                    if not self._validateColumn(key):
                        return Json(
                            {
                                "data": None,
                                "status": SysCodes.READ_FAILED,
                                "message": SysMessages.READ_FAILED,
                                "trace": "Field name not allowed",
                            }
                        )
                    value = val.get("value", val) if isinstance(val, dict) else val
                    operator = (val.get("op") or "=") if isinstance(val, dict) else "="
                    logic = (val.get("bool") or "and").upper() if isinstance(val, dict) else "AND"

                    if operator not in self.validOps:
                        return Json(
                            {
                                "data": None,
                                "status": SysCodes.READ_FAILED,
                                "message": SysMessages.READ_FAILED,
                                "trace": f"Operator not accepted: {operator}",
                            }
                        )
                    if logic not in self.booleans:
                        return Json(
                            {
                                "data": None,
                                "status": SysCodes.READ_FAILED,
                                "message": SysMessages.READ_FAILED,
                                "trace": f"Boolean not accepted: {logic}",
                            }
                        )

                    colSql = _escapeIdentifier(key)
                    if operator == "in":
                        if not isinstance(value, (list, tuple)):
                            value = [value]
                        placeholders = ", ".join(["%s"] * len(value))
                        whereParts.append(f" {logic} {colSql} IN ({placeholders}) ")
                        queryParams.extend(value)
                    elif operator == "nin":
                        if not isinstance(value, (list, tuple)):
                            value = [value]
                        placeholders = ", ".join(["%s"] * len(value))
                        whereParts.append(f" {logic} {colSql} NOT IN ({placeholders}) ")
                        queryParams.extend(value)
                    else:
                        whereParts.append(f" {logic} {colSql} {operator} %s ")
                        queryParams.append(value)

                whereClause = "".join(whereParts).strip()
                if whereClause.startswith("AND "):
                    whereClause = whereClause[4:]
                if whereClause.startswith("OR "):
                    whereClause = whereClause[3:]
                whereClause = "WHERE " + whereClause if whereClause else ""
            else:
                whereClause = ""
                queryParams = []

            limit = self._safeLimitSkip(params.get("limit") if params else None, 1)
            skip = self._safeLimitSkip(params.get("skip") if params else None, 0)
            sortVal = params.get("sort", -1) if params else -1
            sort = -1 if (sortVal is None or int(sortVal) <= 0) else 1
            sortField = (params.get("sortfield") or "id") if params else "id"
            if not self._validateColumn(sortField):
                sortField = "id"
            columns = params.get("include") if params else None
            if columns is not None:
                if not isinstance(columns, (list, tuple)):
                    columns = None
                else:
                    columns = [c for c in columns if self._validateColumn(str(c))] or None

            builder = {
                "whereClause": whereClause,
                "queryParams": tuple(queryParams),
                "limit": limit,
                "sort": sort,
                "sortField": sortField,
                "skip": skip,
                "columns": columns,
            }
            return Json(
                {
                    "data": builder,
                    "status": SysCodes.READ_SUCCESS,
                    "message": SysMessages.READ_SUCCESS,
                }
            )
        except Exception as e:
            return Json(
                {
                    "data": None,
                    "status": SysCodes.READ_FAILED,
                    "message": SysMessages.READ_FAILED,
                    "trace": f"{type(e).__name__}: {e}",
                }
            )

    def buildReadQuery(self, filters=None, params=None):
        """Return full SELECT query + params. Queries layer only executes. limit=0 means fetch all."""
        result = self.readQueryBuilder(filters=filters, params=params)
        if result.status < 0:
            return result
        b = result.data
        colsSql = "*"
        if b["columns"]:
            colsSql = ", ".join(_escapeIdentifier(c) for c in b["columns"])
        order = "DESC" if b["sort"] == -1 else "ASC"
        sortSql = _escapeIdentifier(b["sortField"])
        limit = self._safeLimitSkip(b["limit"], 1)
        skip = self._safeLimitSkip(b["skip"], 0)
        # MySQL LIMIT 0 returns no rows; treat limit=0 as "no limit" (fetch everything)
        if limit == 0:
            if skip == 0:
                query = (
                    f"SELECT {colsSql} FROM {self._tableSql()} {b['whereClause']} "
                    f"ORDER BY {sortSql} {order}"
                )
            else:
                query = (
                    f"SELECT {colsSql} FROM {self._tableSql()} {b['whereClause']} "
                    f"ORDER BY {sortSql} {order} LIMIT 18446744073709551615 OFFSET {skip}"
                )
        else:
            query = (
                f"SELECT {colsSql} FROM {self._tableSql()} {b['whereClause']} "
                f"ORDER BY {sortSql} {order} LIMIT {limit} OFFSET {skip}"
            )
        return Json(
            {
                "data": {"query": query, "queryParams": b["queryParams"], "limit": limit},
                "status": SysCodes.READ_SUCCESS,
                "message": SysMessages.READ_SUCCESS,
            }
        )

    def buildDeleteQuery(self, filters=None, params=None):
        """Return full DELETE query + params. Queries layer only executes."""
        result = self.readQueryBuilder(filters=filters, params=params)
        if result.status < 0:
            result.message = SysMessages.DELETE_FAILED
            return result
        b = result.data
        limit = self._safeLimitSkip(b["limit"], 1)
        query = f"DELETE FROM {self._tableSql()} {b['whereClause']}"
        if limit != 0:
            query += f" LIMIT {limit}"
        return Json(
            {
                "data": {"query": query, "queryParams": b["queryParams"]},
                "status": SysCodes.DELETE_SUCCESS,
                "message": SysMessages.DELETE_SUCCESS,
            }
        )

    def buildCountQuery(self, filters=None, params=None):
        """Return full COUNT query + params. Queries layer only executes."""
        result = self.readQueryBuilder(filters=filters, params=params)
        if result.status < 0:
            result.message = SysMessages.READ_FAILED
            return result
        b = result.data
        query = f"SELECT COUNT(*) FROM {self._tableSql()} {b['whereClause']}"
        return Json(
            {
                "data": {"query": query, "queryParams": b["queryParams"]},
                "status": SysCodes.READ_SUCCESS,
                "message": SysMessages.READ_SUCCESS,
            }
        )

    def createQueryBuilder(self, data, params=None):
        """Build INSERT query. All identifiers validated."""
        try:
            if isinstance(data, dict):
                cols = list(data.keys())
                for c in cols:
                    if not self._validateColumn(c):
                        return Json(
                            {
                                "data": None,
                                "status": SysCodes.CREATE_FAILED,
                                "message": SysMessages.CREATE_FAILED,
                                "trace": "Column name not allowed",
                            }
                        )
                placeholders = ", ".join(["%s"] * len(cols))
                columnsSql = ", ".join(_escapeIdentifier(c) for c in cols)
                query = f"INSERT INTO {self._tableSql()} ({columnsSql}) VALUES ({placeholders})"
                queryParams = tuple(data.values())
                return Json(
                    {
                        "data": {"query": query, "queryParams": queryParams},
                        "status": SysCodes.CREATE_SUCCESS,
                        "message": SysMessages.CREATE_SUCCESS,
                    }
                )
            if isinstance(data, list) and data:
                cols = list(data[0].keys())
                for c in cols:
                    if not self._validateColumn(c):
                        return Json(
                            {
                                "data": None,
                                "status": SysCodes.CREATE_FAILED,
                                "message": SysMessages.CREATE_FAILED,
                                "trace": "Column name not allowed",
                            }
                        )
                columnsSql = ", ".join(_escapeIdentifier(c) for c in cols)
                placeholders = ", ".join(["%s"] * len(cols))
                rows = [tuple(one[c] for c in cols) for one in data]
                query = f"INSERT INTO {self._tableSql()} ({columnsSql}) VALUES "
                query += ", ".join([f"({placeholders})"] * len(rows))
                flatParams = []
                for row in rows:
                    flatParams.extend(row)
                return Json(
                    {
                        "data": {"query": query, "queryParams": tuple(flatParams)},
                        "status": SysCodes.CREATE_SUCCESS,
                        "message": SysMessages.CREATE_SUCCESS,
                    }
                )
            return Json(
                {
                    "data": None,
                    "status": SysCodes.CREATE_FAILED,
                    "message": SysMessages.CREATE_FAILED,
                    "trace": "data must be a non-empty dict or list",
                }
            )
        except Exception as e:
            return Json(
                {
                    "data": None,
                    "status": SysCodes.CREATE_FAILED,
                    "message": SysMessages.CREATE_FAILED,
                    "trace": f"{type(e).__name__}: {e}",
                }
            )

    def updateQueryBuilder(self, filters=None, data=None, params=None):
        """Build UPDATE query. Same signature as Mongo: filters, data, params."""
        try:
            if not data or not isinstance(data, dict):
                return Json(
                    {
                        "data": None,
                        "status": SysCodes.UPDATE_FAILED,
                        "message": SysMessages.UPDATE_FAILED,
                        "trace": "data must be a dictionary",
                    }
                )
            for k in data.keys():
                if not self._validateColumn(k):
                    return Json(
                        {
                            "data": None,
                            "status": SysCodes.UPDATE_FAILED,
                            "message": SysMessages.UPDATE_FAILED,
                            "trace": "Column name not allowed",
                        }
                    )
            result = self.readQueryBuilder(filters=filters, params=params)
            if result.status < 0:
                result.message = SysMessages.UPDATE_FAILED
                return result
            b = result.data
            setParts = [f"{_escapeIdentifier(k)} = %s" for k in data.keys()]
            setParams = list(data.values()) + list(b["queryParams"])
            limit = self._safeLimitSkip(b["limit"], 1)
            query = f"UPDATE {self._tableSql()} SET " + ", ".join(setParts) + " " + b["whereClause"]
            if limit != 0:
                query += f" LIMIT {limit}"
            return Json(
                {
                    "data": {"query": query, "queryParams": tuple(setParams)},
                    "status": SysCodes.UPDATE_SUCCESS,
                    "message": SysMessages.UPDATE_SUCCESS,
                }
            )
        except Exception as e:
            return Json(
                {
                    "data": None,
                    "status": SysCodes.UPDATE_FAILED,
                    "message": SysMessages.UPDATE_FAILED,
                    "trace": f"{type(e).__name__}: {e}",
                }
            )
