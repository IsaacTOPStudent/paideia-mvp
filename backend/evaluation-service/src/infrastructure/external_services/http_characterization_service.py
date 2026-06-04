import requests

from requests.exceptions import (
    ConnectionError,
    Timeout,
    RequestException,
)

from src.domain.dto.characterization_info import (
    CharacterizationInfoDTO
)

from src.domain.ports.external.characterization_service_port import (
    CharacterizationServicePort,
)

from src.domain.exceptions import (
    ExternalServiceError
)


class HttpCharacterizationService(
    CharacterizationServicePort
):

    def __init__(
        self,
        base_url: str,
        timeout: int = 5,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_characterizations(
        self,
        student_id: int
    ) -> list[CharacterizationInfoDTO]:

        try:
            response = requests.get(
                f"{self.base_url}/api/diagnostics/student/{student_id}/characterizations/",
                timeout=self.timeout,
                headers={
                    "Accept": "application/json"
                }
            )
            if response.status_code == 404:
                return []

            if response.status_code != 200:
                raise ExternalServiceError(
                    "diagnostic-service",
                    f"HTTP {response.status_code}"
                )

            data = response.json()

            if isinstance(data, dict):
                results = data.get("results", [])
            else:
                results = data

            return [
                CharacterizationInfoDTO(
                    id=item["id"],
                    student_id=item["student_id"],
                    diagnostic_id=item["diagnostic_id"],
                    diagnostic_name=item.get(
                        "diagnostic_name",
                        ""
                    ),
                    nee_category=item.get(
                        "nee_category",
                        ""
                    ),
                    severity_level=item.get(
                        "severity_level",
                        ""
                    ),
                    identification_date=item.get(
                        "identification_date",
                        ""
                    ),
                    is_active=item.get(
                        "is_active",
                        True
                    ),
                )
                for item in results
            ]

        except (ConnectionError, Timeout) as e:
            raise ExternalServiceError(
                "diagnostic-service",
                str(e)
            )

        except RequestException as e:
            raise ExternalServiceError(
                "diagnostic-service",
                str(e)
            )