import requests

from requests.exceptions import (
    ConnectionError,
    Timeout,
    RequestException,
)

from src.domain.dto.student_info import StudentInfoDTO

from src.domain.ports.external.student_service_port import (
    StudentServicePort,
)

from src.domain.exceptions import (
    StudentNotFoundError,
    ExternalServiceError,
)

class HttpStudentService(StudentServicePort):
    def __init__(
        self,
        base_url: str,
        timeout: int = 5,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_student_info(
        self,
        student_id: int
    ) -> StudentInfoDTO | None:

        try:
            response = requests.get(
                f"{self.base_url}/api/students/{student_id}/",
                timeout=self.timeout,
                headers={
                    "Accept": "application/json"
                }
            )

            if response.status_code == 404:
                return None

            if response.status_code != 200:
                raise ExternalServiceError(
                    "student-service",
                    f"HTTP {response.status_code}"
                )

            data = response.json()

            return StudentInfoDTO(
                id=data["id"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                document_number=data["document_number"],
                is_active=data["is_active"],
            )

        except (ConnectionError, Timeout) as e:
            raise ExternalServiceError(
                "student-service",
                str(e)
            )

        except RequestException as e:
            raise ExternalServiceError(
                "student-service",
                str(e)
            )
