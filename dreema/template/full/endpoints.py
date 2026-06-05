"""
        Dreema Application Entry Routes
        This file defines the root routing table for the application.
"""

from dreema.routing import route
from controllers.sampleController import SampleController
 

async def create():
    return {
         'data': {
            'name': 'Kweku Dreem'
        },
        "message": "Message sent",
        "status": 20
    }

# routes
routes = [
        # creating single routes
        route.get('/welcome', SampleController.welcome),
        route.post('/create', create),

        # create grouped routes
        route.group('/users', [
            route.get('/read', SampleController.welcome),
            route.post('/create', SampleController.sampleRead)
        ]),

        # routes with multiple methods
        route(path="/", methods=["GET", "POST"], handler=SampleController.welcome),
]
