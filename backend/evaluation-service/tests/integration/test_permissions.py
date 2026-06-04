import pytest
from unittest.mock import Mock

from evaluations.permissions import (
    IsAdminOrPsychologist,
    IsAdminPsychologistOrTeacher,
    IsPsychologist,
    IsTeacher,
    UserStatus,
)

@pytest.fixture
def mock_authenticated_request():
    request = Mock()
    request.user = Mock(is_authenticated=True)
    return request


def test_is_psychologist_allows_active_psychologist(mock_authenticated_request):
    mock_authenticated_request.auth = {
        "role": "PSYCHOLOGIST",
        "status": UserStatus.ACTIVE,
    }

    assert IsPsychologist().has_permission(mock_authenticated_request, None)


def test_is_psychologist_denies_non_psychologist(mock_authenticated_request):
    mock_authenticated_request.auth = {
        "role": "TEACHER",
        "status": UserStatus.ACTIVE,
    }

    assert not IsPsychologist().has_permission(mock_authenticated_request, None)


def test_is_teacher_allows_teacher(mock_authenticated_request):
    mock_authenticated_request.auth = {
        "role": "TEACHER",
        "status": UserStatus.ACTIVE,
    }

    assert IsTeacher().has_permission(mock_authenticated_request, None)


def test_admin_or_psychologist_allows_admin(mock_authenticated_request):
    mock_authenticated_request.auth = {
        "role": "ADMIN",
        "status": UserStatus.ACTIVE,
    }

    assert IsAdminOrPsychologist().has_permission(mock_authenticated_request, None)


def test_admin_psychologist_or_teacher_blocks_inactive(mock_authenticated_request):
    mock_authenticated_request.auth = {
        "role": "TEACHER",
        "status": UserStatus.INACTIVE,
    }

    assert not IsAdminPsychologistOrTeacher().has_permission(mock_authenticated_request, None)
