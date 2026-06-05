import os
import importlib.util
from . import Json

_SETTINGS_CACHE = None
_ENV_CACHE = None


def loadenv():
    """Load .env from cwd once, then return cached Json of key=value pairs."""
    global _ENV_CACHE
    if _ENV_CACHE is not None:
        return _ENV_CACHE
    envdict = {}
    try:
        cwd = os.environ.get('DREEMA_APP_PATH', '')
        path = os.path.join(cwd, ".env")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        key, _, value = line.partition("=")
                        envdict[key.strip()] = value.strip().strip("'").strip('"')
    except OSError:
        envdict = {}
    _ENV_CACHE = Json(envdict)
    return _ENV_CACHE


def loadSetting():
    """
    Load all top-level variables from settings.py in the cwd,
    return as a Json object. Cached after first load.
    """
    global _SETTINGS_CACHE
    if _SETTINGS_CACHE is not None:
        return _SETTINGS_CACHE

    cwd = os.getcwd()
    path = os.path.join(cwd, "settings.py")

    if os.path.isfile(path):
        try:
            spec = importlib.util.spec_from_file_location("settings", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Collect all top-level variables (ignore built-ins)
            settings_dict = {
                key: value
                for key, value in vars(module).items()
                if not key.startswith("__")
            }

            _SETTINGS_CACHE = Json(settings_dict)
            return _SETTINGS_CACHE

        except Exception as e:
            pass

    _SETTINGS_CACHE = Json({})
    return _SETTINGS_CACHE


def settings(key: str = None, default=None):
    """
    Access variables from settings.py.
    Supports dot-notation for nested dictionaries.

    Examples:
        settings("DATABASES.default.HOST")
        settings("DEBUG", False)

    Returns:
        The value if found, else default.
    """
    data = loadSetting()
    if not key:
        return data
    parts = key.split(".")
    try:
        for part in parts:
            data = data[part]
        return data
    except (KeyError, TypeError):
        return default


def getenv(key: str, default: str = None) -> str:
    """
    Use:
            Read from .env file to be used by other
            parts of the library

    Parameters:
            key (str): the key is needed to reference to the keyname of the variable

    Returns:
            str: a string of the value of the specified key
            Default: None

    """
    try:
        return loadenv().get(key, default)
    except Exception:
        return default