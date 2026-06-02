"""Terminal scaffolding helpers for Dreema.

This module provides CLI-style helpers to generate basic skeleton
files for models, controllers, and views.
"""


class Model:
    """Create model file templates for Dreema applications."""
    def template(self, classname):
        return f"""from dreema.orm import database

class {classname}(database.Database):
    tablename = '{classname.lower()}'

    # system uses default connection type if not specified
    def __init__(self, connection="default"):
        super().__init__(type)
        self.setTable(self.tablename)
        """

    def create(self, classname, filename):
        # sanitize the classname
        if not isinstance(classname, str):
            print(
                "Error: In future updates, we will consider adding multiple file creations"
            )
            return

        with open(f"models/{filename}.py", "w") as f:
            f.write(self.template(classname))
            f.close()

        print(f"Done: model with name {classname} created")


class Controller:
    def template(self, classname):
        return f"""from dreema.requests import Request
from dreema.responses import response
from dreema.responses import SysCodes, SysMessages

class {classname}:
    async def sample(request: Request):
        # sample how to get and validate request body 
        body = await request.applyRules({{'name':'required,name'}})
        
        # sample response
        return response(data=body, status=SysCodes.OP_COMPLETED, message=SysMessages.OP_COMPLETED)
        """

    def create(self, classname, filename):
        # sanitize the classname
        if not isinstance(classname, str):
            print(
                "Error: In future updates, we will consider adding multiple file creations"
            )
            return

        with open(f"controllers/{filename}.py", "w") as f:
            f.write(self.template(classname))
            f.close()

        print(f"Done: Controller with name {classname} created")


class View:
    def template(self, classname):
        return f"""from dreema.routing import route,routegroup
from controllers import sampleController

class {classname}:
    route = [
        route(path="/sample", methods=['POST','GET'], handler=sampleController.UsersAuth.welcome),
    ]
        """

    def create(self, classname, filename):
        # sanitize the classname
        if not isinstance(classname, str):
            print(
                "Error: In future updates, we will consider adding multiple file creations"
            )
            return

        with open(f"views/{filename}.py", "w") as f:
            f.write(self.template(classname))
            f.close()

        print(f"Done: View with name {classname} created")
