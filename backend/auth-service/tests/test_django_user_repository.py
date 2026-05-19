import pytest
from datetime import datetime

from src.infrastructure.repositories.django_user_repository import DjangoUserRepository
from src.domain.entities.user import User, UserRole, UserStatus
from authentication.models import UserModel


@pytest.mark.django_db
class TestDjangoUserRepository:

    @pytest.fixture
    def repository(self):
        return DjangoUserRepository()

    @pytest.fixture
    def sample_user(self):
        return User(
            id=None,
            email="teacher@paideia.com",
            full_name="Profesor Test",
            password_hash="hashed_password",
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=None
        )

    def test_save_user(self, repository, sample_user):
        """Debe guardar usuario en DB"""

        saved_user = repository.save(sample_user)

        assert saved_user.id is not None
        assert saved_user.email == "teacher@paideia.com"
        assert UserModel.objects.count() == 1

    def test_find_by_email(self, repository, sample_user):
        """Debe buscar por email"""

        repository.save(sample_user)

        found = repository.find_by_email("teacher@paideia.com")

        assert found is not None
        assert found.email == "teacher@paideia.com"

    def test_exists_by_email(self, repository, sample_user):
        """Debe verificar existencia"""

        repository.save(sample_user)

        exists = repository.exists_by_email("teacher@paideia.com")

        assert exists is True

    def test_find_all(self, repository, sample_user):
        """Debe listar usuarios"""

        repository.save(sample_user)

        users = repository.find_all()

        assert len(users) == 1
        assert users[0].email == "teacher@paideia.com"

    def test_deactivate_user(self, repository, sample_user):
        """RN-18: desactivar sin eliminar"""

        saved = repository.save(sample_user)

        result = repository.deactivate(saved.id)

        updated = repository.find_by_id(saved.id)

        assert result is True
        assert updated.status == UserStatus.INACTIVE
        assert UserModel.objects.count() == 1