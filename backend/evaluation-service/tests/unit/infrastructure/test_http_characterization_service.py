from unittest.mock import Mock, patch

import pytest

from requests.exceptions import (
    ConnectionError,
    Timeout,
    RequestException,
)

from src.infrastructure.external_services.http_characterization_service import (
    HttpCharacterizationService,
)

from src.domain.dto.characterization_info import (
    CharacterizationInfoDTO,
)

from src.domain.exceptions import (
    ExternalServiceError,
)

@pytest.fixture
def service():
    return HttpCharacterizationService(
        base_url="http://diagnostic-service:8003",
        timeout=5,
    )

@patch(
    "src.infrastructure.external_services.http_characterization_service.requests.get"
)
def test_get_characterizations_success_list(
    mock_get,
    service,
):
    response = Mock()
    response.status_code = 200
    response.json.return_value = [
        {
            "id": 1,
            "student_id": 10,
            "diagnostic_id": 5,
            "diagnostic_name": "TDAH",
            "nee_category": "COGNITIVE",
            "severity_level": "MEDIUM",
            "identification_date": "2025-01-10",
            "is_active": True,
        }
    ]

    mock_get.return_value = response

    result = service.get_characterizations(10)

    assert len(result) == 1
    assert isinstance(result[0], CharacterizationInfoDTO)

    assert result[0].id == 1
    assert result[0].student_id == 10
    assert result[0].diagnostic_name == "TDAH"

@patch(
    "src.infrastructure.external_services.http_characterization_service.requests.get"
)
def test_get_characterizations_success_paginated(
    mock_get,
    service,
):
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "count": 1,
        "results": [
            {
                "id": 1,
                "student_id": 10,
                "diagnostic_id": 5,
                "diagnostic_name": "Autismo",
                "nee_category": "NEE",
                "severity_level": "HIGH",
                "identification_date": "2025-01-10",
                "is_active": True,
            }
        ]
    }

    mock_get.return_value = response

    result = service.get_characterizations(10)

    assert len(result) == 1
    assert result[0].diagnostic_name == "Autismo"

@patch(
    "src.infrastructure.external_services.http_characterization_service.requests.get"
)
def test_get_characterizations_returns_empty_list_when_404(
    mock_get,
    service,
):
    response = Mock()
    response.status_code = 404

    mock_get.return_value = response

    result = service.get_characterizations(999)

    assert result == []

@patch(
    "src.infrastructure.external_services.http_characterization_service.requests.get"
)
def test_get_characterizations_http_error(
    mock_get,
    service,
):
    response = Mock()
    response.status_code = 500

    mock_get.return_value = response

    with pytest.raises(ExternalServiceError) as exc:
        service.get_characterizations(1)

    assert "diagnostic-service" in str(exc.value)
    assert "HTTP 500" in str(exc.value)

@patch(
    "src.infrastructure.external_services.http_characterization_service.requests.get"
)
def test_get_characterizations_connection_error(
    mock_get,
    service,
):
    mock_get.side_effect = ConnectionError(
        "Connection refused"
    )

    with pytest.raises(ExternalServiceError) as exc:
        service.get_characterizations(1)

    assert "diagnostic-service" in str(exc.value)
    assert "Connection refused" in str(exc.value)

@patch(
    "src.infrastructure.external_services.http_characterization_service.requests.get"
)
def test_get_characterizations_timeout(
    mock_get,
    service,
):
    mock_get.side_effect = Timeout(
        "Request timeout"
    )

    with pytest.raises(ExternalServiceError) as exc:
        service.get_characterizations(1)

    assert "diagnostic-service" in str(exc.value)
    assert "Request timeout" in str(exc.value)

@patch(
    "src.infrastructure.external_services.http_characterization_service.requests.get"
)
def test_get_characterizations_request_exception(
    mock_get,
    service,
):
    mock_get.side_effect = RequestException(
        "Unexpected error"
    )

    with pytest.raises(ExternalServiceError) as exc:
        service.get_characterizations(1)

    assert "diagnostic-service" in str(exc.value)
    assert "Unexpected error" in str(exc.value)

@patch(
    "src.infrastructure.external_services.http_characterization_service.requests.get"
)
def test_get_characterizations_uses_default_values(
    mock_get,
    service,
):
    response = Mock()
    response.status_code = 200
    response.json.return_value = [
        {
            "id": 1,
            "student_id": 10,
            "diagnostic_id": 5,
        }
    ]

    mock_get.return_value = response

    result = service.get_characterizations(10)

    characterization = result[0]

    assert characterization.diagnostic_name == ""
    assert characterization.nee_category == ""
    assert characterization.severity_level == ""
    assert characterization.identification_date == ""
    assert characterization.is_active is True

@patch(
    "src.infrastructure.external_services.http_characterization_service.requests.get"
)
def test_get_characterizations_calls_correct_url(
    mock_get,
    service,
):
    response = Mock()
    response.status_code = 404

    mock_get.return_value = response

    service.get_characterizations(15)

    mock_get.assert_called_once_with(
        "http://diagnostic-service:8003/api/diagnostics/student/15/characterizations/",
        timeout=5,
        headers={
            "Accept": "application/json"
        }
    )