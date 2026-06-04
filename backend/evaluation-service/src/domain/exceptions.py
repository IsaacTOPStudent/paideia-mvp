class DomainException(Exception):
    pass

# Psychological evaluations

class EvaluationNotFoundError(DomainException):
    def __init__(self, evaluation_id: int):
        self.evaluation_id = evaluation_id
        super().__init__(f"Evaluación no encontrada: {evaluation_id}")

class InvalidEvaluationDataError(DomainException):
    def __init__(self, message: str):
        super().__init__(message)

class EvaluationCannotBeDeletedError(DomainException):
    def __init__(self):
        super().__init__(
            "Las evaluaciones psicologicas no pueden eliminarse."
        )

# Academic observations
class ObservationNotFoundError(DomainException):
    def __init__(self, observation_id: int):
        self.observation_id = observation_id
        super().__init__(f"Observación no encontrada: {observation_id}")

class InvalidObservationDataError(DomainException):
    def __init__(self, message: str):
        super().__init__(message)

class ObservationCannotBeDeletedError(DomainException):
    def __init__(self):
        super().__init__("Las observaciones académicas no pueden eliminarse.")

class ObservationAccessDeniedError(DomainException):
    def __init__(self):
        super().__init__(
            "No tiene permisos para acceder a esta observación"
        )

# Longitudinal history
class StudentHasNoEvaluationsError(DomainException):
    def __init__(self, student_id: int):
        self.student_id = student_id
        super().__init__(
            f"El estudiante {student_id} no tiene evaluaciones registradas aún"
        )

# Microservices integration
class StudentNotFoundError(DomainException):

    def __init__(self, student_id: int):
        super().__init__(
            f"Estudiante {student_id} no encontrado."
        )


class StudentNotCharacterizedError(DomainException):

    def __init__(self, student_id: int):
        super().__init__(
            f"El estudiante {student_id} "
            f"no tiene caracterización NEE."
        )


class ExternalServiceError(DomainException):

    def __init__(self, service_name: str, message: str):
        super().__init__(
            f"Error comunicándose con "
            f"{service_name}: {message}"
        )
