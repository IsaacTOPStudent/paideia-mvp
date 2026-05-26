import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_user_psychologist():
    user = Mock()
    user.is_authenticated = True
    user.id = 5
    user.role = "PSYCHOLOGIST"
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
def mock_jwt_token_admin():
    return {
        "user_id": 1,
        "role": "ADMIN",
        "status": "ACTIVE",
    }