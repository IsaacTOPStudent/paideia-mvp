import pytest
from unittest.mock import Mock, patch

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.observation_factory import ObservationFactory

from src.domain.exceptions import (
    StudentNotFoundError,
    ExternalServiceError,
)

@pytest.fixture
def api_client_teacher():
    client = APIClient()

    user = Mock()
    user.is_authenticated = True

    client.force_authenticate(
        user=user,
        token={
            "role": "TEACHER",
            "status": "ACTIVE",
            "user_id": 10,
        }
    )

    return client


@pytest.fixture
def api_client_psychologist():
    client = APIClient()

    user = Mock()
    user.is_authenticated = True

    client.force_authenticate(
        user=user,
        token={
            "role": "PSYCHOLOGIST",
            "status": "ACTIVE",
            "user_id": 5,
        }
    )

    return client

@patch("evaluations.views.list_observations_use_case")
@patch("evaluations.views._get_token_data")
def test_observation_list_success(
    mock_token,
    mock_use_case,
    api_client_teacher,
):
    mock_token.return_value = (
        10,
        "TEACHER"
    )

    observations = [
        ObservationFactory.build(),
        ObservationFactory.build(),
    ]

    mock_use_case.execute.return_value = (
        observations
    )

    response = api_client_teacher.get(
        "/api/observations/",
        {"student_id": 1},
    )

    assert response.status_code == (
        status.HTTP_200_OK
    )

    assert response.data["student_id"] == 1
    assert response.data["count"] == 2
    assert len(response.data["results"]) == 2

    mock_use_case.execute.assert_called_once_with(
        student_id=1,
        requester_id=10,
        requester_role="TEACHER",
    )

def test_observation_list_requires_student_id(
    api_client_teacher,
):
    response = api_client_teacher.get(
        "/api/observations/"
    )

    assert response.status_code == (
        status.HTTP_400_BAD_REQUEST
    )

    assert (
        response.data["error"]
        == "El parámetro 'student_id' es requerido"
    )

def test_observation_list_invalid_student_id(
    api_client_teacher,
):
    response = api_client_teacher.get(
        "/api/observations/",
        {"student_id": "abc"},
    )

    assert response.status_code == (
        status.HTTP_400_BAD_REQUEST
    )

    assert (
        response.data["error"]
        == "'student_id' debe ser un número entero válido"
    )

@patch("evaluations.views.list_observations_use_case")
@patch("evaluations.views._get_token_data")
def test_observation_list_student_not_found(
    mock_token,
    mock_use_case,
    api_client_teacher,
):
    mock_token.return_value = (
        10,
        "TEACHER"
    )

    mock_use_case.execute.side_effect = (
        StudentNotFoundError(1)
    )

    response = api_client_teacher.get(
        "/api/observations/",
        {"student_id": 1},
    )

    assert response.status_code == (
        status.HTTP_404_NOT_FOUND
    )

@patch("evaluations.views.list_observations_use_case")
@patch("evaluations.views._get_token_data")
def test_observation_list_external_service_error(
    mock_token,
    mock_use_case,
    api_client_teacher,
):
    mock_token.return_value = (
        10,
        "TEACHER"
    )

    mock_use_case.execute.side_effect = (
        ExternalServiceError(
            "student-service",
            "timeout",
        )
    )

    response = api_client_teacher.get(
        "/api/observations/",
        {"student_id": 1},
    )

    assert response.status_code == (
        status.HTTP_503_SERVICE_UNAVAILABLE
    )

@patch("evaluations.views.list_observations_use_case")
@patch("evaluations.views._get_token_data")
def test_observation_list_unexpected_error(
    mock_token,
    mock_use_case,
    api_client_teacher,
):
    mock_token.return_value = (
        10,
        "TEACHER"
    )

    mock_use_case.execute.side_effect = (
        Exception("Unexpected")
    )

    response = api_client_teacher.get(
        "/api/observations/",
        {"student_id": 1},
    )

    assert response.status_code == (
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )

def test_observation_list_requires_valid_role():
    client = APIClient()

    user = Mock()
    user.is_authenticated = True

    client.force_authenticate(
        user=user,
        token={
            "role": "SECRETARY",
            "status": "ACTIVE",
        }
    )

    response = client.get(
        "/api/observations/",
        {"student_id": 1},
    )

    assert response.status_code == (
        status.HTTP_403_FORBIDDEN
    )

@patch("evaluations.views.list_observations_use_case")
@patch("evaluations.views._get_token_data")
def test_observation_list_psychologist_success(
    mock_token,
    mock_use_case,
    api_client_psychologist,
):
    mock_token.return_value = (
        5,
        "PSYCHOLOGIST"
    )

    mock_use_case.execute.return_value = [
        ObservationFactory.build()
    ]

    response = api_client_psychologist.get(
        "/api/observations/",
        {"student_id": 1},
    )

    assert response.status_code == (
        status.HTTP_200_OK
    )

    mock_use_case.execute.assert_called_once_with(
        student_id=1,
        requester_id=5,
        requester_role="PSYCHOLOGIST",
    )