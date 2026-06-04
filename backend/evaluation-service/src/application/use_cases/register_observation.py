from django.utils import timezone 

from src.domain.entities.academic_observation import AcademicObservation, Subject

from src.domain.ports.academic_observation_repository import AcademicObservationRepository

from src.domain.ports.external.student_service_port import StudentServicePort

from src.domain.ports.external.characterization_service_port import CharacterizationServicePort

from src.domain.exceptions import InvalidObservationDataError, StudentNotFoundError

class RegisterObservationUseCase:
    def __init__(self, repository: AcademicObservationRepository, student_service: StudentServicePort, characterization_service: CharacterizationServicePort):

        self.repository = repository
        self.student_service = student_service
        self.characterization_service = characterization_service

    def execute(self, data: dict, teacher_id: int, requester_role: str) -> tuple[AcademicObservation, str | None]:
        if requester_role != "TEACHER":
            raise InvalidObservationDataError("No tiene permisos para registrar observaciones académicas")
        
        student_id = data.get("student_id")
        if not student_id: 
            raise InvalidObservationDataError("El estudiante es obligatorio")
        
        student = self.student_service.get_student_info(student_id)

        if not student or not student.is_active:
            raise StudentNotFoundError(student_id)
        
        obs_date = data.get("observation_date")
        if not obs_date:
            raise InvalidObservationDataError("La fecha de observación es obligatoria")

        try:
            subject = Subject.from_string(data.get("subject", ""))
        except ValueError as e:
            raise InvalidObservationDataError(str(e))
        
        warning = None

        characterizations = (
            self.characterization_service.get_characterizations(student_id)
        )

        if not characterizations:
            warning = ("El estudiante no tiene diagnosticos NEE registrados")

        now = timezone.now()

        observation = AcademicObservation(
            student_id=student_id,
            teacher_id=teacher_id,
            observation_date=obs_date,
            subject=subject,
            performance_description=data.get("performance_description", ""),
            behavioral_notes=data.get("behavioral_notes", ""),
            pedagogical_adjustments_applied=data.get("pedagogical_adjustments_applied"),
            recommendations=data.get("recommendations"),
            created_at=now,
            updated_at=now,
            is_active=True,
        )

        is_valid, errors = observation.validate()
        if not is_valid:
            raise InvalidObservationDataError(
                "; ".join(errors)
            )
        
        return self.repository.save(observation), warning