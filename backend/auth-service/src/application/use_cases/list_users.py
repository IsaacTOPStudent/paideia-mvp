from typing import List
from ...domain.entities.user import User
from ...domain.ports.user_repository import UserRepository
from ...domain.exceptions import UnauthorizedOperationError
from ..dtos.user_dto import UserResponseDTO

class ListUsersUseCase:
    """
    Use Case: List users (CU-02)

    Requirements:
    - RF-02: Manage users and basic roles
    - RN-01: Only admin can list users
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, current_user: User, include_inactive: bool = False) ->  List[UserResponseDTO]:
        """
        Execute Use Case

        Args:
        current_user: User executing the action (for RN-01)
        include_inactive: Whether to include inactive users in the list

        Returns:
        List of UserResponseDTO with the users

        Raises:
        UnauthorizedOperationError: If not Admin
        """

        #Validation RN-01: Only Admin can list users
        if not current_user.can_manage_users():
            raise UnauthorizedOperationError(
                operation="listar usuarios",
                role=current_user.role.to_spanish()
            )
        
        if include_inactive:
            users = self.user_repository.find_all()
        else: 
            users = self.user_repository.find_all_active()

        return [UserResponseDTO.from_entity(user) for user in users]