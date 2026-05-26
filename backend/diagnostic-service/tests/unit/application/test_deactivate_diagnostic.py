import pytest
from datetime import datetime
from unittest.mock import Mock

from src.application.use_cases.deactivate_diagnostic import (
    DeactivateDiagnosticUseCase
)

from src.domain.entities.diagnostic_catalog import (
    Diagnostic,
    NEECategory
)

from src.domain.exceptions import (
    DiagnosticNotFoundError
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


class TestDeactivateDiagnosticUseCase:

    def test_deactivate_diagnostic_success(
        self,
        mock_repository,
        sample_diagnostic
    ):
        mock_repository.find_by_id.return_value = sample_diagnostic
        mock_repository.save.return_value = sample_diagnostic

        use_case = DeactivateDiagnosticUseCase(
            mock_repository
        )

        result = use_case.execute(1)

        assert result.is_active is False

        mock_repository.find_by_id.assert_called_once_with(1)
        mock_repository.save.assert_called_once()

    def test_deactivate_diagnostic_not_found(
        self,
        mock_repository
    ):
        mock_repository.find_by_id.return_value = None

        use_case = DeactivateDiagnosticUseCase(
            mock_repository
        )

        with pytest.raises(DiagnosticNotFoundError):
            use_case.execute(999)