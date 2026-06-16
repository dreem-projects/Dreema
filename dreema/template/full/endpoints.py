"""
        Dreema Application Entry Routes
        This file defines the root routing table for the application.
"""

from dreema.routing import route
from controllers.usersController import UsersController
 

# defining all routes coming from the controllers
routes = [
        # creating single routes
        route.get('/welcome', UsersController.welcome),

        # create grouped routes
        route.group('/users', [
            route.get('/read', UsersController.testRead),
            route.post('/create', UsersController.testCreate)
        ]),

        # routes with multiple methods
        route(path="/", methods=["GET", "POST"], handler=UsersController.welcome),
]
