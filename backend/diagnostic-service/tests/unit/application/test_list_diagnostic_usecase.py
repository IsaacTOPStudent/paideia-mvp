import pytest
from unittest.mock import Mock

from src.application.use_cases.manage_catalog import (
    ListDiagnosticUseCase
)
from src.domain.entities.diagnostic_catalog import Diagnostic, NEECategory


class TestListDiagnosticUseCase:
    
    @pytest.fixture
    def mock_diagnostic_repo(self):
        return Mock()
    
    @pytest.fixture
    def use_case(self, mock_diagnostic_repo):
        return ListDiagnosticUseCase(mock_diagnostic_repo)
    
    @pytest.fixture
    def sample_active_diagnostics(self):
        return [
            Diagnostic(
                id=1,
                code="DSL001",
                name="Dislexia",
                category=NEECategory.SPECIFIC_LEARNING_DISORDER,
                description="Dificultad en lectoescritura",
                is_active=True
            ),
            Diagnostic(
                id=2,
                code="TDAH001",
                name="TDAH",
                category=NEECategory.ADHD,
                description="Trastorno por déficit de atención",
                is_active=True
            ),
            Diagnostic(
                id=3,
                code="AUT001",
                name="Autismo",
                category=NEECategory.AUTISM_SPECTRUM,
                description="Trastorno del espectro autista",
                is_active=True
            ),
        ]
    
    @pytest.fixture
    def sample_all_diagnostics(self, sample_active_diagnostics):
        all_diagnostics = sample_active_diagnostics.copy()
        all_diagnostics.append(
            Diagnostic(
                id=4,
                code="OLD001",
                name="Diagnóstico Obsoleto",
                category=NEECategory.COGNITIVE_DISABILITY,
                description="Ya no se usa",
                is_active=False
            )
        )
        return all_diagnostics
    
    def test_execute_returns_only_active_by_default(
        self,
        use_case,
        mock_diagnostic_repo,
        sample_active_diagnostics
    ):
        mock_diagnostic_repo.find_all_active.return_value = sample_active_diagnostics
        
        result = use_case.execute()
        
        assert len(result) == 3
        mock_diagnostic_repo.find_all_active.assert_called_once()
        mock_diagnostic_repo.find_all.assert_not_called()
    
    def test_execute_returns_only_active_explicitly(
        self,
        use_case,
        mock_diagnostic_repo,
        sample_active_diagnostics
    ):
        mock_diagnostic_repo.find_all_active.return_value = sample_active_diagnostics
        
        result = use_case.execute(active_only=True)
        
        assert len(result) == 3
        assert all(d.is_active for d in result)
        mock_diagnostic_repo.find_all_active.assert_called_once()
    
    def test_execute_returns_all_when_active_only_false(
        self,
        use_case,
        mock_diagnostic_repo,
        sample_all_diagnostics
    ):
        mock_diagnostic_repo.find_all.return_value = sample_all_diagnostics
        
        result = use_case.execute(active_only=False)
        
        assert len(result) == 4
        mock_diagnostic_repo.find_all.assert_called_once()
        mock_diagnostic_repo.find_all_active.assert_not_called()
    
    def test_execute_returns_empty_list_when_no_active(
        self,
        use_case,
        mock_diagnostic_repo
    ):
        mock_diagnostic_repo.find_all_active.return_value = []
        
        result = use_case.execute(active_only=True)
        
        assert result == []
        assert len(result) == 0
    
    def test_execute_returns_empty_list_when_no_diagnostics(
        self,
        use_case,
        mock_diagnostic_repo
    ):
        mock_diagnostic_repo.find_all.return_value = []
        
        result = use_case.execute(active_only=False)
        
        assert result == []
        assert len(result) == 0
    
    def test_execute_preserves_diagnostic_properties(
        self,
        use_case,
        mock_diagnostic_repo,
        sample_active_diagnostics
    ):
        mock_diagnostic_repo.find_all_active.return_value = sample_active_diagnostics
        
        result = use_case.execute()
        
        first_diagnostic = result[0]
        assert first_diagnostic.id == 1
        assert first_diagnostic.code == "DSL001"
        assert first_diagnostic.name == "Dislexia"
        assert first_diagnostic.category == NEECategory.SPECIFIC_LEARNING_DISORDER
        assert first_diagnostic.is_active is True
    
    def test_execute_returns_diagnostics_in_repository_order(
        self,
        use_case,
        mock_diagnostic_repo,
        sample_active_diagnostics
    ):
        mock_diagnostic_repo.find_all_active.return_value = sample_active_diagnostics
        
        result = use_case.execute()
        
        assert result[0].code == "DSL001"
        assert result[1].code == "TDAH001"
        assert result[2].code == "AUT001"
    
    def test_execute_handles_mixed_active_inactive(
        self,
        use_case,
        mock_diagnostic_repo,
        sample_all_diagnostics
    ):
        mock_diagnostic_repo.find_all.return_value = sample_all_diagnostics
        
        result = use_case.execute(active_only=False)
        
        active_count = sum(1 for d in result if d.is_active)
        inactive_count = sum(1 for d in result if not d.is_active)
        
        assert active_count == 3
        assert inactive_count == 1
        assert len(result) == 4
    
    def test_execute_returns_list_of_diagnostics(
        self,
        use_case,
        mock_diagnostic_repo,
        sample_active_diagnostics
    ):
        mock_diagnostic_repo.find_all_active.return_value = sample_active_diagnostics
        
        result = use_case.execute()
        
        assert isinstance(result, list)
        assert all(isinstance(d, Diagnostic) for d in result)
    
    def test_execute_with_different_categories(
        self,
        use_case,
        mock_diagnostic_repo
    ):
        diagnostics = [
            Diagnostic(
                id=1,
                code="PHYS001",
                name="Física",
                category=NEECategory.PHYSICAL_DISABILITY,
                description="Test",
                is_active=True
            ),
            Diagnostic(
                id=2,
                code="SENS001",
                name="Sensorial",
                category=NEECategory.SENSORY_VISUAL,
                description="Test",
                is_active=True
            ),
            Diagnostic(
                id=3,
                code="GIFT001",
                name="Superdotación",
                category=NEECategory.GIFTEDNESS,
                description="Test",
                is_active=True
            ),
        ]
        
        mock_diagnostic_repo.find_all_active.return_value = diagnostics
        
        result = use_case.execute()
        
        assert len(result) == 3
        categories = [d.category for d in result]
        assert NEECategory.PHYSICAL_DISABILITY in categories
        assert NEECategory.SENSORY_VISUAL in categories
        assert NEECategory.GIFTEDNESS in categories