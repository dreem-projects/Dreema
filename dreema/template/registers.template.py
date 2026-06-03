# registers.py
# This registers all app-specific handlers before any requests are processed


from dreema.security import setAuthHandler

# ============================================
# REGISTER AUTH HANDLER
# ============================================
# Create your auth handler anywhere and then import and register here:
#
# Example:
# from utilities.AuthHandler import authHandler
# setAuthHandler(authHandler)
# print("==> Auth handler: registered")

# ============================================
# EXTEND CODES (optional)
# ============================================
# Add app-specific status codes and messages:
#
# from dreema.responses import extendCodes, extendMessages
# extendCodes({
#     'CUSTOM_ERROR': -100,
#     'CUSTOM_SUCCESS': 100,
# })
# extendMessages({
#     'CUSTOM_ERROR': 'A custom error occurred',
#     'CUSTOM_SUCCESS': 'Custom operation successful',
# })
# print("==> Custom codes: registered")

