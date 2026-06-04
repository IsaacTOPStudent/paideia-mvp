import pytest
from unittest.mock import Mock
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def mock_user_psychologist():
    user = Mock()
    user.is_authenticated = True
    user.id = 5
    user.role = "PSYCHOLOGIST"
    user.status = "ACTIVE"
    return user


@pytest.fixture
def mock_user_teacher():
    user = Mock()
    user.is_authenticated = True
    user.id = 7
    user.role = "TEACHER"
    user.status = "ACTIVE"
    return user


@pytest.fixture
def mock_user_admin():
    user = Mock()
    user.is_authenticated = True
    user.id = 1
    user.role = "ADMIN"
    user.status = "ACTIVE"
    return user


@pytest.fixture
def mock_jwt_token_psychologist():
    return {
        "user_id": 5,
        "role": "PSYCHOLOGIST",
        "status": "ACTIVE",
    }


@pytest.fixture
def mock_jwt_token_teacher():
    return {
        "user_id": 7,
        "role": "TEACHER",
        "status": "ACTIVE",
    }


@pytest.fixture
def mock_jwt_token_admin():
    return {
        "user_id": 1,
        "role": "ADMIN",
        "status": "ACTIVE",
    }
