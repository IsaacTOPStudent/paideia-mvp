from typing import List 
from src.domain.entities.academic_observation import AcademicObservation
from src.domain.ports.academic_observation_repository import AcademicObservationRepository
from src.domain.ports.external.student_service_port import StudentServicePort

from src.domain.exceptions import StudentNotFoundError, InvalidObservationDataError

class ListObservationsUseCase:
    def __init__(self, repository: AcademicObservationRepository, student_service: StudentServicePort):
        self.repository = repository
        self.student_service = student_service

    def execute(self, student_id: int, requester_id: int, requester_role: str, only_active: bool = True) -> List[AcademicObservation]:
        if student_id <= 0:
            raise InvalidObservationDataError("ID del estudiante inválido")
        
        student = self.student_service.get_student_info(
            student_id
        )

        if not student or not student.is_active:
            raise StudentNotFoundError(student_id)
        
        if requester_role == "TEACHER":
            return self.repository.find_by_student_and_teacher(student_id=student_id, teacher_id=requester_id)
        
        if only_active:
            return self.repository.find_active_by_student(student_id)
        
        return self.repository.find_by_student(student_id)
        