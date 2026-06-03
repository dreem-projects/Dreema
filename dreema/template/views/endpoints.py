from dreema.routing import route, routegroup
import controllers.sampleController as SampleController

"""
        author:  Raphael Djangmah
        Use:
                This file is the main view entry.
"""
routes = [
        # creating single routes
        route(path="/", methods=["GET", "POST"], handler=SampleController.welcome),
        route(path="/sample-create", methods=["POST"], handler=SampleController.sampleCreate),
        route(path="/sample-read", methods=["GET"], handler=SampleController.sampleRead),
        route(path="/sample-update", methods=["POST"], handler=SampleController.sampleUpdate),
        route(path="/sample-delete", methods=["DELETE"], handler=SampleController.sampleDelete),
]
