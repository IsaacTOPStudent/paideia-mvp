import pytest 
from unittest.mock import Mock

from src.infrastructure.adapters.password_hasher import DjangoPasswordHasher
from src.domain.entities.user import User, UserRole, UserStatus
from datetime import datetime 

@pytest.fixture
def mock_user_repository():
    return Mock()

@pytest.fixture
def password_hasher():
    return DjangoPasswordHasher()

@pytest.fixture
def admin_user():
    return User(
        id=1,
        email="admin@paideia.com",
        full_name='Administrador',
        password_hash="hashed",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=None
    )