class DomainException(Exception):
    """Base class para excepciones del dominio."""
    pass

class DiagnosticAlreadyExistsError(DomainException):
    """Raised cuando se intenta crear un diagnóstico que ya existe."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(f"Ya existe un diagnóstico con el código: {code}")

class DiagnosticNotFoundError(DomainException):
    """Raised cuando no se encuentra un diagnóstico."""
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(f"Diagnóstico no encontrado: {identifier}")

class InvalidDiagnosticDataError(DomainException):
    """Raised cuando los datos del diagnóstico no son válidos."""
    def __init__(self, message: str):
        super().__init__(message)

class CharacterizationAlreadyExistsError(DomainException):
    """Raised cuando ya existe una caracterización para un estudiante y diagnóstico."""
    def __init__(self, student_id: int, diagnostic_id: int):
        self.student_id = student_id
        self.diagnostic_id = diagnostic_id
        super().__init__(f"Ya existe una caracterización para el estudiante {student_id} y el diagnóstico {diagnostic_id}")

class CharacterizationNotFoundError(DomainException):
    """Raised cuando no se encuentra una caracterización."""
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(f"Caracterización no encontrada: {identifier}")

class InvalidCharacterizationDataError(DomainException):
    """Raised cuando los datos de la caracterización no son válidos."""
    def __init__(self, message: str):
        super().__init__(message)

class DiagnosticInactiveError(DomainException):
    """Raised cuando se intenta usar un diagnóstico inactivo."""
    def __init__(self, diagnostic_id: int):
        self.diagnostic_id = diagnostic_id
        super().__init__(f"El diagnóstico {diagnostic_id} está inactivo y no puede usarse.")
