"""

Use:
    serves as the entry point for the application
    Runs uvicorn as the main server and parse all
    information required to index.py for processing
"""

import argparse
# import uvicorn
from dreema.helpers import settings
import socket, sys

# auto retry server
def findAvailablePort(userPort=8888, retries=10):
    port = userPort
    for _ in range(retries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError("No available ports found")


# autoparse function arguments to the config
def autoParse():
    parser = argparse.ArgumentParser(description="Start Dreema server")

    parser.add_argument(
        "--port",
        type=int,
        default=settings("SERVER_PORT", 8888),
        help="Port to run the server on"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address"
    )

    parser.add_argument(
        "--reload",
        dest="reload",
        action="store_true",
        help="Enable auto-reload"
    )

    parser.add_argument(
        "--no-reload",
        dest="reload",
        action="store_false",
        help="Disable auto-reload"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        help="Logging level"
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker processes"
    )

    # Set default AFTER defining reload flags
    parser.set_defaults(
        reload=settings("environment", "local") == "local"
    )


    args = parser.parse_args()

    return {
        "port": args.port,
        "host": args.host,
        "reload": args.reload,
        "logLevel": args.log_level,
        "workers": args.workers,
    }

if __name__ == "__main__":
    try:
        parser = autoParse()
        port = findAvailablePort(int(parser['port']))
        
        if port != parser['port']:
            print(f"❌ Port {parser['port']} is already in use")

            res = input(f"👉 Enter 'y' to run with the next available port - {port} : ")
            if res not in ['y', 'Y']:
                sys.exit(1)

        uvicorn.run(
            "index:app",
            port=port,
            host=parser['host'],
            workers=int(parser['workers']),
            reload=False if str(settings("environment") or parser.get("reload")) == "live" else True,
            log_level=parser["logLevel"],
        )

    except Exception as e:
        print("Error starting the server: ", e)
        sys.exit(1)

# COMMAND TO START CELERY
# celery -A dreema.scheduler.setup.scheduler worker --loglevel=info
# celery -A dreema.scheduler.setup.scheduler beat --loglevel=info
