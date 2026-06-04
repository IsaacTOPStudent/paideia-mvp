import pytest 
from unittest.mock import Mock, patch

from rest_framework import status
from rest_framework.test import APIClient

from src.application.dtos.longitudinal_history_dto import LongitudinalHistoryResult

from src.domain.exceptions import (
    StudentNotFoundError,
    ExternalServiceError,
)

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
            "user_id": 10,
        }
    )

    return client

@patch("evaluations.views.get_longitudinal_history_use_case.execute")
def test_longitudinal_history_success(
    mock_execute,
    api_client_psychologist,
):

    mock_history_result = LongitudinalHistoryResult(
        student_id=1,
        student_info={"id": 1, "full_name": "Juan Pérez"},
        characterizations=[{"diagnostic_name": "TEA Grado 1"}],
        follow_up_status="Al día",
        days_until_next_evaluation=15,
        evaluations=[],  
        observations=[],
        total_evaluations=0,
        total_observations=0,
        has_records=True
    )

    mock_execute.return_value = mock_history_result

    response = api_client_psychologist.get("/api/longitudinal_history/1/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["student_id"] == 1
    assert response.data["has_records"] is True
    assert "evaluations" in response.data
    assert "observations" in response.data

    mock_execute.assert_called_once_with(
        student_id=1,
        requester_role="PSYCHOLOGIST"
    )

@patch("evaluations.views.get_longitudinal_history_use_case.execute")
def test_longitudinal_history_student_not_found(
    mock_execute,
    api_client_psychologist,
):
    mock_execute.side_effect = StudentNotFoundError(1)

    response = api_client_psychologist.get("/api/longitudinal_history/1/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "error" in response.data
    assert response.data["suggestion"] == "Verifique el número de documento del estudiante"

@patch("evaluations.views.get_longitudinal_history_use_case.execute")
def test_longitudinal_history_external_service_error(
    mock_execute,
    api_client_psychologist,
):
    mock_execute.side_effect = ExternalServiceError("student-service", "student-service no responde")

    response = api_client_psychologist.get("/api/longitudinal_history/1/")

    assert response.status_code in [status.HTTP_502_BAD_GATEWAY, status.HTTP_503_SERVICE_UNAVAILABLE]

@patch("evaluations.views.get_longitudinal_history_use_case.execute")
def test_longitudinal_history_unexpected_error(
    mock_execute,
    api_client_psychologist,
):
    mock_execute.side_effect = Exception("Fallo catastrófico en la base de datos")

    response = api_client_psychologist.get("/api/longitudinal_history/1/")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data["error"] == "Error interno del servidor"

def test_longitudinal_history_requires_allowed_roles():

    client = APIClient()

    user = Mock()
    user.is_authenticated = True

    client.force_authenticate(
        user=user,
        token={
            "role": "SECRETARY",
            "status": "ACTIVE",
            "user_id": 99,
        }
    )

    response = client.get("/api/longitudinal_history/1/")

    assert response.status_code == status.HTTP_403_FORBIDDEN