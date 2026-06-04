from typing import List
from src.domain.entities.student import Student 
from src.domain.ports.student_repository import StudentRepository

class ListStudentsUseCase:

    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self, include_inactive: bool = False) -> List[Student]:

        if include_inactive:
            return self.repository.find_all_including_inactive()
        
        return self.repository.find_all()