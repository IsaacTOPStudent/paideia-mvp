import pytest
from datetime import date, timedelta
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import Mock

from tests.factories.evaluation_factory import EvaluationFactory
from src.domain.exceptions import (
    StudentNotFoundError,
    StudentNotCharacterizedError,
    InvalidEvaluationDataError,
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

@pytest.fixture
def valid_payload():
    return {
        "student_id": 1,
        "evaluation_date": str(date.today()),
        "instrument_used": "WISC-V",
        "findings": "Hallazgos suficientemente extensos",
        "recommendations": "Recomendaciones suficientemente extensas",
        "cognitive_assessment": "Normal",
        "follow_up_frequency": "MONTHLY",
        "next_evaluation_date": str(
            date.today() + timedelta(days=30)
        ),
    }

@patch("evaluations.views.register_evaluation_use_case")
def test_register_evaluation_success(
    mock_use_case,
    api_client,
    valid_payload,
):
    evaluation = EvaluationFactory.build()
    evaluation.id = 1

    mock_use_case.execute.return_value = evaluation

    response = api_client.post(
        "/api/evaluations/register/",
        valid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    mock_use_case.execute.assert_called_once()

def test_register_evaluation_invalid_serializer(
    api_client,
):
    response = api_client.post(
        "/api/evaluations/register/",
        {},
        format="json",
    )

    assert response.status_code == (
        status.HTTP_400_BAD_REQUEST
    )

    assert "error" in response.data

@patch("evaluations.views.register_evaluation_use_case")
def test_register_evaluation_student_not_found(
    mock_use_case,
    api_client,
    valid_payload,
):
    mock_use_case.execute.side_effect = (
        StudentNotFoundError(1)
    )

    response = api_client.post(
        "/api/evaluations/register/",
        valid_payload,
        format="json",
    )

    assert response.status_code == (
        status.HTTP_404_NOT_FOUND
    )

@patch("evaluations.views.register_evaluation_use_case")
def test_register_evaluation_student_not_characterized(
    mock_use_case,
    api_client,
    valid_payload,
):
    mock_use_case.execute.side_effect = (
        StudentNotCharacterizedError(1)
    )

    response = api_client.post(
        "/api/evaluations/register/",
        valid_payload,
        format="json",
    )

    assert response.status_code == (
        status.HTTP_422_UNPROCESSABLE_ENTITY
    )

@patch("evaluations.views.register_evaluation_use_case")
def test_register_evaluation_invalid_domain_data(
    mock_use_case,
    api_client,
    valid_payload,
):
    mock_use_case.execute.side_effect = (
        InvalidEvaluationDataError(
            "Error de dominio"
        )
    )

    response = api_client.post(
        "/api/evaluations/register/",
        valid_payload,
        format="json",
    )

    assert response.status_code == (
        status.HTTP_400_BAD_REQUEST
    )

@patch("evaluations.views.register_evaluation_use_case")
def test_register_evaluation_external_service_error(
    mock_use_case,
    api_client,
    valid_payload,
):

    mock_use_case.execute.side_effect = (
        ExternalServiceError(
            "student-service",
            "timeout"
        )
    )

    response = api_client.post(
        "/api/evaluations/register/",
        valid_payload,
        format="json",
    )

    assert response.status_code == (
        status.HTTP_503_SERVICE_UNAVAILABLE
    )

@patch("evaluations.views.register_evaluation_use_case")
def test_register_evaluation_unexpected_error(
    mock_use_case,
    api_client,
    valid_payload,
):
    mock_use_case.execute.side_effect = Exception(
        "Unexpected"
    )

    response = api_client.post(
        "/api/evaluations/register/",
        valid_payload,
        format="json",
    )

    assert response.status_code == (
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )

def test_register_evaluation_requires_psychologist_role(
):
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

    response = client.post(
        "/api/evaluations/register/",
        {},
        format="json",
    )

    assert response.status_code == (
        status.HTTP_403_FORBIDDEN
    )