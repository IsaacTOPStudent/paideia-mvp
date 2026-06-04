import pytest
from unittest.mock import Mock, patch

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.observation_factory import ObservationFactory

from src.domain.exceptions import (
    ObservationNotFoundError,
    ObservationAccessDeniedError,
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
            "user_id": 15, # ID simulado del docente
        }
    )

    return client

@patch(
    "src.application.use_cases.observation_detail.GetObservationUseCase.execute"
)
def test_observation_detail_success(
    mock_execute,
    api_client_teacher,
):
    observation = ObservationFactory.build()
    observation.id = 1

    mock_execute.return_value = observation

    response = api_client_teacher.get(
        "/api/observations/1/"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == 1

    mock_execute.assert_called_once_with(
        observation_id=1, 
        requester_id=15, 
        requester_role="TEACHER"
    )


@patch(
    "src.application.use_cases.observation_detail.GetObservationUseCase.execute"
)
def test_observation_detail_not_found(
    mock_execute,
    api_client_teacher,
):
    mock_execute.side_effect = ObservationNotFoundError(1)

    response = api_client_teacher.get(
        "/api/observations/1/"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "error" in response.data


@patch(
    "src.application.use_cases.observation_detail.GetObservationUseCase.execute"
)
def test_observation_detail_access_denied_by_domain_rule(
    mock_execute,
    api_client_teacher,
):

    mock_execute.side_effect = ObservationAccessDeniedError()

    response = api_client_teacher.get(
        "/api/observations/1/"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "error" in response.data


@patch(
    "src.application.use_cases.observation_detail.GetObservationUseCase.execute"
)
def test_observation_detail_unexpected_error(
    mock_execute,
    api_client_teacher,
):
    mock_execute.side_effect = Exception("Unexpected database failure")

    response = api_client_teacher.get(
        "/api/observations/1/"
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data["error"] == "Error interno del servidor"


def test_observation_detail_requires_admin_psychologist_or_teacher():

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

    response = client.get(
        "/api/observations/1/"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN