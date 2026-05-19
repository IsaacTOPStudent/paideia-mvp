import pytest 
from datetime import datetime

from src.application.use_cases.create_user import CreateUserUseCase
from src.application.dtos.user_dto import CreateUserDTO
from src.domain.entities.user import User, UserRole, UserStatus
from src.domain.exceptions import UnauthorizedOperationError, UserAlreadyExistsError, InvalidUserDataError

def test_admin_can_create_user(mock_user_repository, password_hasher, admin_user):

    use_case = CreateUserUseCase(mock_user_repository, password_hasher)

    dto = CreateUserDTO(
        email="teacher@paideia.com",
        full_name="Profesor Test",
        password="12345678",
        role="TEACHER"
    )

    saved_user = User(
        id=2,
        email=dto.email,
        full_name=dto.full_name,
        password_hash="hashed",
        role=UserRole.TEACHER,
        status=UserStatus.ACTIVE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=admin_user.id
    )

    mock_user_repository.exists_by_email.return_value = False
    mock_user_repository.save.return_value = saved_user

    result = use_case.execute(dto, admin_user)

    assert result.email == dto.email
    assert result.role == "TEACHER"
    assert result.created_by == admin_user.id

def test_non_admin_cannot_create_user(mock_user_repository, password_hasher):
    """
        Only admin can create users
    """

    non_admin = User(
        id=2,
        email="teacher@paideia.com",
        full_name="Profesor",
        password_hash="hashed",
        role=UserRole.TEACHER,
        status=UserStatus.ACTIVE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=None
    )

    use_case = CreateUserUseCase(mock_user_repository, password_hasher)

    dto = CreateUserDTO(
        email="new@paideia.com",
        full_name="Nuevo usuario",
        password="12345678",
        role="TEACHER"
    )

    with pytest.raises(UnauthorizedOperationError):
        use_case.execute(dto, non_admin)

def test_cannot_create_user_with_existing_email(mock_user_repository, password_hasher, admin_user):
    """RN-02: email único"""

    use_case = CreateUserUseCase(mock_user_repository, password_hasher)

    dto = CreateUserDTO(
        email="existing@paideia.com",
        full_name="Usuario Existente",
        password="12345678",
        role="TEACHER"
    )

    mock_user_repository.exists_by_email.return_value = True

    with pytest.raises(UserAlreadyExistsError):
        use_case.execute(dto, admin_user)

def test_cannot_create_user_with_invalid_data(mock_user_repository, password_hasher, admin_user):
    """RN-17: campos obligatorios"""

    use_case = CreateUserUseCase(mock_user_repository, password_hasher)

    dto = CreateUserDTO(
        email="invalid@paideia.com",
        full_name="",
        password="123",
        role="TEACHER"
    )

    mock_user_repository.exists_by_email.return_value = False

    with pytest.raises(InvalidUserDataError):
        use_case.execute(dto, admin_user)

def test_cannot_create_user_with_invalid_role(mock_user_repository, password_hasher, admin_user):
    """Rol inválido"""

    use_case = CreateUserUseCase(mock_user_repository, password_hasher)

    dto = CreateUserDTO(
        email="user@paideia.com",
        full_name="Usuario Test",
        password="12345678",
        role="INVALID_ROLE"
    )

    mock_user_repository.exists_by_email.return_value = False

    with pytest.raises(InvalidUserDataError):
        use_case.execute(dto, admin_user)

