from datetime import datetime 
from ...domain.entities.user import User 
from ...domain.ports.user_repository import UserRepository
from ...domain.exceptions import (
    UserNotFoundError,
    UnauthorizedOperationError,
    InvalidUserDataError
)
from ..dtos.user_dto import UserResponseDTO

class DeactivateUserUseCase:
    """
    Use case: Deactivate user (CU-02)
    
    Requirements:
    - RF-02: Manage users and basic roles
    - RN-01: Only admin can deactivate users
    - RN-18: Deactivation without deletion
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int, current_user: User) -> UserResponseDTO:
        """
        Use case execution

        Args: 
            user_id: ID of the user to deactivate
            current_user: The user performing the deactivation

        Returns:
            UserResponseDTO: The deactivated user data

        Raises:
            UnauthorizedOperationError: If the current user is not an admin
            UserNotFoundError: If the user to deactivate does not exist
            InvalidUserDataError: If the user is already inactive
        """

        if not current_user.can_manage_users():
            raise UnauthorizedOperationError(
                operation="desactivar usuarios",
                role=current_user.role.to_spanish()
            )
        
        user = self.user_repository.find_by_id(user_id)

        if not user:
            raise UserNotFoundError(str(user_id))
        
        if user.id == current_user.id:
            raise InvalidUserDataError("No puedes desactivar tu propia cuenta")
        
        user.deactivate()

        updated_user = self.user_repository.save(user)

        return UserResponseDTO.from_entity(updated_user)