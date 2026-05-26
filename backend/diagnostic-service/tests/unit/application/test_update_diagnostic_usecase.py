import pytest
from datetime import datetime
from unittest.mock import Mock

from src.application.use_cases.update_diagnostic import (
    UpdateDiagnosticUseCase
)

from src.domain.entities.diagnostic_catalog import (
    Diagnostic,
    NEECategory
)

from src.domain.exceptions import (
    DiagnosticNotFoundError,
    DiagnosticAlreadyExistsError,
    InvalidDiagnosticDataError
)


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def sample_diagnostic():
    return Diagnostic(
        id=1,
        code="ADHD001",
        name="TDAH",
        category=NEECategory.ADHD,
        description="Diagnóstico inicial",
        normative_reference="Ley 2216",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


class TestUpdateDiagnosticUseCase:

    def test_update_diagnostic_success(
        self,
        mock_repository,
        sample_diagnostic
    ):
        mock_repository.find_by_id.return_value = sample_diagnostic
        mock_repository.find_by_code.return_value = None
        mock_repository.save.return_value = sample_diagnostic

        use_case = UpdateDiagnosticUseCase(
            mock_repository
        )

        data = {
            "code": "AUT001",
            "name": "Autismo",
            "category": "AUTISM_SPECTRUM",
            "description": "Actualizado"
        }

        result = use_case.execute(1, data)

        assert result.code == "AUT001"
        assert result.name == "Autismo"
        assert result.category == NEECategory.AUTISM_SPECTRUM
        assert result.description == "Actualizado"

        mock_repository.find_by_id.assert_called_once_with(1)
        mock_repository.save.assert_called_once()

    def test_update_diagnostic_not_found(
        self,
        mock_repository
    ):
        mock_repository.find_by_id.return_value = None

        use_case = UpdateDiagnosticUseCase(
            mock_repository
        )

        with pytest.raises(DiagnosticNotFoundError):
            use_case.execute(999, {})

    def test_update_diagnostic_duplicate_code(
        self,
        mock_repository,
        sample_diagnostic
    ):
        existing = Diagnostic(
            id=2,
            code="AUT001",
            name="Otro",
            category=NEECategory.ADHD,
            description="Duplicado"
        )

        mock_repository.find_by_id.return_value = sample_diagnostic
        mock_repository.find_by_code.return_value = existing

        use_case = UpdateDiagnosticUseCase(
            mock_repository
        )

        with pytest.raises(DiagnosticAlreadyExistsError):
            use_case.execute(
                1,
                {
                    "code": "AUT001"
                }
            )

    def test_update_diagnostic_invalid_category(
        self,
        mock_repository,
        sample_diagnostic
    ):
        mock_repository.find_by_id.return_value = sample_diagnostic
        mock_repository.find_by_code.return_value = None

        use_case = UpdateDiagnosticUseCase(
            mock_repository
        )

        with pytest.raises(InvalidDiagnosticDataError):
            use_case.execute(
                1,
                {
                    "category": "INVALID_CATEGORY"
                }
            )

    def test_update_diagnostic_empty_name(
        self,
        mock_repository,
        sample_diagnostic
    ):
        mock_repository.find_by_id.return_value = sample_diagnostic
        mock_repository.find_by_code.return_value = None

        use_case = UpdateDiagnosticUseCase(
            mock_repository
        )

        with pytest.raises(InvalidDiagnosticDataError):
            use_case.execute(
                1,
                {
                    "name": ""
                }
            )

    def test_update_diagnostic_invalid_entity(
        self,
        mock_repository,
        sample_diagnostic
    ):
        mock_repository.find_by_id.return_value = sample_diagnostic
        mock_repository.find_by_code.return_value = None

        use_case = UpdateDiagnosticUseCase(
            mock_repository
        )

        with pytest.raises(InvalidDiagnosticDataError):
            use_case.execute(
                1,
                {
                    "description": ""
                }
            )