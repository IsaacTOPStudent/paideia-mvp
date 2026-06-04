import pytest

from datetime import date
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import Mock

from tests.factories.observation_factory import ObservationFactory

from src.domain.exceptions import (
    StudentNotFoundError,
    InvalidObservationDataError,
    ExternalServiceError
)

@pytest.fixture
def api_client():
    client = APIClient()

    user = Mock()
    user.is_authenticated = True

    client.force_authenticate(
        user=user,
        token={
            "role": "TEACHER",
            "status": "ACTIVE",
            "user_id": 15,
        }
    )

    return client

@pytest.fixture
def valid_payload():
    return {
        "student_id": 1,
        "observation_date": str(date.today()),
        "subject": "MATH",
        "performance_description": (
            "Desempeño académico adecuado durante la clase"
        ),
        "behavioral_notes": (
            "Comportamiento apropiado durante la actividad"
        ),
        "pedagogical_adjustments_applied": (
            "Apoyo visual"
        ),
        "recommendations": (
            "Continuar seguimiento"
        ),
    }

@patch("evaluations.views.register_observation_use_case")
def test_register_observation_success(
    mock_use_case,
    api_client,
    valid_payload,
):
    observation = ObservationFactory.build()
    observation.id = 1

    mock_use_case.execute.return_value = (
        observation,
        None,
    )

    response = api_client.post(
        "/api/observations/register/",
        valid_payload,
        format="json",
    )

    assert response.status_code == (
        status.HTTP_201_CREATED
    )

    assert response.data["id"] == 1

    mock_use_case.execute.assert_called_once()

@patch("evaluations.views.register_observation_use_case")
def test_register_observation_with_warning(
    mock_use_case,
    api_client,
    valid_payload,
):
    observation = ObservationFactory.build()
    observation.id = 1

    warning = (
        "El estudiante no tiene diagnosticos NEE registrados"
    )

    mock_use_case.execute.return_value = (
        observation,
        warning,
    )

    response = api_client.post(
        "/api/observations/register/",
        valid_payload,
        format="json",
    )

    assert response.status_code == (
        status.HTTP_201_CREATED
    )

    assert response.data["warning"] == warning

def test_register_observation_invalid_serializer(
    api_client,
):
    response = api_client.post(
        "/api/observations/register/",
        {},
        format="json",
    )

    assert response.status_code == (
        status.HTTP_400_BAD_REQUEST
    )

    assert response.data["error"] == (
        "Datos de observación inválidos"
    )

@patch("evaluations.views.register_observation_use_case")
def test_register_observation_student_not_found(
    mock_use_case,
    api_client,
    valid_payload,
):
    mock_use_case.execute.side_effect = (
        StudentNotFoundError(1)
    )

    response = api_client.post(
        "/api/observations/register/",
        valid_payload,
        format="json",
    )

    assert response.status_code == (
        status.HTTP_404_NOT_FOUND
    )

@patch("evaluations.views.register_observation_use_case")
def test_register_observation_invalid_domain_data(
    mock_use_case,
    api_client,
    valid_payload,
):
    mock_use_case.execute.side_effect = (
        InvalidObservationDataError(
            "Error de dominio"
        )
    )

    response = api_client.post(
        "/api/observations/register/",
        valid_payload,
        format="json",
    )

    assert response.status_code == (
        status.HTTP_400_BAD_REQUEST
    )

    assert response.data["error"] == (
        "Error de dominio"
    )

@patch("evaluations.views.register_observation_use_case")
def test_register_observation_external_service_error(
    mock_use_case,
    api_client,
    valid_payload,
):
    mock_use_case.execute.side_effect = (
        ExternalServiceError(
            "student-service",
            "timeout",
        )
    )

    response = api_client.post(
        "/api/observations/register/",
        valid_payload,
        format="json",
    )

    assert response.status_code == (
        status.HTTP_503_SERVICE_UNAVAILABLE
    )

@patch("evaluations.views.register_observation_use_case")
def test_register_observation_unexpected_error(
    mock_use_case,
    api_client,
    valid_payload,
):
    mock_use_case.execute.side_effect = (
        Exception("Unexpected")
    )

    response = api_client.post(
        "/api/observations/register/",
        valid_payload,
        format="json",
    )

    assert response.status_code == (
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    assert response.data["error"] == (
        "Error interno del servidor"
    )

def test_register_observation_requires_teacher_role():
    client = APIClient()

    user = Mock()
    user.is_authenticated = True

    client.force_authenticate(
        user=user,
        token={
            "role": "PSYCHOLOGIST",
            "status": "ACTIVE",
        }
    )

    response = client.post(
        "/api/observations/register/",
        {},
        format="json",
    )

    assert response.status_code == (
        status.HTTP_403_FORBIDDEN
    )