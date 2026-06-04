from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.psychological_evaluation import PsychologicalEvaluation

class PsychologicalEvaluationRepository(ABC):

    @abstractmethod
    def save(self, evaluation: PsychologicalEvaluation) -> PsychologicalEvaluation:
        pass

    @abstractmethod
    def find_by_id(self, evaluation_id: int) -> Optional[PsychologicalEvaluation]:
        pass

    @abstractmethod
    def find_by_student(self, student_id: int) -> List[PsychologicalEvaluation]:
        pass

    @abstractmethod
    def find_active_by_student(self, student_id: int) -> List[PsychologicalEvaluation]:
        pass

    @abstractmethod
    def find_latest_by_student(self, student_id: int) -> Optional[PsychologicalEvaluation]:
        pass

    @abstractmethod
    def has_evaluations(self, student_id: int) -> bool:
        pass

