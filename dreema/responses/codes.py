"""Response codes and messages for Dreema.

This module defines HTTP status constants and internal response codes
and messages used throughout the framework.
"""


class StatusCodes:
    """
    Contains HTTP status codes
    """
    # 2xx Success
    OK                          = 200                          
    CREATED                     = 201                     
    ACCEPTED                    = 202                    
    NO_CONTENT                  = 204                  
    
    # 3xx Redirection
    MOVED_PERMANENTLY           = 301          
    FOUND                       = 302                      
    NOT_MODIFIED                = 304                
    
    # 4xx Client Errors
    BAD_REQUEST                 = 400               
    UNAUTHORIZED                = 401               
    FORBIDDEN                   = 403               
    NOT_FOUND                   = 404               
    METHOD_NOT_ALLOWED          = 405               
    CONFLICT                    = 409               
    UNPROCESSABLE_ENTITY        = 422               
    
    # 5xx Server Errors
    INTERNAL_SERVER_ERROR       = 500               
    NOT_IMPLEMENTED             = 501               
    BAD_GATEWAY                 = 502               
    SERVICE_UNAVAILABLE         = 503               
    GATEWAY_TIMEOUT             = 504               


class SysMessages:
    """
    Contains string representation of custom codes
    """
    SETUP_COMPLETED             = "Setup completed successfully"
    SETUP_FAILED                = "Setup failed"
    
    # database
    DB_CONNECTION_FAILED        = "Database connection failed"
    DB_CONNECTION_SUCCESS       = "Database connection successful"
    DB_ATTR_MISSING             = "Database connection attribute is missing"
    CREATE_SUCCESS              = "CREATE operation successful"
    READ_SUCCESS                = "Read operation successful"
    UPDATE_SUCCESS              = "Update operation successful"
    DELETE_SUCCESS              = "Delete operation successful"
    RECORD_FOUND                = "Record Found"
    OP_SUCCESS                  = "Operation successful"
    OP_COMPLETED                = "Operation completed"
    BUILD_SUCCESS               = "Query build operation successful"
    
    # system flags
    ENV_NOT_FOUND               = '.env File not found'
    ENV_KEY_NOT_FOUND           = 'Key not found in .env'
    ENV_READ_FAILED             = 'Reading .env failed'
    UNKNOWN_ERROR               = 'An unknown error occurred'
    
    CREATE_FAILED               = "CREATE operation failed"
    ALREADY_EXISTS              = "Record already exists"
    READ_FAILED                 = "Read operation failed"
    UPDATE_FAILED               = "Update operation failed"
    DELETE_FAILED               = "Delete operation failed"
    NO_RECORD                   = "Record Not Found"
    OP_FAILED                   = "Operation failed"
    BUILD_FAILED                = "Query build operation failed"
        
    TABLE_FOUND                 = "Table Found"
    DB_CONNECTED                = "Database connection successful"
    TABLE_NOT_FOUND             = "Table not found"
    INVALID_CREDS               = "Invalid credentials"
    ATTR_MISSING                = "Attribute is missing"
    ATTR_FOUND                  = "All required attributes found"
        
    # HTTP
    ENDPOINT_NOT_FOUND          = 'Endpoint not found'
    UNALLOWED_METHOD            = 'This method not allowed'
    ENDPOINT_FUNC_FAIL          = 'Could not process endpoint controller'
    CORS_ORIGIN_NOT_ALLOWED     = 'Unauthorized origin'
    CORS_METHOD_NOT_ALLOWED     = 'CORS for certain methods not allowed'
    CORS_HEADER_NOT_ALLOWED     = 'CORS for certain headers not allowed'
    CORS_NO_ISSUES              = 'No CORS issues found'
    CORS_ERRORS                 = 'Could not process CORS'

    SCHEDULER_SETUP_SUCCESS     = "Scheduler setup success"
    SCHEDULER_SETUP_FAILED      = "Scheduler setup failed"
    SCHEDULE_OP_SUCCESS         = "Scheduling operation successful"
    SCHEDULE_OP_FAILED          = "Scheduling operation failed"

    # REDIS
    REDIS_SETUP_FAILED          = 'Setup for redis server failed'
    REDIS_SETUP_SUCCESS         = 'Setup for redis successful'
    REDIS_CREATE_FAILED         = 'Create Operation failed'
    REDIS_CREATE_SUCCESS        = 'Create Operation successful'
    REDIS_READ_FAILED           = 'Getting value failed'
    REDIS_READ_SUCCESS          = 'Getting value successful'
    REDIS_KEY_NOT_FOUND         = 'No data found'
    REDIS_NO_RECORD             = 'No Records found'
    
    # FILES
    FILE_NOT_EXISTS             = 'File does not exist'
    FILE_TOO_BIG                = 'File size is too big'
    FILE_UPLOAD_FAILED          = 'File upload failed'
    FILE_EXT_NOT_ALLOWED        = 'File extension not allowed'
    FILE_UPLOAD_SUCCESS         = 'File uploaded successfully'
    FILE_DES_NOT_FOUND          = 'Could not find file destination'
    
    # SECURITY
    AUTH_FAILED                 = 'Auth failed'
    AUTH_EXPIRED                = 'Auth token expired'
    AUTH_REVOKED                = 'Auth token revoked'
    AUTH_SUCCESS                = 'Auth successful'
    USER_NOT_VERIFIED           = 'User not verified to take request'
    USER_VERIFIED               = 'User is verified'

    # PAYMENTS
    PAYMENT_SUCCESSFUL          = "Payment successful"
    PAYMENT_FAILED              = "Payment not successful"
    PAYMENT_VERIFIED_SUCCESS    = "Payment verification successful"
    PAYMENT_VERIFIED_FAILED     = "Payment verification failed"
    PAYMENT_INIT_FAILED         = "Payment initialization failed"
    PAYMENT_INITIALIZED         = "Payment initialization successful"
    INVALID_PAYMENT_DETAILS     = "Invalid payment details"
    NO_PAYMENTS_FOUND           = "No payments found"
    
    
