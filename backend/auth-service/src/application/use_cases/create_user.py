from datetime import datetime
from typing import Optional
from ...domain.entities.user import User, UserRole, UserStatus
from ...domain.ports.user_repository import UserRepository
from ...domain.value_objects.email import Email
from ...domain.exceptions import (
    UserAlreadyExistsError,
    InvalidUserDataError, 
    UnauthorizedOperationError
)
from ..dtos.user_dto import CreateUserDTO, UserResponseDTO

class CreateUserUseCase:
    """
    Use Case: Create user (CU-02)

    Requirements:
    - RF-02: Manage users and basic roles
    - RN-01: Only admin can create users
    - RN-02: Unique Email
    - RN-17 required fields
    """

    def __init__(self, user_repository: UserRepository, password_hasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher 

    def execute(self, dto: CreateUserDTO, current_user: Optional[User] = None) -> UserResponseDTO:
        """
        Execute Use Case

        Args:
        dto: Data of the user to create
        current_user: User executing the action (for RN-01)

        Returns:
        UserResponseDTO with the created user

        Raises:
        UnauthorizedOperationError: If not Admin
        UserAlreadyExistsError: If the email already exists
        InvalidUserDataError: If the data is invalid
        """

        #Validation RN-01: Only Admin can create users

        if current_user and not current_user.can_create_users():
            raise UnauthorizedOperationError(
                operation="crear usuarios",
                role=current_user.role.to_spanish()
            )

        try:
            email = Email(dto.email.lower().strip())
        except ValueError as e:
            raise InvalidUserDataError(f"Email inválido: {str(e)}")

        if self.user_repository.exists_by_email(email.value):
            raise UserAlreadyExistsError(email.value)
        
        if not dto.full_name or not dto.full_name.strip():
            raise InvalidUserDataError("El nombre completo es obligatorio")
        
        if not dto.password or len(dto.password) < 8:
            raise InvalidUserDataError("La contraseña es obligatoria y debe tener al menos 8 caracteres")
        
        #validate rol
        try:
            role = UserRole(dto.role)
        except ValueError:
            raise InvalidUserDataError(f"Rol inválido: {dto.role}")
        
        password_hash = self.password_hasher.hash(dto.password)
        
        user = User(
            id=None,
            email=email.value,
            full_name=dto.full_name.strip(),
            password_hash=password_hash,
            role=role,
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=current_user.id if current_user else None
        )

        saved_user = self.user_repository.save(user)

        return UserResponseDTO.from_entity(saved_user)