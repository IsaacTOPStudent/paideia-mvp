from django.utils import timezone

from src.domain.entities.diagnostic_catalog import NEECategory
from src.domain.ports.diagnostic_repository import DiagnosticCatalogRepository
from src.domain.exceptions import (
    InvalidDiagnosticDataError,
    DiagnosticAlreadyExistsError,
    DiagnosticNotFoundError
)

class UpdateDiagnosticUseCase:

    def __init__(self, repository: DiagnosticCatalogRepository):
        self.repository = repository

    def execute(self, diagnostic_id: int, data: dict):

        diagnostic = self.repository.find_by_id(diagnostic_id)

        if not diagnostic:
            raise DiagnosticNotFoundError(
                "Diagnóstico no encontrado"
            )

        code = str(
            data.get("code", diagnostic.code)
        ).strip().upper()

        name = str(
            data.get("name", diagnostic.name)
        ).strip()

        if not code or not name:
            raise InvalidDiagnosticDataError(
                "El código y el nombre son obligatorios"
            )

        existing = self.repository.find_by_code(code)

        if existing and existing.id != diagnostic.id:
            raise DiagnosticAlreadyExistsError(
                f"Ya existe un diagnóstico con código {code}"
            )

        try:
            category = NEECategory.from_string(
                data.get("category", diagnostic.category.value)
            )

        except ValueError:
            raise InvalidDiagnosticDataError(
                f"Categoría inválida: {data.get('category')}"
            )

        diagnostic.code = code
        diagnostic.name = name
        diagnostic.category = category

        diagnostic.description = data.get(
            "description",
            diagnostic.description
        )

        diagnostic.normative_reference = data.get(
            "normative_reference",
            diagnostic.normative_reference
        )

        diagnostic.updated_at = timezone.now()

        is_valid, errors = diagnostic.validate()

        if not is_valid:
            raise InvalidDiagnosticDataError(
                f"Campos inválidos: {', '.join(errors)}"
            )

        return self.repository.save(diagnostic)