class SysCodes:
    """
    Contains integer representation of custom codes
    """
    SETUP_COMPLETED             = 100
    SETUP_FAILED                = -100
    
    # database 21-29
    DB_CONNECTION_SUCCESS       = 21
    CREATE_SUCCESS              = 22
    READ_SUCCESS                = 23
    UPDATE_SUCCESS              = 24
    DELETE_SUCCESS              = 25
    RECORD_FOUND                = 26
    OP_SUCCESS                  = 27
    OP_COMPLETED                = 28
    BUILD_SUCCESS               = 29
    
    DB_CONNECTION_FAILED        = -21
    DB_ATTR_MISSING             = -30
    CREATE_FAILED               = -22
    ALREADY_EXISTS              = -23
    READ_FAILED                 = -24
    UPDATE_FAILED               = -25
    DELETE_FAILED               = -26
    NO_RECORD                   = -27
    OP_FAILED                   = -28
    BUILD_FAILED                = -29
    TABLE_NOT_FOUND             = -29
    
    # system flags 0-10
    ATTR_FOUND                  = 1
    ATTR_MISSING                = -1
    ENV_NOT_FOUND               = -2
    ENV_KEY_NOT_FOUND           = -3
    ENV_READ_FAILED             = -4
    UNKNOWN_ERROR               = -5
    INVALID_CREDS               = -20
        
    # HTTP 11-19
    ENDPOINT_NOT_FOUND          = -11
    UNALLOWED_METHOD            = -12
    ENDPOINT_FUNC_FAIL          = -13
    CORS_ORIGIN_NOT_ALLOWED     = -14
    CORS_METHOD_NOT_ALLOWED     = -15
    CORS_HEADER_NOT_ALLOWED     = -16
    CORS_ERRORS                 = -17
    CORS_NO_ISSUES              = 12

    # SCHEDULER 32-34
    SCHEDULER_SETUP_SUCCESS     = 32
    SCHEDULER_SETUP_FAILED      = -32
    SCHEDULE_OP_SUCCESS         = 33
    SCHEDULE_OP_FAILED          = -33

    # REDIS 35-49
    REDIS_SETUP_FAILED          = -35
    REDIS_SETUP_SUCCESS         = 35
    REDIS_CREATE_FAILED         = -36
    REDIS_CREATE_SUCCESS        = 36
    REDIS_READ_FAILED           = -37
    REDIS_READ_SUCCESS          = 37
    REDIS_KEY_NOT_FOUND         = -38
    REDIS_NO_RECORD             = -39

    # FILES 40-50 
    FILE_UPLOAD_SUCCESS         = 41
    FILE_NOT_EXISTS             = -41
    FILE_TOO_BIG                = -42
    FILE_UPLOAD_FAILED          = -43
    FILE_EXT_NOT_ALLOWED        = -44
    FILE_DES_NOT_FOUND          = -45

    # SECURITY 50-60
    AUTH_INVALID                = -55
    AUTH_FAILED                 = -51
    AUTH_EXPIRED                = -52
    AUTH_REVOKED                = -53
    AUTH_SUCCESS                = 51
    USER_NOT_VERIFIED           = -54
    USER_VERIFIED               = 54
    
    # PAYMENTS 61-70
    PAYMENT_SUCCESSFUL          = 61
    PAYMENT_FAILED              = -61
    PAYMENT_INITIALIZED         = 62
    PAYMENT_INIT_FAILED         = -62
    INVALID_PAYMENT_DETAILS     = -63
    NO_PAYMENTS_FOUND           = -64
    PAYMENT_VERIFIED_SUCCESS    = 65
    PAYMENT_VERIFIED_FAILED     = -65


def extendCodes(custom_codes: dict):
    """
    Extend SysCodes with app-specific codes.
    
    Parameters:
        custom_codes: Dictionary of code_name -> code_value
    
    Example:
        from dreema.responses import extendCodes
        
        extendCodes({
            'STUDENT_NOT_FOUND': -101,
            'STUDENT_CREATED': 101,
            'GRADE_SUBMITTED': 102,
        })
    """
    for name, value in custom_codes.items():
        setattr(SysCodes, name, value)


def extendMessages(custom_messages: dict):
    """
    Extend SysMessages with app-specific messages.
    
    Parameters:
        custom_messages: Dictionary of message_name -> message_string
    
    Example:
        from dreema.responses import extendMessages
        
        extendMessages({
            'STUDENT_NOT_FOUND': 'Student not found',
            'STUDENT_CREATED': 'Student created successfully',
            'GRADE_SUBMITTED': 'Grade submitted successfully',
        })
    """
    for name, value in custom_messages.items():
        setattr(SysMessages, name, value)

