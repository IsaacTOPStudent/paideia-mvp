from dataclasses import dataclass
from datetime import datetime 
from typing import Optional

@dataclass
class CreateUserDTO:
    """create user DTO"""
    email: str
    full_name: str
    password: str
    role: str
    created_by: Optional[int] = None

@dataclass
class UpdateUserDTO:
    """Update user DTO"""
    user_id: int
    full_name: Optional[str] = None 
    role: Optional[str] = None 
    updated_by: Optional[int] = None

@dataclass
class UserResponseDTO:
    """User response DTO"""
    id: int 
    email: str
    full_name: str
    role: str
    status: str
    created_at: datetime
    updated_at: datetime 
    created_by: Optional[int] = None

    @classmethod
    def from_entity(cls, user):
        """
        Change entity user to DTO
        """

        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            status=user.status.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
            created_by=(
                user.created_by.id
                if hasattr(user.created_by, "id")
                else user.created_by
            )
        )