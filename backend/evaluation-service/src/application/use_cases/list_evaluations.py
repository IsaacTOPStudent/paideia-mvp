from typing import List
from src.domain.entities.psychological_evaluation import PsychologicalEvaluation
from src.domain.ports.psychological_evaluation_repository import PsychologicalEvaluationRepository
from src.domain.ports.external.student_service_port import StudentServicePort

from src.domain.exceptions import StudentNotFoundError

class ListEvaluationsUseCase:
    def __init__(self, repository: PsychologicalEvaluationRepository, student_service: StudentServicePort):
        self.repository = repository
        self.student_service = student_service

    def execute(self, student_id: int, is_active: bool = True) -> List[PsychologicalEvaluation]:
        student = self.student_service.get_student_info(student_id)
        if not student or not student.is_active:
            raise StudentNotFoundError(student_id)

        if is_active:
            return self.repository.find_active_by_student(student_id)
        
        return self.repository.find_by_student(student_id)