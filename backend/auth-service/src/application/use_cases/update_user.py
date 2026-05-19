from datetime import datetime 
from ...domain.entities.user import User, UserRole
from ...domain.ports.user_repository import UserRepository
from ...domain.exceptions import (
    UserNotFoundError,
    InvalidUserDataError,
    UnauthorizedOperationError
)
from ..dtos.user_dto import UpdateUserDTO, UserResponseDTO

class UpdateUserUseCase:
    """
    Use case: Update user (CU-02)

    Requirements:
    - RF-02: Manage users and basic roles
    - RN-01: Only admin can update users
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, dto: UpdateUserDTO, current_user: User) -> UserResponseDTO:
        """
        Execute use case

        Args:
            dto: Data of the user to update
            current_user: The user performing the update

        Returns:
            UserResponseDTO: The updated user data

        Raises:
            UnauthorizedOperationError: If the current user is not an admin
            UserNotFoundError: If the user to update does not exist
            InvalidUserDataError: If the provided data is invalid
        """

        if not current_user.can_manage_users():
            raise UnauthorizedOperationError(
                operation="actualizar usuarios",
                role=current_user.role.to_spanish()
            )
        
        # Fetch the user to update
        user = self.user_repository.find_by_id(dto.user_id)
        if not user:
            raise UserNotFoundError(str(dto.user_id))
        
        # Validate and update fields
        if dto.full_name is not None:
            if not dto.full_name.strip():
                raise InvalidUserDataError("El nombre completo no puede estar vacío")
            user.full_name = dto.full_name.strip()

        if dto.role is not None:
            try:
                new_role = UserRole(dto.role)
                user.role = new_role
            except ValueError:
                raise InvalidUserDataError(f"Rol inválido: {dto.role}")
            
        user.updated_at = datetime.now()

        updated_user = self.user_repository.save(user)

        return UserResponseDTO.from_entity(updated_user)
