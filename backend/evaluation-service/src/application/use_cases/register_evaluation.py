from django.utils import timezone 
from datetime import date

from src.domain.entities.psychological_evaluation import (
    PsychologicalEvaluation,
    FollowUpFrequency,
)
from src.domain.ports.psychological_evaluation_repository import (
    PsychologicalEvaluationRepository,
)

from src.domain.ports.external.characterization_service_port import CharacterizationServicePort
from src.domain.ports.external.student_service_port import StudentServicePort

from src.domain.exceptions import InvalidEvaluationDataError, StudentNotFoundError, StudentNotCharacterizedError

class RegisterEvaluationUseCase: 
    def __init__(self, repository: PsychologicalEvaluationRepository, student_service: StudentServicePort, characterization_service: CharacterizationServicePort):
        self.repository = repository
        self.student_service = student_service
        self.characterization_service = characterization_service

    def execute(self, data: dict, psychologist_id: int, requester_role: str) -> PsychologicalEvaluation:
        if requester_role != "PSYCHOLOGIST":
            raise InvalidEvaluationDataError("No tiene permisos para registrar evaluaciones")

        student_id = data.get("student_id")

        if not student_id:
            raise InvalidEvaluationDataError("El estudiante es obligatorio")
        
        evaluation_date = data.get("evaluation_date")

        if not evaluation_date:
            raise InvalidEvaluationDataError("La fecha de evaluación es obligatoria")
        
        next_date = data.get("next_evaluation_date")

        if not next_date:
            raise InvalidEvaluationDataError("Se debe proporcionar la fecha de la proxima evaluación")
        
        student = self.student_service.get_student_info(student_id)

        if not student or not student.is_active: 
            raise StudentNotFoundError(student_id)
        
        characterizations = (
            self.characterization_service.get_characterizations(student_id)
        )
        if not characterizations: 
            raise StudentNotCharacterizedError(student_id)

        try:
            frequency = FollowUpFrequency.from_string(data.get("follow_up_frequency", ""))

        except ValueError as e:
            raise InvalidEvaluationDataError(str(e))

        now = timezone.now()

        evaluation = PsychologicalEvaluation(
            student_id=student_id,
            psychologist_id=psychologist_id,
            evaluation_date=evaluation_date,
            instrument_used=data.get("instrument_used", ""),
            findings=data.get("findings", ""),
            recommendations=data.get("recommendations", ""),
            cognitive_assessment=data.get("cognitive_assessment"),
            emotional_assessment=data.get("emotional_assessment"),
            behavioral_assessment=data.get("behavioral_assessment"),
            motor_assessment=data.get("motor_assessment"),
            social_assessment=data.get("social_assessment"),
            follow_up_frequency=frequency,
            next_evaluation_date=next_date,
            created_at=now,
            updated_at=now,
            is_active=True,
        )

        is_valid, errors = evaluation.validate()
        if not is_valid:
            raise InvalidEvaluationDataError(
                "; ".join(errors)
            )

        return self.repository.save(evaluation)