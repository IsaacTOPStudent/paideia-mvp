from abc import ABC, abstractmethod
from src.domain.entities.user import User

class UserRepository(ABC):

    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> User:
        pass

    