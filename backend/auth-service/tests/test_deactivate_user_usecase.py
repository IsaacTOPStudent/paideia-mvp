import pytest
from datetime import datetime
from unittest.mock import Mock

from src.application.use_cases.deactivate_user import DeactivateUserUseCase
from src.domain.entities.user import User, UserRole, UserStatus
from src.domain.exceptions import (
    UnauthorizedOperationError,
    UserNotFoundError,
    InvalidUserDataError
)

@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def use_case(mock_repository):
    return DeactivateUserUseCase(mock_repository)


@pytest.fixture
def admin_user():
    return User(
        id=1,
        email="admin@test.com",
        full_name="Administrador",
        password_hash="hashed",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=None
    )


@pytest.fixture
def teacher_user():
    return User(
        id=2,
        email="teacher@test.com",
        full_name="Profesor",
        password_hash="hashed",
        role=UserRole.TEACHER,
        status=UserStatus.ACTIVE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=1
    )

def test_admin_can_deactivate_user(use_case, mock_repository, admin_user, teacher_user):
    mock_repository.find_by_id.return_value = teacher_user
    mock_repository.save.return_value = teacher_user

    result = use_case.execute(user_id=2, current_user=admin_user)

    assert result.id == 2
    assert result.status == "INACTIVE"
    mock_repository.find_by_id.assert_called_once_with(2)
    mock_repository.save.assert_called_once()

def test_non_admin_cannot_deactivate_user(use_case, teacher_user):
    with pytest.raises(UnauthorizedOperationError):
        use_case.execute(user_id=1, current_user=teacher_user)

def test_deactivate_nonexistent_user(use_case, mock_repository, admin_user):
    mock_repository.find_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        use_case.execute(user_id=999, current_user=admin_user)

def test_admin_cannot_deactivate_self(use_case, mock_repository, admin_user):
    mock_repository.find_by_id.return_value = admin_user

    with pytest.raises(InvalidUserDataError):
        use_case.execute(user_id=1, current_user=admin_user)

