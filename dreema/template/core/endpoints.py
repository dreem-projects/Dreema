"""
        Dreema Application Entry Routes
        This file defines the root routing table for the application.
"""

from dreema.routing import route   
from dreema.responses import SysCodes, response, SysMessages

async def userRead():
    {
        'data': {
            'name': 'Qweku Dreem'
        },
        "message": "Message sent",
        "status": 20
    }

async def welcome():
    # using standard response envelope
    return response(data=None, message=SysMessages.SETUP_COMPLETED, status=SysCodes.SETUP_COMPLETED)


# define your route here
routes = [
        # get, post, put, delete for single routes
        route.get('/',welcome),
        
        # grouping multiple routes
        route.group('/users', [
            route.get('/read', userRead)
        ]),
]
