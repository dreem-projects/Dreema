"""
        Dreema Application Entry Routes
        This file defines the root routing table for the application.
"""

from dreema.routing import route
from controllers.usersController import UsersController
 

# routes can also be defined this way
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
        route.get('/welcome', UsersController.welcome),
        route.post('/create', create),

        # create grouped routes
        route.group('/users', [
            route.get('/read', UsersController.welcome),
            route.post('/create', UsersController.testRead)
        ]),

        # routes with multiple methods
        route(path="/", methods=["GET", "POST"], handler=UsersController.welcome),
]
