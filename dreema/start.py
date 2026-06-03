import os
from pathlib import Path
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
        if not os.path.exists(os.path.join(path,'views', 'endpoints.py')):
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
               f"dreema.index:app",
                port=port,
                host=self.params['host'],
                workers=int(self.params['workers']),
                reload= False if str(settings("environment")) == 'live' else True,
                log_level=self.params["logLevel"],
            )

        except Exception as e:
            print("Error starting the server: ", e)
            sys.exit(1)

