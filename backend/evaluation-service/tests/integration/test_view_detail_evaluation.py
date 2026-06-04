import pytest

from unittest.mock import Mock, patch

from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.evaluation_factory import EvaluationFactory

from src.domain.exceptions import (
    EvaluationNotFoundError,
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

@patch(
    "src.application.use_cases.evaluation_detail.GetEvaluationUseCase.execute"
)
def test_evaluation_detail_success(
    mock_execute,
    api_client,
):
    evaluation = EvaluationFactory.build()
    evaluation.id = 1

    mock_execute.return_value = evaluation

    response = api_client.get(
        "/api/evaluations/1/"
    )

    assert response.status_code == (
        status.HTTP_200_OK
    )

    assert response.data["id"] == 1

    mock_execute.assert_called_once_with(1)

@patch(
    "src.application.use_cases.evaluation_detail.GetEvaluationUseCase.execute"
)
def test_evaluation_detail_not_found(
    mock_execute,
    api_client,
):
    mock_execute.side_effect = (
        EvaluationNotFoundError(1)
    )

    response = api_client.get(
        "/api/evaluations/1/"
    )

    assert response.status_code == (
        status.HTTP_404_NOT_FOUND
    )

    assert "error" in response.data

@patch(
    "src.application.use_cases.evaluation_detail.GetEvaluationUseCase.execute"
)
def test_evaluation_detail_unexpected_error(
    mock_execute,
    api_client,
):
    mock_execute.side_effect = (
        Exception("Unexpected")
    )

    response = api_client.get(
        "/api/evaluations/1/"
    )

    assert response.status_code == (
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    assert response.data["error"] == (
        "Error interno del servidor"
    )

def test_evaluation_detail_requires_admin_or_psychologist():
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
        "/api/evaluations/1/"
    )

    assert response.status_code == (
        status.HTTP_403_FORBIDDEN
    )