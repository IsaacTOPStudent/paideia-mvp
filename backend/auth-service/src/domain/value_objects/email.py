import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    """
    Value Object: Email
    Represents a valid email address.
    """

    value: str

    def __post_init__(self):
        if not self._is_valid(self.value):
            raise ValueError(f"Email inválido: {self.value}")
        
    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def __str__(self):
        return self.value