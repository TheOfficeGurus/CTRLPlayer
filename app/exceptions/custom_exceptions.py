class APIException(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

class InvalidCredentials(APIException):
    def __init__(self):
        super().__init__("Invalid credentials", 401)
class InvalidRequestError(APIException):
    def __init__(self):
        super().__init__("Invalid request", 400)
        
class JWTExeptions(Exception):
    def __init__(self, message):
        self.message = message

class TokenExpired(JWTExeptions):
    def __init__(self):
        super().__init__("Token expired")
        
class TokenInvalidAuth(JWTExeptions):
    def __init__(self):
        super().__init__("Authorization header missing or invalid token")
class TokenClaimsMismatch(JWTExeptions):
    def __init__(self):
        super().__init__("Unauthorized: claim mismatch")
class TokenConfigExeption(JWTExeptions):
    def __init__(self):
        super().__init__("Config: Missing configuration contact the system admin")
        
class UserExceptions(Exception):    
    def __init__(self, message):
        self.message = message
class UserADNoUpdatedException(UserExceptions):
    def __init__(self,message):
        self.message = message
class UserNotFoundException(UserExceptions):
    def __init__(self,message):
        # super().__init__("User not found")
        self.message=message
class UserEmpIDInUseException(UserExceptions):
    def __init__(self,message):
        super().__init__("Employee ID is in use by another user")
