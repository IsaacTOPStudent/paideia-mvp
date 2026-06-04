from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.student import Student 

class StudentRepository(ABC):
    """
        Port: Student repository interface
    """

    @abstractmethod
    def save(self, student: Student) -> Student:
        pass 

    @abstractmethod
    def find_by_id(self, student_id: int) -> Optional[Student]:
        pass 

    @abstractmethod
    def find_by_document(self, document: str) -> Optional[Student]:
        pass 

    @abstractmethod
    def find_all(self) -> List[Student]:
        pass

    @abstractmethod
    def find_all_including_inactive(self) -> List[Student]:
        pass 

    @abstractmethod 
    def exists_by_document(self, document: str) -> bool:
        pass

