from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.academic_observation import AcademicObservation

class AcademicObservationRepository(ABC):

    @abstractmethod
    def save(self, observation: AcademicObservation) -> AcademicObservation:
        pass

    @abstractmethod
    def find_by_id(self, observation_id: int) -> Optional[AcademicObservation]:
        pass

    @abstractmethod
    def find_by_student(self, student_id: int) -> List[AcademicObservation]:
        pass

    @abstractmethod
    def find_active_by_student(self, student_id: int) -> List[AcademicObservation]:
        pass

    @abstractmethod
    def find_by_student_and_teacher(
        self,
        student_id: int,
        teacher_id: int
    ) -> List[AcademicObservation]:
        pass