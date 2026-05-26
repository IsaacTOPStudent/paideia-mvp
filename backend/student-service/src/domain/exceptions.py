class DomainException(Exception):
    """
        Domain base exception
    """

class StudentAlreadyExistsError(DomainException):
    """
        Student already exists    
    """
    def __init__(self, document: str):
        self.document = document
        super().__init__(f"Ya existe un estudiante con documento: {document}")

class StudentNotFoundError(DomainException):
    """
        Student does not exists
    """
    def __init__(self, identifier: str):
        super().__init__(f"Estudiante no encontrado: {identifier}")

class InvalidStudentDataError(DomainException):
    """
        Invalid data student
    """

    def __init__(self, message: str):
        super().__init__(message)

class StudentNotReadyForCharacterizationError(DomainException):
    """
        Student is not ready for characterization
    """
    def __init__(self):
        super().__init__("El estudiante no tiene un perfil completo para caracterización")