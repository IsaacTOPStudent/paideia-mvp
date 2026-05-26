from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.characterization import Characterization

class CharacterizationRepository(ABC):
    """Port: Repository of characterizations"""

    @abstractmethod
    def save(self, characterization: Characterization) -> Characterization:
        """Save characterization"""
        pass

    @abstractmethod
    def find_by_id(self, characterization_id: int) -> Optional[Characterization]:
        """Search for characterization by ID"""
        pass

    @abstractmethod
    def find_by_student(self, student_id: int) -> List[Characterization]:
        """Find all the characterizations of a student"""
        pass
    
    @abstractmethod
    def find_active_by_student(self, student_id: int) -> List[Characterization]:
        """Finding active characterizations of a student"""
        pass

    @abstractmethod
    def find_by_student_and_diagnostic(self, student_id: int, diagnostic_id: int) -> Optional[Characterization]:
        """Check if there is a specific characterization"""
        pass