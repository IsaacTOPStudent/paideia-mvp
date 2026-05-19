from rest_framework import serializers
from typing import cast, Any
from .models import UserModel 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed

class UserCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new user.
    """

    email = serializers.EmailField(required=True)
    full_name = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    role = serializers.ChoiceField(
        choices=['ADMIN', 'PSYCHOLOGIST', 'TEACHER', 'SECRETARY'], 
        required=True
    )
    def validate_email(self, value):
        """
        validate email format
        """
        return value.lower().strip()
    
    def validate_full_name(self, value):
        """
        Validate full name is not empty
        """

        if not value.strip():
            raise serializers.ValidationError("El nombre completo no puede estar vacío")
        return value.strip()


class UserUpdateSerializer(serializers.Serializer):
    """
    Serializer to update user
    """

    full_name = serializers.CharField(max_length=255, required=False)
    role = serializers.ChoiceField(
        choices=['ADMIN', 'PSYCHOLOGIST', 'TEACHER', 'SECRETARY'], 
        required=False
    )

class UserResponseSerializer(serializers.Serializer):
    """
    Serializer for user response
    """

    role_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    id = serializers.IntegerField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
    role = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    created_by = serializers.IntegerField(allow_null=True)

    role_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()


    def get_role_display(self, obj: Any):
        role = obj["role"] if isinstance(obj, dict) else obj.role

        role_map = {            
            'ADMIN': 'Administrador',
            'PSYCHOLOGIST': 'Psicólogo',
            'TEACHER': 'Docente',
            'SECRETARY': 'Secretaria'
        }
        return role_map.get(role, role)

    def get_status_display(self, obj):
        status = obj["status"] if isinstance(obj, dict) else obj.status

        status_map = {
            'ACTIVE': 'Activo',
            'INACTIVE': 'Inactivo'
        }
        return status_map.get(status, status)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
        Custom serializer for login JWT.
        Return access + refresh + basic information from user
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Custom claims
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name

        return token

    def validate(self, attrs):
        data: dict[str, Any] = dict(super().validate(attrs))

        user = cast(UserModel, self.user)

        if not user:
            raise AuthenticationFailed('Credenciales inválidas')

        if user.status == 'INACTIVE':
            raise AuthenticationFailed('El usuario está inactivo')

        #Custom answer
        data['user'] = {
            'id':getattr(user, 'id', None),
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
        }

        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()