from dreema.helpers import Json
from dreema.responses import SysCodes, SysMessages
from bson import ObjectId

"""
    
    Use: 
        Query Builder compiles all database queries into a structure
        and secured form to be executed by the queries class
"""


class QueryBuilder:
    def __init__(self, table: str) -> None:
        """
        initializes class parameters to be used for further processing
        """
        self.table = table
        self.validOps = [
            ">",
            "=",
            "!=",
            "<",
            "<=",
            ">=",
            "in",
            "nin",
        ]
        self.validOpsMap = {
            ">": "$gt",
            "=": "$eq",
            "!=": "$ne",
            "<": "$lt",
            "<=": "$lte",
            ">=": "$gte",
            "in": "$in",
            "nin": "$nin",
        }
        self.booleans = [
            "OR",
            "AND",
        ]
        self.booleanMap = {"OR": "$or", "AND": "$and"}
 
  
    def readQueryBuilder(self, filters=None, params=None):
        """
        This builder sets the filters in the right format
        to be parsed for read database operation
        Same builder is employed delete and update since they both require some reading

        Parameters:
                dict (filters): Takes the query filters passed from the controller
                dict (params): Extra parameters added

        Returns:
            json (dict): a json serialized result containing message, status, data, trace

        """

        self.query = {}

        # process your filters
        try:
            if filters is not None and filters:
                op = self.booleanMap.get(('and' if not params else params.get('bool','and')).upper())
                self.query = {op: []}
                for key, val in filters.items():

                    column, operator, value, logic = key, "=", None, "AND"
                    value = val.get("value", None) if isinstance(val, dict) else val
                    operator = val.get("op", "=") if isinstance(val, dict) else "="
                    logic = (
                        val.get("bool", "and").upper()
                        if isinstance(val, dict)
                        else "AND"
                    )

                    # validate the columns, operator (reject if operator OR logic invalid)
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

                    # Block MongoDB operator injection via key names (e.g. $where, a.$gt)
                    if key.startswith("$") or any(p.startswith("$") for p in key.split(".")):
                        return Json(
                            {
                                "data": None,
                                "status": SysCodes.READ_FAILED,
                                "message": SysMessages.READ_FAILED,
                                "trace": "Field name not allowed",
                            }
                        )

                    # Handling _id conversion to ObjectId
                    if key == "_id":
                        try:
                            if isinstance(value, ObjectId):
                                pass  # keep as-is
                            elif isinstance(value, str):
                                value = ObjectId(value)
                            elif isinstance(value, list):
                                converted = []
                                for v in value:
                                    if isinstance(v, ObjectId):
                                        converted.append(v)
                                    elif isinstance(v, str):
                                        converted.append(ObjectId(v))
                                    else:
                                        return Json(
                                            {
                                                "data": None,
                                                "status": SysCodes.READ_FAILED,
                                                "message": SysMessages.READ_FAILED,
                                                "trace": "_id list items must be string or ObjectId",
                                            }
                                        )
                                value = converted
                            else:
                                return Json(
                                    {
                                        "data": None,
                                        "status": SysCodes.READ_FAILED,
                                        "message": SysMessages.READ_FAILED,
                                        "trace": "_id must be string, ObjectId, or list of string/ObjectId",
                                    }
                                )
                        except Exception:
                            return Json(
                                {
                                    "data": None,
                                    "status": SysCodes.READ_FAILED,
                                    "message": SysMessages.READ_FAILED,
                                    "trace": "Could not convert _id to ObjectId",
                                }
                            )

                    operator = self.validOpsMap.get(operator)
                    if operator is None:
                        return Json(
                            {
                                "data": None,
                                "status": SysCodes.READ_FAILED,
                                "message": SysMessages.READ_FAILED,
                                "trace": "Operator not accepted",
                            }
                        )
                    #CREATE: Read boolean logic. logic = self.booleanMap.get(logic)
                    condition = {column: {operator: value}}

                    # Handle grouping based on the boolean
                    self.query[op].append(condition)

            # Build result with query + read options (limit, sort, skip, projection) for Queries layer
            builder = {"query": self.query}
            if params:
                builder["limit"] = params.get("limit", 1)
                builder["sort"]  = (-1 if params.get("sort", -1) <= 0 else 1)
                builder["skip"]  = params.get("skip", 0)
                builder["sortfield"] = params.get("sortfield", "_id")
                builder['columns'] = {}
                if params.get("include", None):
                    builder["columns"].update({v:1 for v in params["include"]})
                if params.get('exclude', None):
                    builder["columns"].update({v:0 for v in params["exclude"]})
            else:
                builder["limit"] = 1
                builder["sort"]  = -1
                builder["skip"]  = 0
                builder["sortfield"] = "_id"
                builder['columns'] = {}
                
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

    def createQueryBuilder(self, data, params=None):
        """
        This builder is used to build the filters to be parsed for creating into mongodb

        Parameters:
                dict (data): The data to be inserted
                dict (params): Extra parameters added

        Returns:
            json (dict): a json serialized result containing message, status, data, trace
        """
        try:
            self.query = data
            return Json(
                {
                    "data": {"query": self.query},
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
