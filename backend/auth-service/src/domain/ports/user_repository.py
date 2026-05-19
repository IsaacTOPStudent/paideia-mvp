from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.user import User

class UserRepository(ABC):
    """
    Port: User repository interface
    Decouples domain from infrastructure
    """

    @abstractmethod
    def save(self, user: User) -> User:
        """
        Save or update a user

        Returns:
            User with assigned ID

        Raises:
            UserAlreadyExistsError: If a user with the same email already exists
        """

        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        Find a user by ID

        Returns:
            User if found, else None
        """

        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by email

        Returns:
            User if found, else None
        """

        pass

    @abstractmethod
    def find_all_active(self) -> List[User]:
        """
        Find all active users
        
        Returns:
            List of active users
        """
        pass

    @abstractmethod
    def find_all(self) -> List[User]:
        """
        Find all users

        Returns:
            List of users
        """

        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """
        Check if a user exists by email
        
        Returns:
            True if user exists, False otherwise
        """
        pass

    @abstractmethod
    def deactivate(self, user_id: int) -> bool:
        """
        Deactivate a user by ID (soft delete)
        
        Returns:
            True if user was marked as deactivated, False if user not found
        """
        pass

    @abstractmethod
    def reactivate(self, user_id: int) -> bool:
        """
            Reactivate a user by ID.
            Returns True if user was marked active, False if not found
        """
        pass