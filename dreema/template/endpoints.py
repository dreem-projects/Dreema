"""
        Dreema Application Entry Routes
        This file defines the root routing table for the application.
"""

from dreema.routing import route, routegroup
from controllers.sampleController import SampleController
 

async def create():
    return {
        'data': "Some message",
        "message": "Success",
        "status": 200
    }

routes = [
        # creating single routes
        route(path="/", methods=["GET", "POST"], handler=SampleController.welcome),
        route(path="/sample-create", methods=["POST"], handler=create),
        route(path="/sample-read", methods=["GET"], handler=None),
        route(path="/sample-update", methods=["POST"], handler=None),
        route(path="/sample-delete", methods=["DELETE"], handler=None),
]
