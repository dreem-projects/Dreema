"""Terminal scaffolding helpers for Dreema.

This module provides CLI-style helpers to generate basic skeleton
files for models, controllers, and views.
"""
# Force logging initialization before anything else
import os
import subprocess
import shutil
from pathlib import Path
import argparse
import uvicorn
from dreema.helpers import settings
import socket, sys


class RunHandler:
    def __init__(self, parser:object):
        
        # make sure path is valid and endpoint.py exists
        definedPath = '.'
        if len(parser.args) > 0:
            definedPath = parser.args[0]
        elif parser.kwargs.get('path', None):
            definedPath = parser.kwargs.get('path', None)
        
        path = os.path.abspath(definedPath)

        # check for endpoint.py in views of the path
        if not os.path.exists(os.path.join(path, 'views', 'endpoints.py')):
            print("Error: Folder structure not defined for dreema")
            return
        
        os.environ['DREEMA_APP_PATH'] = path

        # get the command to perform
        self.params = {
            "port": parser.kwargs.get('port', 8888),
            "host": parser.kwargs.get('host', '127.0.0.1'),
            "reload": parser.kwargs.get('reload', True),
            "logLevel": parser.kwargs.get('log_level', 'info'),
            "workers": parser.kwargs.get('workers', 1),
        }
        self.run()
    

    def findAvailablePort(self,userPort=8888, retries=10):
        port = userPort
        for _ in range(retries):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("0.0.0.0", port))
                    return port
                except OSError:
                    port += 1
        raise RuntimeError("No available ports found")

    
    def run(self):
        try:
            port = self.findAvailablePort(int(self.params['port']))
            
            if port != self.params['port']:
                print(f"❌ Port {self.params['port']} is already in use")

                res = input(f"👉 Enter 'y' to run with the next available port - {port} : ")
                if res not in ['y', 'Y']:
                    sys.exit(1)
            
            uvicorn.run(
                "index:app",
                port=port,
                host=self.params['host'],
                workers=int(self.params['workers']),
                reload= False if str(settings("environment")) == 'live' else True,
                log_level=self.params["logLevel"],
            )

        except Exception as e:
            print("Error starting the server: ", e)
            sys.exit(1)


class CreateHandler:
    def __init__(self, parser:object):
        # get the command to perform
        commands = parser.command.split('-')[1:]
        allowedCmd = ["model", "controller", "view", 'project']

        # validate the command
        if commands[0] not in allowedCmd:
            print(f'Erorr: Action {parser.command} not defined')
            return 
        
        if len(parser.args) == 0:
            print(f'Error: This action requires values. Non provided')
            return
        

        # handle MVC scalfoldding
        for cmd in commands:
            if cmd in ['model', 'controller', 'view']:
                # use classnames and names. if names not passed use classnames with lowered first letter
                if len(parser.kwargs.get('name', [])) != 0 and len(parser.args) != len(parser.kwargs.get('name', [])):
                    print('Error: Unmatch between classes and names provided')
                    return
                
                # if the parser is zero, change the classes to names by lowering the first letter
                if len(parser.kwargs.get('name', [])) == 0:
                    parser.kwargs['name'] = []
                    for classname in parser.args:
                        parser.kwargs['name'].append(classname[0].lower() + classname[1:])
                
                # create objects now
                match cmd:
                    case 'model':
                        self.Model().create(parser.args, parser.kwargs.get('name', []))
                    case 'controller':
                        self.Controller().create(parser.args, parser.kwargs.get('name', []))
                    case 'view':
                        self.View().create(parser.args, parser.kwargs.get('name', []))  

        #   creating a project
        if cmd == 'project':
            self.Project().create(parser.args[0])


    class Project:
        def __init__(self,):
            pass

        def create(self, name):
            # 1. Path to your template inside the installed package
            template_dir = Path(__file__).parent.parent / "template" 
            destination = Path.cwd() / name
            
            # 2. Copy the files
            shutil.copytree(template_dir, destination)
            
            # 3. Initialize Git in the new project
            subprocess.run(["git", "init"], cwd=destination)
            
            print(f"✅ : New Project '{name}' created and Git initialized!")


    class Model:
        """Create model file templates for Dreema applications."""
        def template(self, cls):
            return f"""from dreema.orm import database

class {cls}(database.Database):
    tablename = '{cls.lower()}'

    # system uses default connection type if not specified
    def __init__(self, connection="default"):
        super().__init__(type, connection)
        self.setTable(self.tablename)
            """

        def create(self, cls:list, filename:list):
            # 
           # create models folder if it doesn't exist
            os.makedirs("models", exist_ok=True)

            for i in range(len(cls)):
                with open(f"models/{filename[i]}.py", "w") as f:
                    f.write(self.template(cls[i]))

            print(f"✅ Model{'s' if len(cls) > 1 else ''} created")

    class Controller:
        def template(self, cls):
            return f"""from dreema.requests import Request
from dreema.responses import response
from dreema.responses import SysCodes, SysMessages

class {cls}:
    async def sample(request: Request):
        # sample how to get and validate request body 
        body = await request.body()
        
        # sample response
        return response(data=body, status=SysCodes.OP_COMPLETED, message=SysMessages.OP_COMPLETED)
            """

        def create(self, cls:list, filename:list):
            os.makedirs("controllers", exist_ok=True)
            for i in range(len(cls)):
                with open(f"controllers/{filename[i]}.py", "w") as f:
                    f.write(self.template(cls[i]))
                    f.close()

            print(f"✅ Controller{'s' if len(cls) > 1 else ''} created")

    class View:
        def template(self, cls):
            return f"""from dreema.routing import route,routegroup

class {cls}:
    route = [
        # route(path="/sample", methods=['POST','GET'], handler=sampleController.UsersAuth.welcome),
    ]
            """

        def create(self, cls:list, filename:list):
            os.makedirs("views", exist_ok=True)
            for i in range(len(cls)):
                with open(f"views/{filename[i]}.py", "w") as f:
                    f.write(self.template(cls[i]))
                    f.close()

            print(f"✅ View{'s' if len(cls) > 1 else ''} created")

