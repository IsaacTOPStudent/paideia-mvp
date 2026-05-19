import pytest
from datetime import datetime
from unittest.mock import Mock

from src.application.use_cases.list_users import ListUsersUseCase
from src.domain.entities.user import User, UserRole, UserStatus
from src.domain.exceptions import UnauthorizedOperationError

@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def use_case(mock_repository):
    return ListUsersUseCase(mock_repository)


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
        full_name="Docente",
        password_hash="hashed",
        role=UserRole.TEACHER,
        status=UserStatus.ACTIVE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=1
    )


@pytest.fixture
def inactive_user():
    return User(
        id=3,
        email="inactive@test.com",
        full_name="Inactivo",
        password_hash="hashed",
        role=UserRole.SECRETARY,
        status=UserStatus.INACTIVE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=1
    )

def test_admin_can_list_active_users(use_case, mock_repository, admin_user, teacher_user):
    mock_repository.find_all_active.return_value = [teacher_user]

    result = use_case.execute(current_user=admin_user)

    assert len(result) == 1
    assert result[0].email == "teacher@test.com"
    mock_repository.find_all_active.assert_called_once()

def test_admin_can_list_all_users(use_case, mock_repository, admin_user, teacher_user, inactive_user):
    mock_repository.find_all.return_value = [teacher_user, inactive_user]

    result = use_case.execute(current_user=admin_user, include_inactive=True)

    assert len(result) == 2
    assert result[1].status == "INACTIVE"
    mock_repository.find_all.assert_called_once()

def test_non_admin_cannot_list_users(use_case, teacher_user):
    with pytest.raises(UnauthorizedOperationError):
        use_case.execute(current_user=teacher_user)

def test_list_empty_users(use_case, mock_repository, admin_user):
    mock_repository.find_all_active.return_value = []

    result = use_case.execute(current_user=admin_user)

    assert result == []

