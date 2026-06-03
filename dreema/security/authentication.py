"""Authentication registry and request auth helper for Dreema.

This module allows apps to register a custom async authentication handler
and provides a shared authenticate() helper for request-level validation.
"""

from dreema.helpers import Json
from dreema.responses import SysCodes

# Global auth handler - apps register their implementation
_auth_handler = None


def setAuthHandler(handler):
    """
    Set the authentication handler for request.auth().
    
    The handler must be an async function with signature:
        async def handler(request, *args, **kwargs) -> Json
    
    Parameters:
        handler: Async function that handles authentication
    
    Example:
        from dreema.security import setAuthHandler
        
        async def myAuthHandler(request, *args, **kwargs):
            # Extract types or any other params you need
            types = kwargs.get('types', [])
            
            # Your authentication logic here
            cookies = parseCookies(request)
            user = await verifyUser(cookies, types)
            
            if user:
                return Json({
                    'data': user,
                    'status': 1,
                    'message': 'Authenticated'
                })
            
            return Json({
                'data': None,
                'status': -1,
                'message': 'Unauthorized'
            })
        
        setAuthHandler(myAuthHandler)
    """
    global _auth_handler
    _auth_handler = handler


def getAuthHandler():
    """Get the currently registered auth handler."""
    return _auth_handler


async def authenticate(request, *args, **kwargs):
    """
    Authenticate a request using the registered handler.
    
    This is called internally by request.auth().
    
    Parameters:
        request: The Request object
        *args: Additional positional arguments passed to handler
        **kwargs: Additional keyword arguments passed to handler
    
    Returns:
        Json: Authentication result from the handler
    """
    handler = _auth_handler
    
    if handler is None:
        return Json({
            'data': None,
            'status': SysCodes.INVALID_CREDS,
            'message': 'No authentication handler registered. Call setAuthHandler() in your app.'
        })
    
    return await handler(request, *args, **kwargs)

