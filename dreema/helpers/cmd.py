"""Terminal scaffolding helpers for Dreema.

This module provides CLI-style helpers to generate basic skeleton
files for models, controllers, and views.
"""
# Force logging initialization before anything else
from datetime import datetime
import json
import os
import subprocess
import shutil
from pathlib import Path
from  dreema.config import APP
from dreema.helpers.serialization import Json
import subprocess, sys, requests


class KwargsHandler:
    def __init__(self, parser:object):
        if(parser.kwargs.get('version', None)):
            glb = APP.get("version")
            print(f'Dreema Global: {glb}')
            try:
                path = os.path.abspath('.')
                config = None
                with open(f'{path}/.dreema.json', "r") as f:
                    config = Json(json.load(f))
                
                print(f'Dreema Local : {config.version}')

                if glb != config.version:
                    print('🟡 You are outdated: run `dreema update` to update to the latest version.')
                else:
                    print('🟢 Updated version: You are all caught up')
            except Exception as e:
                print(f'🔴 .dreema.json file not found in your folder directory')
                

class CreateHandler:
    def __init__(self, parser:object):
        # get the command to perform
        commands = parser.command.split('-')[1:]
        allowedCmd = ["model", "controller", "view", 'project']

        if len(commands) == 0:
            print(f'🔴 Erorr: Action {parser.command} not defined')
            return 

        # validate the command
        if commands[0] not in allowedCmd:
            print(f'🔴 Erorr: Action {parser.command} not defined')
            return 
        
        if len(parser.args) == 0:
            print(f'🔴 Error: This action requires values. None provided')
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
            self.Project(parser).create()


    class Project:
        def __init__(self,parser:object):
            self.name = parser.args[0]
            self.mode = parser.kwargs.get('mode', 'full')

        def create(self):
            destination = Path.cwd() / (self.name if self.name != "." else "")
            exists = os.path.exists(destination)
            template = Path(__file__).parent.parent / "template"
            src = template / self.mode
            filecount = 0
            # Walk through the template directory
            for root,dir, files in os.walk(src):
                rel_path = Path(root).relative_to(src)
                dest_path = destination / rel_path
                dest_path.mkdir(parents=True, exist_ok=True)

                for file in files:
                    src_file = Path(root) / file
                    dest_file = dest_path / file

                    dest_filename = ".env" if file == "env.template" else file
                    dest_file = dest_path / dest_filename
                    
                    # Only copy if the file does NOT exist in the destination
                    if not dest_file.exists():
                        filecount += 1
                        shutil.copy2(src_file, dest_file)

            # 
            metadata = {
                "version": APP["version"],
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            
            with open(destination / ".dreema.json", "w") as f:
                json.dump(metadata, f, indent=4)

            #  initialize git only if the folder didn't exists before
            if filecount:
                print(f'🟢 {filecount} File copied')
            else:
                print('Files updated')
                
            if not exists:
                
                if self.mode == "full":
                    with open(destination / ".env", "w") as f:
                        f.write("""# can be changed in settings.py
ENVIRONMENT=local
SERVER_PORT=8000

# default db settings
DB_TYPE=mongo
DB_HOST=localhost
DB_PORT=27017
DB_NAME=
DB_USER=
DB_PASSWORD=
"""
                    )

                subprocess.run(["git", "init"], cwd=destination)
                print(f"🟢 : New Project {self.name if self.name != '.' else ''} created and Git initialized!")


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

            print(f"🟢 Model{'s' if len(cls) > 1 else ''} created")

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

            print(f"🟢 Controller{'s' if len(cls) > 1 else ''} created")

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

            print(f"🟢 View{'s' if len(cls) > 1 else ''} created")

class CommandsHandler:
    def __init__(self, parser:object):
        # get the command to perform
        command = parser.command
        allowedCmd = ["upgrade"]
        if command not in allowedCmd:
            print(f'🔴 Erorr: Action {parser.command} not defined')
            return 
        

        if command == "upgrade":
                self.upgrade()

    def pipUpdate(self):
        """
        Checks for the latest version on PyPI and performs an 
        in-place pip upgrade within the current virtual environment.
        """

        # 1. Fetch latest version
        try:
            url = f"https://pypi.org/pypi/{APP.get('name', 'dreema')}/json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            latest = response.json()["info"]["version"]
        except Exception as e:
            print(f"🔴 Failed to check for updates: {e}")
            return

        # 2. Perform the upgrade using the current interpreter
        print(f"🟡 Upgrading Dreema to version {latest}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--upgrade",  APP.get('name', 'dreema')
            ])
            print(f'🟢 {APP.get("name", "dreema")} updated to the latest version - {latest}')
        except subprocess.CalledProcessError:
            print("🔴 Error: Could not update. Check your network or permissions.")
                
    def upgrade(self):
        glb = APP.get("version")
        try:
                path = os.path.abspath('.')
                config = None
                with open(f'{path}/.dreema.json', "r") as f:
                    config = Json(json.load(f))
                

                if glb != config.version:
                    usr = config.version
                    print(f'-> Your current Dreema version: {usr}')
                    print(f'-> Upgrading to the latest version: {glb}')
                    user_v = int(usr.split('.')[0])
                    glb_v = int(glb.split('.')[0])

                    # check for when user version is greater than global version
                    if(user_v > glb_v):
                        print(f'🔴 Invalid version in .dreema.json as local version is ahead of global version')
                    else:
                        breakTrace = APP.get("templateBreakTrace")[user_v:glb_v]
                        if any(x is False for x in breakTrace):
                            print(f'🔴 Updated version v{glb} contains breaking changes of dreema.\nCheck the documentation to make the necessary migrations')
                        else:
                            self.pipUpdate()
                else:
                    print(f'🟢 Updated version: Dreema running on the latest version {glb}')
        except Exception as e:
                print(f'🔴 .dreema.json file not found in your folder director. To update dreema globally without affecting specific codebases, run `pip install --upgrade dreema `')