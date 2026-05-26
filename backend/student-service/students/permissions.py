from rest_framework.permissions import BasePermission 
from rest_framework.exceptions import PermissionDenied

class UserRole: 
    ADMIN = 'ADMIN'
    PSYCHOLOGIST = 'PSYCHOLOGIST'
    SECRETARY = 'SECRETARY'
    TEACHER = 'TEACHER'

class UserStatus:
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'

class BaseRolePermission(BasePermission):
    allowed_roles: list[str] = []

    def has_permission(self, request, view) -> bool: # type: ignore
        if not request.user or not request.user.is_authenticated or not request.auth:
            return False 
        
        token_payload = request.auth

        user_role = token_payload.get('role')
        user_status = token_payload.get('status', UserStatus.INACTIVE)

        return bool(
            user_role in self.allowed_roles and
            user_status == UserStatus.ACTIVE
        )


class IsAdmin(BaseRolePermission):
    allowed_roles = [UserRole.ADMIN]
    message = "Acceso denegado. Se requieren permisos de Administrador."


class IsPsychologist(BaseRolePermission):
    allowed_roles = [UserRole.PSYCHOLOGIST]
    message = "Acceso denegado. Se requieren permisos de Psicología."

class IsSecretary(BaseRolePermission):
    allowed_roles = [UserRole.SECRETARY]
    message = "Tu rol no tiene permisos para realizar esta acción. Acceso exclusivo para Secretaría."

class IsTeacher(BaseRolePermission):
    allowed_roles = [UserRole.TEACHER]
    message = "Acceso denegado. Se requieren permisos de Docente."


class IsAdminOrPsychologist(BaseRolePermission):
    allowed_roles = [
        UserRole.ADMIN,
        UserRole.PSYCHOLOGIST
    ]    
    message = "Acceso denegado. Requiere rol de Administrador o Psicología."

class IsAdminPsychologistOrTeacher(BaseRolePermission):
    allowed_roles = [
        UserRole.ADMIN,
        UserRole.PSYCHOLOGIST,
        UserRole.TEACHER
    ]

    message =  "No tienes autorización para consultar caracterizaciones"
        
    


