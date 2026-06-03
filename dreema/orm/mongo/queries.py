"""MongoDB ORM query implementation for Dreema.

This module provides async CRUD operations for MongoDB collections,
serializing BSON results into JSON-friendly responses.
"""

from dreema.orm.events import EventsInterface
from dreema.helpers.configurations import Json, settings
from dreema.responses import SysCodes, SysMessages
from .querybuilder import QueryBuilder
import json
from bson.json_util import dumps

# Functions:
#     This class provides access to MongoDB operations that form the core of the ORM.

class Queries(EventsInterface):
    """MongoDB query handler that executes CRUD operations via Motor."""

    def __init__(self, connector: dict, table: str, db: str = None) -> None:
        self.conn = connector.data.connection
        self.table = table
        self.database = str(db or settings("databases.default.database", settings("DB_NAME", "test_mongo"))) 

    def serialize(self, data: dict):
        """
        Because mongodb can return object types, a serializer is needed to convert json

        Parameters:
            data (dict): a non serialized dictionary normally from mongodb

        Return:
            data (dict): a serialized version of the object
        """
        serialized = dumps(data)
        return json.loads(serialized)

    async def create(self, data, params: dict = None):
        """
        This method is used to perform all create operations for mongodb

        Parameters:
            dict (data) : the data to be inserted into the database
            dict (params): extra parameters to be used

        Returns:
            json (dict): a json serialized result containing message, status, data, trace

        """

        if not isinstance(data, dict) and not isinstance(data, list):
            return Json(
                {
                    "data": None,
                    "status": SysCodes.DB_CONNECTION_FAILED,
                    "message": "data must be a dictionary or a list for bulk create",
                }
            )

        try:
            builder = QueryBuilder(self.table)
            resultBuild = builder.createQueryBuilder(data, params=params)

            if resultBuild.status < 0:
                return resultBuild

            db = self.conn[self.database]
            collection = db[self.table]

            _id = []
            if isinstance(data, list):
                result = await collection.insert_many(resultBuild.data.query)
                inserted_ids = result.inserted_ids
                _id = [self.serialize(_id)['$oid'] for _id in inserted_ids]
            else:
                result = await collection.insert_one(resultBuild.data.query)
                inserted_id = result.inserted_id
                _id = [self.serialize(inserted_id)['$oid']]

            return Json(
                {
                    "data": {"_id": _id},
                    "status": SysCodes.CREATE_SUCCESS,
                    "message": SysMessages.CREATE_SUCCESS,
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

    async def read(self, filters: dict = None, params: dict = None):
        """
        This method is used to perform all read operations for mongodb

        Parameters:
            filters (dict) : filters to be used for querying
            dict (params): extra parameters to be used

        Returns:
            json (dict): a json serialized result containing message, status, data, trace
        """
        try:
            #  build the queries
            builder = QueryBuilder(self.table)
            resultBuild = builder.readQueryBuilder(filters=filters, params=params)

            if resultBuild.status < 0:
                return resultBuild

            # params
            db = self.conn[self.database]
            collection = db[self.table]
            
            builder = resultBuild.data
            cursor =  collection.find(builder.query, builder.columns).sort(builder.sortfield, builder.sort).limit(builder.limit).skip(builder.skip)
            documents = await cursor.to_list()

            # serialize and parse back to json
            serialized = dumps(documents)
            parsedRes = json.loads(serialized)
            for item in parsedRes:
                if "_id" in item and "$oid" in item["_id"]:
                    item["_id"] = item["_id"]["$oid"] 
                    
            # apply limits
            result = parsedRes[0] if builder.limit==1 and parsedRes else parsedRes
            if len(result)==0:
                return Json(
                {
                    "data": result,
                    "status": SysCodes.NO_RECORD,
                    "message": SysMessages.NO_RECORD,
                }
            )

            return Json(
                {
                    "data": result,
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

    async def delete(self, filters, params: dict = None):
        """
        This method is used to perform all delete operations for mongodb

        Parameters:
            filters (dict) : filters to be used for querying the right object(s)
            dict (params): extra parameters to be used

        Returns:
            json (dict): a json serialized result containing message, status, data, trace
        """

        if not isinstance(filters, dict) and (not params or params.get("limit") != 0):
            return Json(
                {
                    "data": None,
                    "status": SysCodes.DB_CONNECTION_FAILED,
                    "message": "delete require filters. For bulk delete, set limit to 0",
                }
            )

        try:
            #  build the queries
            builder = QueryBuilder(self.table)
            resultBuild = builder.readQueryBuilder(filters=filters, params=params)

            if resultBuild.status < 0:
                resultBuild.message = SysMessages.DELETE_FAILED
                return resultBuild

            db = self.conn[self.database]
            collection = db[self.table]

            if params:
                if params.get("limit", None) == 0:
                    await collection.delete_many(resultBuild.data.query)
            else:
                await collection.delete_one(resultBuild.data.query)

            return Json(
                {
                    "data": None,
                    "status": SysCodes.DELETE_SUCCESS,
                    "message": SysMessages.DELETE_SUCCESS,
                }
            )

        except Exception as e:
            return Json(
                {
                    "data": None,
                    "status": SysCodes.DELETE_FAILED,
                    "message": SysMessages.DELETE_FAILED,
                    "trace": f"{type(e).__name__}: {e}",
                }
            )

    async def update(self, filters=None, data=None, params: dict = None):
        """
        This method is used to perform all update operations for mongodb

        Parameters:
            filters (dict) : filters to be used for querying the right object(s)
            data (dict): the new data to be used to replace
            params (dict): extra parameters to be used

        Returns:
            json (dict): a json serialized result containing message, status, data, trace
        """
        if not isinstance(data, dict):
            return Json(
                {
                    "data": None,
                    "status": SysCodes.DB_CONNECTION_FAILED,
                    "message": "data and filter must be a dictionary",
                }
            )

        try:
            #  build the queries
            builder = QueryBuilder(self.table)
            resultBuild = builder.readQueryBuilder(filters=filters, params=params)

            if resultBuild.status < 0:
                resultBuild.message = SysMessages.UPDATE_FAILED
                return resultBuild

            db = self.conn[self.database]
            collection = db[self.table]

            if params and params.get("limit", None) == 0:
                await collection.update_many(resultBuild.data.query, {"$set": data})
            else:
                await collection.update_one(resultBuild.data.query, {"$set": data})
            
            
            return Json(
                {
                    "data": None,
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

    async def count(self, filters: dict = None, params: dict = None):
        try:
            builder = QueryBuilder(self.table)
            resultBuild = builder.readQueryBuilder(filters=filters, params=params)

            if resultBuild.status < 0:
                resultBuild.message = SysMessages.READ_FAILED
                return resultBuild

            db = self.conn[self.database]
            collection = db[self.table]

            # Execute COUNT query
            count = await collection.count_documents(resultBuild.data.query)

            return Json(
                {
                    "data": count,
                    "status": SysCodes.READ_SUCCESS,
                    "message": SysMessages.READ_SUCCESS,
                }
            )

        except Exception as e:
            self.errorMessage = f"{type(e).__name__}: {e}"
            return Json(
                {
                    "data": None,
                    "status": SysCodes.READ_FAILED,
                    "message": self.errorMessage,
                }
            )