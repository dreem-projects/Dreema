import sys
from .start import RunHandler
from dreema.helpers.serialization import Json
from dreema.helpers.cmd import CreateHandler




"""
    
    Use:
        To be used to create files from the terminal
        These files include Models, Views and Controllers
"""

# terminalParse function arguments to the the config
def terminalParse():
    try:
        argv = sys.argv

        if len(argv) < 2:
            return "Error: No command provided", False

        result = {
            "command": argv[1].lower(),
            "args": [],
            "kwargs": {}
        }

        i = 2
        isNamed = False

        while i < len(argv):
            token = argv[i]

            if token.startswith("--"):
                isNamed = True

                key = token[2:]

                if i + 1 >= len(argv):
                    print(f"Error: Missing value for --{key}\nDefaulting to `True`")
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
    except:
        return "Command not defined", False

def main():
    parser, success = terminalParse()

    if not success:
        print(parser)
        sys.exit(1)
    
    # handle each command
    if "create" in parser.get("command"):
        CreateHandler(parser)
        sys.exit(1)

    if "run" in parser.get("command"):
        RunHandler(parser)
        sys.exit(1)
    


if __name__ == "__main__":
    main()
   



