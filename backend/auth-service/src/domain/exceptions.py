class DomainException(Exception):
    """Base class for domain exceptions."""
    pass

class UserAlreadyExistsError(DomainException):
    """Raised when trying to create a user that already exists."""
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Ya existe un usuario con el email: {email}")

class UserNotFoundError(DomainException):
    """Raised when a user is not found"""
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(f"Usuario no encontrado: {identifier}")

class InvalidUserDataError(DomainException):
    """Raised when user data is invalid."""
    def __init__(self, message: str):
        super().__init__(message)

class UnauthorizedOperationError(DomainException):
    """Raised when a user attempts an operation they are not authorized to perform."""
    def __init__(self, operation: str, role: str):
        super().__init__(f"El rol {role} no puede realizar la operación: {operation}")

class InactiveUserError(DomainException):
    """User is inactive"""
    def __init__(self, email: str):
        super().__init__(f"El usuario {email} está inactivo")
