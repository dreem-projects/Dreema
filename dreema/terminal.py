import sys
from .start import RunHandler
from dreema.helpers.serialization import Json
from dreema.helpers.cmd import CreateHandler, KwargsHandler




"""
    
    Use:
        To be used to create files from the terminal
        These files include Models, Views and Controllers
"""

# terminalParse function arguments to the the config
def terminalParse():
    try:
        argv = sys.argv
        isKwargs = True if '--' in argv[1] else False
        result = {
            "command": argv[1].lower() if not isKwargs else '',
            "args": [],
            "kwargs": {}
        }

        i = 2 if not isKwargs else 1
        isNamed = False

        while i < len(argv):
            token = argv[i]

            if token.startswith("--"):
                isNamed = True

                key = token[2:]

                if i + 1 >= len(argv):
                    # print(f"Error: Missing value for --{key}\nDefaulting to `True`")
                    result["kwargs"][key] = True

                else:
                    result["kwargs"][key] = argv[i + 1]
                
                i += 2

            else:
                if isNamed:
                    return f"Positional argument '{token}' cannot appear after named arguments", False

                result["args"].append(token)
                i += 1

        return Json(result) , True
    except Exception as e:
        print(e)
        return "Command not defined", False

def main():
    parser, success = terminalParse()

    if not success:
        print(parser)
        sys.exit(1)
    
    # handle each command
    if "create" in parser.get("command"):
        CreateHandler(parser)
        sys.exit(0)

    if "run" in parser.get("command"):
        RunHandler(parser)
        sys.exit(0)

    if not parser.get('command',None) and parser.get('kwargs',{}):
        KwargsHandler(parser)
        sys.exit(0)

    


if __name__ == "__main__":
    main()
   



