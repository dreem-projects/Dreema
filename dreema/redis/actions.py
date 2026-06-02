"""Redis async helper for Dreema.

This module provides a lightweight wrapper around redis-py asyncio
with JSON serialization support and a shared singleton client.
"""

from datetime import datetime
import json
import operator
from helpers.configurations import getenv
from responses import SysCodes, SysMessages
from helpers import Json
import redis.asyncio as redis

class Redis:
    """Wrapper for Redis async operations with JSON-friendly responses."""

    _instance = None
    OPS = {
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
            "==": operator.eq,
            "!=": operator.ne
        } 

    def __init__(self, client=None):
        """Initialize the Redis wrapper and ensure the client is connected."""
        self.connect()

    def connect(self):
        """Create or reuse a singleton Redis client and wrap it in a Json response."""
        if not Redis._instance:
                Redis._instance = redis.Redis(
                    host=getenv("REDIS_HOST") or "localhost",
                    port=int(getenv("REDIS_PORT") or "6379"),
                    password=getenv("REDIS_PASSWORD") or "",
                    decode_responses=True
                )

        self.client = Json({
            'data': Redis._instance,
            'message': SysMessages.REDIS_SETUP_SUCCESS,
            'status': SysCodes.REDIS_SETUP_SUCCESS
        })
        return self.client

    async def disconnect(self):
        """Close the current Redis client if available."""
        if self.client.status < 0:
            return Json({'data':None, 'message':f'{SysMessages.OP_FAILED} - Could not get client', 'status':SysCodes.REDIS_READ_FAILED})
        try:
            await self.client.data.close()
            return Json({'data':None, 'message':f'{SysMessages.REDIS_SETUP_SUCCESS}', 'status':SysCodes.REDIS_SETUP_SUCCESS})
        except Exception as e:
            return Json({'data':None, 'message':f'{SysMessages.REDIS_SETUP_FAILED} - {e}', 'status':SysCodes.REDIS_SETUP_FAILED})
        
    async def internalUpdate(self, key, model):
        """Refresh the cached Redis entry by reading the model and setting the key."""
        res = await model.read(params={'limit':0})
        value = res.data
        res = await self.set(key,value)
        return res

    async def deleteKey(self, key):
        """Delete a Redis key and return a standardized result."""
        if self.client.status < 0:
            return Json({'data':None, 'message':f'{SysMessages.REDIS_READ_FAILED} - Could not get client', 'status':SysCodes.REDIS_READ_FAILED})
        
        try:
            res = await self.client.data.delete(key)
            if res is None:
                return Json({'data':None, 'message':f'{SysMessages.REDIS_KEY_NOT_FOUND}', 'status':SysCodes.REDIS_KEY_NOT_FOUND})
            
            # res = json.load(res)
            return Json({'data':res, 'message':f'{SysMessages.OP_COMPLETED}', 'status':SysCodes.OP_COMPLETED})
        except Exception as e:
            return Json({'data':None, 'message':f'{SysMessages.OP_FAILED} - {e}', 'status':SysCodes.OP_FAILED})

    async def internalRead(self, key):
        """Read a Redis key and deserialize the value into Python data."""
        if self.client.status < 0:
            return Json({
                'data': None,
                'message': f'{SysMessages.REDIS_READ_FAILED} - Could not get client',
                'status': SysCodes.REDIS_READ_FAILED
            })
        
        try:
            r = self.client.data  # actual redis client
            ktype = await r.type(key)  # check what kind of value this key holds

            # handle if key does not exist
            if ktype == "none":
                return Json({
                    'data': None,
                    'message': f'{SysMessages.REDIS_KEY_NOT_FOUND}',
                    'status': SysCodes.REDIS_KEY_NOT_FOUND
                })

            # handle lists
            elif ktype == "list":
                items = await r.lrange(key, 0, -1)
                # try to decode JSON items
                try:
                    data = [json.loads(i) for i in items]
                except Exception:
                    data = items
                return Json({
                    'data': data,
                    'message': f'{SysMessages.REDIS_READ_SUCCESS} (list)',
                    'status': SysCodes.REDIS_READ_SUCCESS
                })

            # handle simple strings
            elif ktype == "string":
                res = await r.get(key)
                try:
                    data = json.loads(res)
                except Exception:
                    data = res
                return Json({
                    'data': data,
                    'message': f'{SysMessages.REDIS_READ_SUCCESS} (string)',
                    'status': SysCodes.REDIS_READ_SUCCESS
                })

            # handle other types (optional)
            else:
                return Json({
                    'data': None,
                    'message': f'{SysMessages.REDIS_READ_FAILED} - Unsupported Redis type: {ktype}',
                    'status': SysCodes.REDIS_READ_FAILED
                })

        except Exception as e:
            return Json({
                'data': None,
                'message': f'{SysMessages.REDIS_READ_FAILED} - {e}',
                'status': SysCodes.REDIS_READ_FAILED
            })

        
            
    async def append(self, key, value):
        """Append a value to a Redis list, serializing non-string values."""
        if not isinstance(value, str):
            value = json.dumps(value)
        
        if self.client.status < 0:
            return Json({'data':None, 'message':f'{SysMessages.REDIS_CREATE_FAILED} - Could not get client', 'status':SysCodes.REDIS_CREATE_FAILED})
        try:
            r = self.client.data  # real redis client
            
            # make sure key type is list or nonexistent
            ktype = await r.type(key)
            if ktype == "string":
                await r.delete(key)  # clear out any wrong type
            elif ktype not in ["list", "none"]:
                await r.delete(key)

            # append record to the one list
            await r.rpush(key, value)

            return Json({
                'data': None,
                'message': f'{SysMessages.REDIS_CREATE_SUCCESS}',
                'status': SysCodes.REDIS_CREATE_SUCCESS
            })

        except Exception as e:
            return Json({
                'data': None,
                'message': f'{SysMessages.REDIS_CREATE_FAILED} - {e}',
                'status': SysCodes.REDIS_CREATE_FAILED
            })
     
    async def set(self, key, value,expiry=0):
        """Set a Redis key with optional expiry, serializing non-string values."""
        if not isinstance(value, str):
            value = json.dumps(value)
        
        if self.client.status < 0:
            return Json({'data':None, 'message':f'{SysMessages.REDIS_CREATE_FAILED} - Could not get client', 'status':SysCodes.REDIS_CREATE_FAILED})
        
        try:
            if expiry > 0:
                await self.client.data.set(key, value, ex=expiry)
            else:
                await self.client.data.set(key, value)
            return Json({'data':None, 'message':f'{SysMessages.REDIS_CREATE_SUCCESS}', 'status':SysCodes.REDIS_CREATE_SUCCESS})
        except Exception as e:
            return Json({'data':None, 'message':f'{SysMessages.REDIS_CREATE_FAILED} - {e}', 'status':SysCodes.REDIS_CREATE_FAILED})

    async def create(self, key, model, data, expiry=0):
        """Create model data and refresh the corresponding Redis cache entry."""
        
        # add the time created to it
        if(isinstance(data, list)):
            for index,_ in enumerate(data):
                if data[index].get('flag', "-_") == "-_":
                    data[index]['flag'] =  1
                data[index]['dateCreated'] = int(datetime.now().timestamp())
        
        if(isinstance(data, dict)):
            if data.get('flag', "-_") == "-_":
                data['flag'] =  1
            data['dateCreated'] =  int(datetime.now().timestamp())
        
        # use model to create and quickly update
        res = await model.create(data=data)

        if res.status < 0:
            return res
        
        # update the redis
        await self.internalUpdate(key, model)
        return res
    
    async def update(self, key, model, data,  filters:dict=None, params:dict=None):
        """Update model data, refresh the cache, and return the operation result."""
        if(isinstance(data, object)):
            data['lastUpdated'] =  int(datetime.now().timestamp())

         # use model to create and quickly update
        res = await model.update(filters, data, params=params)

        if res.status < 0:
            return res
        
        # update the redis
        await self.internalUpdate(key, model)
        return res
    
    async def delete(self, key, model, filters:dict=None, params:dict=None):
        """Delete model data and refresh the Redis cache."""
         # use model to create and quickly update
        res = await model.delete(filters, params=params)

        if res.status < 0:
            return res
        
        # update the redis
        await self.internalUpdate(key, model)
        return res
       
    async def read(self, key:str="", filters:dict=None, params:dict=None, model=None, modelFirst=False):
        """Read from the underlying model. Redis caching is handled elsewhere."""
        
        res = await model.read(filters=filters, params=params)
        return res
        
    def nestedValues(self,obj, key):
        """Resolve a nested dictionary value using a dot-separated key path."""
        keys = key.split(".")
        for key in keys:
            if isinstance(obj, dict):
                obj = obj.get(key)
            else:
                return None
        return obj