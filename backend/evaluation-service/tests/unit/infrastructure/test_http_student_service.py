import pytest
from unittest.mock import Mock, patch

from requests.exceptions import (
    ConnectionError,
    Timeout,
    RequestException,
)

from src.infrastructure.external_services.http_student_service import (
    HttpStudentService,
)

from src.domain.dto.student_info import StudentInfoDTO

from src.domain.exceptions import (
    ExternalServiceError,
)

@pytest.fixture
def service():
    return HttpStudentService(
        base_url="http://student-service:8002",
        timeout=5,
    )

@patch("src.infrastructure.external_services.http_student_service.requests.get")
def test_get_student_info_success(mock_get, service):
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "id": 1,
        "first_name": "Juan",
        "last_name": "Perez",
        "document_number": "123456",
        "is_active": True,
    }

    mock_get.return_value = response

    result = service.get_student_info(1)

    assert isinstance(result, StudentInfoDTO)

    assert result.id == 1
    assert result.first_name == "Juan"
    assert result.last_name == "Perez"
    assert result.document_number == "123456"
    assert result.is_active is True

@patch("src.infrastructure.external_services.http_student_service.requests.get")
def test_get_student_info_returns_none_when_404(
    mock_get,
    service
):
    response = Mock()
    response.status_code = 404

    mock_get.return_value = response

    result = service.get_student_info(999)

    assert result is None

@patch("src.infrastructure.external_services.http_student_service.requests.get")
def test_get_student_info_raises_external_service_error_for_http_error(
    mock_get,
    service
):
    response = Mock()
    response.status_code = 500

    mock_get.return_value = response

    with pytest.raises(ExternalServiceError) as exc:
        service.get_student_info(1)

    assert "student-service" in str(exc.value)
    assert "HTTP 500" in str(exc.value)

@patch("src.infrastructure.external_services.http_student_service.requests.get")
def test_get_student_info_connection_error(
    mock_get,
    service
):
    mock_get.side_effect = ConnectionError("Connection refused")

    with pytest.raises(ExternalServiceError) as exc:
        service.get_student_info(1)

    assert "student-service" in str(exc.value)
    assert "Connection refused" in str(exc.value)

@patch("src.infrastructure.external_services.http_student_service.requests.get")
def test_get_student_info_timeout(
    mock_get,
    service
):
    mock_get.side_effect = Timeout("Request timeout")

    with pytest.raises(ExternalServiceError) as exc:
        service.get_student_info(1)

    assert "student-service" in str(exc.value)
    assert "Request timeout" in str(exc.value)

@patch("src.infrastructure.external_services.http_student_service.requests.get")
def test_get_student_info_request_exception(
    mock_get,
    service
):
    mock_get.side_effect = RequestException("Unexpected error")

    with pytest.raises(ExternalServiceError) as exc:
        service.get_student_info(1)

    assert "student-service" in str(exc.value)
    assert "Unexpected error" in str(exc.value)

@patch("src.infrastructure.external_services.http_student_service.requests.get")
def test_get_student_info_calls_correct_url(
    mock_get,
    service
):
    response = Mock()
    response.status_code = 404

    mock_get.return_value = response

    service.get_student_info(15)

    mock_get.assert_called_once_with(
        "http://student-service:8002/api/students/15/",
        timeout=5,
        headers={
            "Accept": "application/json"
        }
    )