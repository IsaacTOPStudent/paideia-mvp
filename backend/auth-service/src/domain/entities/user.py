from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class UserRole(Enum):
    ADMIN = "ADMIN"
    PSYCHOLOGIST = "PSYCHOLOGIST"
    TEACHER = "TEACHER"
    SECRETARY = "SECRETARY"

    @classmethod
    def from_str(cls, role: str):
        """
        Convert a string to a UserRole enum member.
        """
        try:
            return cls[role.upper()]
        except KeyError:
            raise ValueError(f"Invalid role: {role}")
        
    def to_spanish(self) -> str:
        """
        Convert the UserRole to its Spanish equivalent.
        """

        traslations = {
            'ADMIN': 'Administrador',
            'PSYCHOLOGIST': 'Psicólogo',
            'TEACHER': 'Docente',
            'SECRETARY': 'Secretaria'
        }
        return traslations[self.name]

class UserStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

    @classmethod
    def from_str(cls, status: str):
        """
        Convert a string to a UserStatus enum member.
        """
        try:
            return cls[status.upper()]
        except KeyError:
            raise ValueError(f"Invalid status: {status}")

@dataclass
class User:
    id: Optional[int]
    email: str
    full_name: str 
    password_hash: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]

    def __post_init__(self):
        if isinstance(self.role, str):
            self.role = UserRole.from_str(self.role)
        if isinstance(self.status, str):
            self.status = UserStatus.from_str(self.status)

    #--- Domain Logic Methods ---#
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE
    
    def can_manage_users(self) -> bool:
        return self.role == UserRole.ADMIN and self.is_active()
    
    def can_create_users(self) -> bool:
        return self.can_manage_users()
    
    def can_characterize_students(self) -> bool:
        return self.role == UserRole.PSYCHOLOGIST and self.is_active()
    
    def can_register_students(self) -> bool:
        return self.role in [UserRole.SECRETARY, UserRole.ADMIN] and self.is_active()
    
    def can_register_evaluations(self) -> bool:
        return self.role == UserRole.PSYCHOLOGIST and self.is_active()
    
    def can_register_observations(self) -> bool:
        return self.role == UserRole.TEACHER and self.is_active()
    
    def can_generate_reports(self) -> bool:
        return self.role == UserRole.PSYCHOLOGIST and self.is_active()
    
    def can_manage_catalog(self) -> bool:
        return self.role == UserRole.ADMIN and self.is_active()
    
    def deactivate(self) -> None:
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.now()

    def reactivate(self) -> None:
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.now()

    def update_info(self, full_name: Optional[str] = None, role: Optional[UserRole] = None) -> None:
        if full_name:
            self.full_name = full_name
        if role:
            self.role = role
        self.updated_at = datetime.now()

    def __str__(self):
        return f"User ({self.email}, {self.role.value}, {self.status.value})"
    
    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.id == other.id if self.id and other.id else self.email == other.email 