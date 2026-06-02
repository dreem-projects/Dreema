import sys
from helpers.cmd import Model, Controller, View

"""
    
    Use:
        To be used to create files from the terminal
        These files include Models, Views and Controllers
"""

def createCommand():
    pass

# terminalParse function arguments to the the config
def terminalParse():
    result = {}
    for arg in sys.argv:
        split = arg.split("=")
        if len(split) < 2:
            continue
        result[f"{split[0]}"] = split[1]

    # lowercase the keys
    result = {key.lower(): value for key, value in result.items()}
    print(result)

    # create attribute validation
    if result.get("create", None):
        allowedtypes = ["view", "controller", "model"]
        if result.get("create", None).lower() not in allowedtypes:
            print("Error: Create options available are view, controller, and model")
            return None

    if not result.get("create", None):
        print("Error: You must parse the create attribute")
        return None

    # class attributes
    if not result.get("class", None):
        print("Error: You must parse the class attribute")
        return None

    # name of file
    if not result.get("name", None):
            print("Error: You must parse the name for the file")
            return None

    return result


if __name__ == "__main__":
    parser = terminalParse()

    print(parser)
    if parser:
        #
        if parser.get("create") == "model":
            mod = Model()
            mod.create(parser.get("class"), parser.get("name"))

        #
        if parser.get("create") == "controller":
            cont = Controller()
            cont.create(parser.get("class"), parser.get("name"))

        #
        if parser.get("create") == "view":
            view = View()
            view.create(parser.get("class"), parser.get("name"))
