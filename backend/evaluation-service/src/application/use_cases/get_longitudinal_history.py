from datetime import date
from typing import Optional

from src.domain.ports.psychological_evaluation_repository import (
    PsychologicalEvaluationRepository
)
from src.domain.ports.academic_observation_repository import (
    AcademicObservationRepository
)
from src.domain.ports.external.student_service_port import StudentServicePort
from src.domain.ports.external.characterization_service_port import CharacterizationServicePort

from src.domain.exceptions import (
    StudentNotFoundError
)

from src.application.dtos.longitudinal_history_dto import LongitudinalHistoryResult

class GetLongitudinalHistoryUseCase:
    def __init__(
        self,
        evaluation_repository: PsychologicalEvaluationRepository,
        observation_repository: AcademicObservationRepository,
        student_service: StudentServicePort,
        characterization_service: CharacterizationServicePort
    ):
        self.evaluation_repository = evaluation_repository
        self.observation_repository = observation_repository
        self.student_service = student_service
        self.characterization_service = characterization_service

    def execute(self, student_id: int, requester_role: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> LongitudinalHistoryResult:

        student = self.student_service.get_student_info(student_id)

        if student is None: 
            raise StudentNotFoundError(student_id)

        is_teacher = requester_role == "TEACHER"

        # Observations

        observations = self.observation_repository.find_active_by_student(student_id)

        if start_date and end_date:
            observations = [
                obs for obs in observations
                if start_date <= obs.observation_date <= end_date
            ]

        # Evaluations

        evaluations = []
        follow_up_status = None
        days_until_next = None

        if not is_teacher:
            evaluations = (
                self.evaluation_repository.find_active_by_student(student_id)
            )

            if start_date and end_date:
                evaluations = [
                    ev for ev in evaluations
                    if start_date <= ev.evaluation_date <= end_date
                ]

            latest = (
                self.evaluation_repository.find_latest_by_student(student_id)
            )

            if latest:
                follow_up_status = (
                    latest.follow_up_status.to_spanish()
                )

                days_until_next = (
                    latest.days_until_next_evaluation
                )

        # Characterizations

        characterizations = (
            self.characterization_service.get_characterizations(
                student_id
            )
        )

        if is_teacher:
            characterizations = [
                {
                "nee_category": car.nee_category,
                "diagnostic_name": car.diagnostic_name
                }
                for car in characterizations
            ]

        else:
            characterizations = [
                {
                    "id": car.id,
                    "diagnostic_name": car.diagnostic_name,
                    "nee_category": car.nee_category,
                    "severity_level": car.severity_level,
                    "identification_date": car.identification_date,
                }
                for car in characterizations
            ]

        # Results

        has_records = (
            len(evaluations) > 0
            or len(observations) > 0
            or len(characterizations) > 0
        )

        return LongitudinalHistoryResult(
            student_id=student_id,
            student_info={
                "id": student.id,
                "full_name": f"{student.first_name} {student.last_name}"
            },
            characterizations=characterizations,
            follow_up_status=follow_up_status,
            days_until_next_evaluation=days_until_next,

            evaluations=evaluations,
            observations=observations,

            total_evaluations=len(evaluations),
            total_observations=len(observations),

            has_records=has_records
        )