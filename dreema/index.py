import os
import sys

from dreema.routing import Dispatcher
from dreema.requests import Request
from dreema.responses import Response
from dreema.responses import StatusCodes, SysCodes, SysMessages
import traceback
from dreema.context import AppContext

"""
    Use:
        Handles request and response information 
        to and fro the client
"""

# dispatch the routes
async def app(scope, receive, send):
    try:
        # lifespan phase
        scp = scope['type']
        if scp == 'lifespan':
            while True:
                message = await receive()

                if message['type'] == 'lifespan.startup':
                    print('======= Starting server =======')
                    # connect to database, cache routes, env etc
                    rootPath = os.environ.get('DREEMA_APP_PATH')
                    if rootPath not in sys.path:
                        sys.path.insert(0, rootPath)
                    try:
                        await AppContext.init() 
                    except Exception as e: 
                        print(f'==> Startup error: {e}') 
                    
                    await send({"type": "lifespan.startup.complete"})
                    
                elif message['type'] == 'lifespan.shutdown':
                    print('======= Shutting down server =======')
                    try:
                        await AppContext.shutdown()
                    except Exception as e: 
                        print(f'==> Shutdown error: {e}')
                    
                    # handle all cleanups before app shuts down 

                    await send({"type": "lifespan.shutdown.complete"})
                    return
        
        if scp == "http":
            request = Request(scope, receive, send)

            #start the redis server
            request.redisClient = None
            dispatch = Dispatcher(request)
            exec = await dispatch.dispatchRoute()

            response = Response(request,send)
            await response.response(exec)

    except Exception as e:

        response = Response(None, send)
        await response.response(
            content={
                "data": None,
                "message": SysMessages.UNKNOWN_ERROR,
                "status": SysCodes.UNKNOWN_ERROR,
                "trace": f"{e} {traceback.format_exc()}",
                "statuscode": StatusCodes.FORBIDDEN,
            }
        )
