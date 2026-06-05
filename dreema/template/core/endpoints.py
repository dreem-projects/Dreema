"""
        Dreema Application Entry Routes
        This file defines the root routing table for the application.
"""

from dreema.routing import route   

async def create():
    return {
        'data': {
            'name': 'Kweku Dreem'
        },
        "message": "Message sent",
        "status": 20
    }


# define your route here
routes = [
        # get, post, put, delete
        route.get('/',create),
        
        # declaring multiple routes
        route.group('/users', [
            route.get('/create', create)
        ]),
]
