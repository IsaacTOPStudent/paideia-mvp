from abc import ABC, abstractmethod
from typing import Optional
from src.domain.dto.student_info import StudentInfoDTO

class StudentServicePort(ABC):

    @abstractmethod
    def get_student_info(self, student_id: int) -> Optional[StudentInfoDTO]:
        pass


