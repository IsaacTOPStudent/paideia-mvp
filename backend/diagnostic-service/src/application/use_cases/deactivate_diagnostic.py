from django.utils import timezone

from src.domain.ports.diagnostic_repository import (
    DiagnosticCatalogRepository
)

from src.domain.exceptions import (
    DiagnosticNotFoundError
)

class DeactivateDiagnosticUseCase:

    def __init__(self, repository: DiagnosticCatalogRepository):
        self.repository = repository

    def execute(self, diagnostic_id: int):

        diagnostic = self.repository.find_by_id(
            diagnostic_id
        )

        if not diagnostic:
            raise DiagnosticNotFoundError(
                "Diagnóstico no encontrado"
            )

        diagnostic.deactivate()

        return self.repository.save(diagnostic)