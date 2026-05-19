import pytest 
from datetime import datetime
from src.domain.entities.user import User, UserRole, UserStatus

@pytest.fixture
def active_admin():
    return User(
        id=1,
        email="admin@paideia.com",
        full_name="Admin",
        password_hash="hashed",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=None
    )


@pytest.fixture
def active_teacher():
    return User(
        id=2,
        email="teacher@paideia.com",
        full_name="Teacher",
        password_hash="hashed",
        role=UserRole.TEACHER,
        status=UserStatus.ACTIVE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=1
    )


def test_admin_can_manage_users(active_admin):
    """RN-01: administrador puede gestionar usuarios"""
    assert active_admin.can_manage_users() is True
    assert active_admin.can_create_users() is True


def test_teacher_cannot_manage_users(active_teacher):
    """RN-01: docente no puede gestionar usuarios"""
    assert active_teacher.can_manage_users() is False
    assert active_teacher.can_create_users() is False


def test_user_can_be_deactivated(active_teacher):
    """RN-18: usuario se desactiva (soft delete)"""
    active_teacher.deactivate()

    assert active_teacher.status == UserStatus.INACTIVE
    assert active_teacher.is_active() is False


def test_user_can_be_reactivated(active_teacher):
    active_teacher.deactivate()
    active_teacher.reactivate()

    assert active_teacher.status == UserStatus.ACTIVE
    assert active_teacher.is_active() is True


def test_teacher_can_register_observations(active_teacher):
    assert active_teacher.can_register_observations() is True


def test_teacher_cannot_generate_reports(active_teacher):
    assert active_teacher.can_generate_reports() is False