
import pytest
from datetime import date
from unittest.mock import Mock

from src.application.use_cases.manage_catalog import (
    CharacterizeStudentUseCase,
    CreateDiagnosticUseCase,
)
from src.domain.entities.diagnostic_catalog import NEECategory
from src.domain.entities.characterization import SeverityLevel
from src.domain.exceptions import DiagnosticAlreadyExistsError, DiagnosticInactiveError, InvalidCharacterizationDataError, InvalidDiagnosticDataError


class TestCreateDiagnosticUseCase:
    
    @pytest.fixture
    def mock_diagnostic_repo(self):
        repo = Mock()
        repo.exists_by_code = Mock(return_value=False)
        repo.save = Mock(side_effect=lambda d: d)
        return repo
    
    @pytest.fixture
    def use_case(self, mock_diagnostic_repo):
        return CreateDiagnosticUseCase(mock_diagnostic_repo)
    
    def test_create_diagnostic_success(self, use_case, mock_diagnostic_repo):
        data = {
            "code": "DSL001",
            "name": "Dislexia",
            "category": "SPECIFIC_LEARNING_DISORDER",
            "description": "Dificultad en lectoescritura",
        }
        
        diagnostic = use_case.execute(data)
        
        assert diagnostic.code == "DSL001"
        assert diagnostic.name == "Dislexia"
        assert diagnostic.category == NEECategory.SPECIFIC_LEARNING_DISORDER
        mock_diagnostic_repo.save.assert_called_once()
    
    def test_create_diagnostic_normalizes_code(self, use_case):
        data = {
            "code": "dsl001",
            "name": "Dislexia",
            "category": "SPECIFIC_LEARNING_DISORDER",
        }
        
        diagnostic = use_case.execute(data)
        
        assert diagnostic.code == "DSL001"
    
    def test_create_diagnostic_fails_duplicate_code(self, use_case, mock_diagnostic_repo):
        mock_diagnostic_repo.exists_by_code.return_value = True
        
        data = {
            "code": "DSL001",
            "name": "Dislexia",
            "category": "SPECIFIC_LEARNING_DISORDER",
        }
        
        with pytest.raises(DiagnosticAlreadyExistsError, match=f"Ya existe un diagnóstico con el código: {data['code']}"):
            use_case.execute(data)
    
    def test_create_diagnostic_fails_missing_code(self, use_case):
        data = {
            "code": "",
            "name": "Dislexia",
            "category": "SPECIFIC_LEARNING_DISORDER",
        }
        
        with pytest.raises(InvalidDiagnosticDataError, match="obligatorios"):
            use_case.execute(data)
    
    def test_create_diagnostic_fails_invalid_category(self, use_case):
        data = {
            "code": "DSL001",
            "name": "Dislexia",
            "category": "INVALID_CATEGORY",
        }
        
        with pytest.raises(InvalidDiagnosticDataError, match="Categoría no válida"):
            use_case.execute(data)


class TestCharacterizeStudentUseCase:
    
    @pytest.fixture
    def mock_diagnostic_repo(self):
        """Mock del repositorio de diagnósticos"""
        repo = Mock()
        
        diagnostic = Mock()
        diagnostic.id = 10
        diagnostic.can_be_used = Mock(return_value=True)
        
        repo.is_any_active = Mock(return_value=True)
        repo.find_by_id = Mock(return_value=diagnostic)
        return repo
    
    @pytest.fixture
    def mock_char_repo(self):
        repo = Mock()
        repo.save = Mock(side_effect=lambda c: c)
        return repo
    
    @pytest.fixture
    def use_case(self, mock_diagnostic_repo, mock_char_repo):
        return CharacterizeStudentUseCase(mock_diagnostic_repo, mock_char_repo)
    
    def test_characterize_student_success(self, use_case, mock_char_repo):
        data = {
            "student_id": 1,
            "diagnostic_id": 10,
            "severity_level": "MODERATE",
            "identification_date": date(2026, 5, 1),
            "observations": "Requiere apoyo",
            "cognitive_area_notes": "Dificultad en comprensión",
        }
        psychologist_id = 5
        
        char = use_case.execute(data, psychologist_id)
        
        assert char.student_id == 1
        assert char.diagnostic_id == 10
        assert char.severity_level == SeverityLevel.MODERATE
        assert char.created_by == psychologist_id
        mock_char_repo.save.assert_called_once()
    
    def test_characterize_fails_no_active_diagnostics(self, use_case, mock_diagnostic_repo):
        mock_diagnostic_repo.is_any_active.return_value = False
        
        data = {
            "student_id": 1,
            "diagnostic_id": 10,
            "severity_level": "MODERATE",
            "identification_date": date.today(),
        }
        
        with pytest.raises(InvalidDiagnosticDataError, match="catálogo de diagnósticos no está configurado"):
            use_case.execute(data, psychologist_id=5)
    
    def test_characterize_fails_inactive_diagnostic(self, use_case, mock_diagnostic_repo):
        inactive_diagnostic = Mock()
        inactive_diagnostic.can_be_used = Mock(return_value=False)
        mock_diagnostic_repo.find_by_id.return_value = inactive_diagnostic
        
        data = {
            "student_id": 1,
            "diagnostic_id": 10,
            "severity_level": "MODERATE",
            "identification_date": date.today(),
        }
        
        with pytest.raises(DiagnosticInactiveError, match=f"El diagnóstico {data['diagnostic_id']} está inactivo y no puede usarse."):
            use_case.execute(data, psychologist_id=5)
    
    def test_characterize_fails_invalid_severity(self, use_case):
        data = {
            "student_id": 1,
            "diagnostic_id": 10,
            "severity_level": "INVALID",
            "identification_date": date.today(),
        }
        
        with pytest.raises(InvalidCharacterizationDataError, match="Nivel de severidad inválido"):
            use_case.execute(data, psychologist_id=5)
    
    def test_characterize_fails_validation(self, use_case):
        data = {
            "student_id": None,  
            "diagnostic_id": 10,
            "severity_level": "MODERATE",
            "identification_date": None,  
        }
        
        with pytest.raises(InvalidCharacterizationDataError, match="Campos obligatorios faltantes"):
            use_case.execute(data, psychologist_id=5)