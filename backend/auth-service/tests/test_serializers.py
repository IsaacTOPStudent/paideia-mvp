import pytest
from authentication.serializers import (
    UserCreateSerializer,
    UserResponseSerializer
)
from src.application.dtos.user_dto import UserResponseDTO
from datetime import datetime
from typing import cast, Any
from dataclasses import asdict

def test_create_user_serializer_valid_data():
    payload = {
        "email": "user@test.com",
        "full_name": "Usuario Test",
        "password": "Password123*",
        "role": "PSYCHOLOGIST"
    }

    serializer = UserCreateSerializer(data=payload)

    assert serializer.is_valid()


def test_create_user_serializer_invalid_email():
    payload = {
        "email": "correo-invalido",
        "full_name": "Usuario Test",
        "password": "Password123*",
        "role": "PSYCHOLOGIST"
    }

    serializer = UserCreateSerializer(data=payload)

    assert not serializer.is_valid()
    assert "email" in serializer.errors

def test_create_user_serializer_invalid_role():
    payload = {
        "email": "user@test.com",
        "full_name": "Usuario Test",
        "password": "Password123*",
        "role": "INVALID_ROLE"
    }

    serializer = UserCreateSerializer(data=payload)

    assert not serializer.is_valid()
    assert "role" in serializer.errors

def test_create_user_serializer_required_fields():
    serializer = UserCreateSerializer(data={})

    assert not serializer.is_valid()
    assert "email" in serializer.errors
    assert "password" in serializer.errors
    assert "full_name" in serializer.errors

def test_user_response_serializer():
    dto = UserResponseDTO(
        id=1,
        email="user@test.com",
        full_name="Usuario Test",
        role="ADMIN",
        status="ACTIVE",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=1
    )

    serializer = UserResponseSerializer(dto.__dict__)

    data = cast(dict[str, Any], serializer.data)

    assert data["email"] == "user@test.com"
    assert data["role"] == "ADMIN"
    assert data["status"] == "ACTIVE"