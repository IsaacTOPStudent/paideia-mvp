from datetime import datetime
from ...domain.entities.user import User, UserStatus 
from ...domain.ports.user_repository import UserRepository
from ...domain.exceptions import (
    UserNotFoundError,
    UnauthorizedOperationError,
    InvalidUserDataError
)
from ..dtos.user_dto import UserResponseDTO

class  ReactivateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int, current_user: User) -> UserResponseDTO:
        if not current_user.can_manage_users():
            raise UnauthorizedOperationError(
                operation="reactivar usuario",
                role=current_user.role.to_spanish()
            )
        
        user = self.user_repository.find_by_id(user_id)
        if not user: 
            raise UserNotFoundError(str(user_id))
        
        if user.id == current_user.id:
            raise InvalidUserDataError("No puedes reactivar tu propia cuenta")
        
        if user.status == UserStatus.ACTIVE:
            raise InvalidUserDataError("El usuario ya está activo")
        
        user.reactivate()
        updated_user = self.user_repository.save(user)
        return UserResponseDTO.from_entity(updated_user)