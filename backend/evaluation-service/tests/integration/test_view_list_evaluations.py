import pytest

from unittest.mock import Mock, patch

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.evaluation_factory import EvaluationFactory

from src.domain.exceptions import (
    StudentNotFoundError,
    ExternalServiceError,
)

@pytest.fixture
def api_client():
    client = APIClient()

    user = Mock()
    user.is_authenticated = True

    client.force_authenticate(
        user=user,
        token={
            "role": "PSYCHOLOGIST",
            "status": "ACTIVE",
            "user_id": 10,
        }
    )

    return client

@patch("evaluations.views.list_evaluations_use_case")
def test_evaluation_list_success(
    mock_use_case,
    api_client,
):
    evaluations = [
        EvaluationFactory.build(),
        EvaluationFactory.build(),
    ]

    mock_use_case.execute.return_value = evaluations

    response = api_client.get(
        "/api/evaluations/",
        {"student_id": 1},
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["student_id"] == 1
    assert response.data["count"] == 2
    assert len(response.data["results"]) == 2

    mock_use_case.execute.assert_called_once_with(1)

def test_evaluation_list_requires_student_id(
    api_client,
):
    response = api_client.get(
        "/api/evaluations/"
    )

    assert response.status_code == (
        status.HTTP_400_BAD_REQUEST
    )

    assert "error" in response.data

def test_evaluation_list_invalid_student_id(
    api_client,
):
    response = api_client.get(
        "/api/evaluations/",
        {"student_id": "abc"},
    )

    assert response.status_code == (
        status.HTTP_400_BAD_REQUEST
    )

    assert "error" in response.data

@patch("evaluations.views.list_evaluations_use_case")
def test_evaluation_list_student_not_found(
    mock_use_case,
    api_client,
):
    mock_use_case.execute.side_effect = (
        StudentNotFoundError(1)
    )

    response = api_client.get(
        "/api/evaluations/",
        {"student_id": 1},
    )

    assert response.status_code == (
        status.HTTP_404_NOT_FOUND
    )

    assert "error" in response.data

@patch("evaluations.views.list_evaluations_use_case")
def test_evaluation_list_external_service_error(
    mock_use_case,
    api_client,
):
    mock_use_case.execute.side_effect = (
        ExternalServiceError(
            "student-service",
            "timeout"
        )
    )

    response = api_client.get(
        "/api/evaluations/",
        {"student_id": 1},
    )

    assert response.status_code == (
        status.HTTP_503_SERVICE_UNAVAILABLE
    )

@patch("evaluations.views.list_evaluations_use_case")
def test_evaluation_list_unexpected_error(
    mock_use_case,
    api_client,
):
    mock_use_case.execute.side_effect = (
        Exception("Unexpected")
    )

    response = api_client.get(
        "/api/evaluations/",
        {"student_id": 1},
    )

    assert response.status_code == (
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    assert response.data["error"] == (
        "Error interno del servidor"
    )

def test_evaluation_list_requires_admin_or_psychologist():
    client = APIClient()

    user = Mock()
    user.is_authenticated = True

    client.force_authenticate(
        user=user,
        token={
            "role": "TEACHER",
            "status": "ACTIVE",
        }
    )

    response = client.get(
        "/api/evaluations/",
        {"student_id": 1},
    )

    assert response.status_code == (
        status.HTTP_403_FORBIDDEN
    )