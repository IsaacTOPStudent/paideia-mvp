from abc import ABC, abstractmethod
from typing import Optional
from src.domain.dto.characterization_info import CharacterizationInfoDTO


class CharacterizationServicePort(ABC):

    @abstractmethod
    def get_characterizations(self, student_id: int) -> list[CharacterizationInfoDTO]:
        pass
