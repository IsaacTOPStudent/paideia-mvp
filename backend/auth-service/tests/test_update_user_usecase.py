import pytest
from datetime import datetime
from unittest.mock import Mock

from src.application.use_cases.update_user import UpdateUserUseCase
from src.application.dtos.user_dto import UpdateUserDTO
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
    return UpdateUserUseCase(mock_repository)


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

def test_admin_can_update_full_name(use_case, mock_repository, admin_user, teacher_user):
    dto = UpdateUserDTO(
        user_id=2,
        full_name="Nuevo Nombre"
    )

    mock_repository.find_by_id.return_value = teacher_user
    mock_repository.save.return_value = teacher_user

    result = use_case.execute(dto=dto, current_user=admin_user)

    assert result.full_name == "Nuevo Nombre"
    mock_repository.find_by_id.assert_called_once_with(2)
    mock_repository.save.assert_called_once()

def test_admin_can_update_role(use_case, mock_repository, admin_user, teacher_user):
    dto = UpdateUserDTO(
        user_id=2,
        role="SECRETARY"
    )

    mock_repository.find_by_id.return_value = teacher_user
    mock_repository.save.return_value = teacher_user

    result = use_case.execute(dto=dto, current_user=admin_user)

    assert result.role == "SECRETARY"

def test_non_admin_cannot_update_user(use_case, teacher_user):
    dto = UpdateUserDTO(user_id=1, full_name="Hack")

    with pytest.raises(UnauthorizedOperationError):
        use_case.execute(dto=dto, current_user=teacher_user)

def test_update_nonexistent_user(use_case, mock_repository, admin_user):
    dto = UpdateUserDTO(user_id=999, full_name="Ghost")

    mock_repository.find_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        use_case.execute(dto=dto, current_user=admin_user)

def test_update_invalid_empty_name(use_case, mock_repository, admin_user, teacher_user):
    dto = UpdateUserDTO(
        user_id=2,
        full_name="   "
    )

    mock_repository.find_by_id.return_value = teacher_user

    with pytest.raises(InvalidUserDataError):
        use_case.execute(dto=dto, current_user=admin_user)

def test_update_invalid_role(use_case, mock_repository, admin_user, teacher_user):
    dto = UpdateUserDTO(
        user_id=2,
        role="SUPERADMIN"
    )

    mock_repository.find_by_id.return_value = teacher_user

    with pytest.raises(InvalidUserDataError):
        use_case.execute(dto=dto, current_user=admin_user)