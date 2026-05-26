from django.utils import timezone

from src.domain.ports.student_repository import StudentRepository
from src.domain.exceptions import StudentNotFoundError

class DeactivateStudentUseCase:

    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self, student_id: int):

        student = self.repository.find_by_id(student_id)

        if not student:
            raise StudentNotFoundError(str(student_id))
        
        student.deactivate()

        return self.repository.save(student)

    