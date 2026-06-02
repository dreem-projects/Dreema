"""Serialization helpers for Dreema.

This module defines a Json wrapper for dictionaries that supports
attribute-style access for nested payloads.
"""


class Json(dict):
    """
    Parameters:
        dict: any dictionary

    Returns:
        dict: return a json serialized version of the dictionary
              accessible using the dot(.) operator
    """

    def __init__(self, *args, **kwargs):
        super(Json, self).__init__(*args, **kwargs)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = Json(value)
            elif isinstance(value, list):
                self[key] = [Json(v) if isinstance(v, dict) else v for v in value]
                
    # set attr allows to add an object/key - eg: data.key = value
    __setattr__ = dict.__setitem__

    # del attr allows to delete a key - eg: del data.key
    __delattr__ = dict.__delitem__

    def __getattr__(self, attr):
        if attr not in self:
            raise AttributeError(f"Key '{attr}' does not exist")
        return self[attr]