import pytest
from datetime import date

from diagnostics.models import DiagnosticModel, CharacterizationModel
from src.infrastructure.repositories.django_diagnostic_repository import (
    DjangoDiagnosticRepository,
    DjangoCharacterizationRepository,
)
from src.domain.entities.diagnostic_catalog import Diagnostic, NEECategory
from src.domain.entities.characterization import Characterization, SeverityLevel


@pytest.mark.django_db
class TestDjangoDiagnosticRepository:
    
    @pytest.fixture
    def repository(self):
        return DjangoDiagnosticRepository()
    
    def test_save_new_diagnostic(self, repository):
        diagnostic = Diagnostic(
            id=None,
            code="DSL001",
            name="Dislexia",
            category=NEECategory.SPECIFIC_LEARNING_DISORDER,
            description="Dificultad en lectoescritura",
            is_active=True,
        )
        
        saved = repository.save(diagnostic)
        
        assert saved.id is not None
        assert DiagnosticModel.objects.filter(code="DSL001").exists()
    
    def test_find_by_id(self, repository):
        model = DiagnosticModel.objects.create(
            code="TDAH001",
            name="TDAH",
            category="SPECIFIC_LEARNING_DISORDER",
            is_active=True,
        )
        
        found = repository.find_by_id(model.pk)
        
        assert found is not None
        assert found.code == "TDAH001"
        assert found.category == NEECategory.SPECIFIC_LEARNING_DISORDER
    
    def test_find_by_code(self, repository):
        DiagnosticModel.objects.create(
            code="AUT001",
            name="Autismo",
            category="COGNITIVE_DISABILITY",
            is_active=True,
        )
        
        found = repository.find_by_code("AUT001")
        
        assert found is not None
        assert found.name == "Autismo"
    
    def test_find_all_active(self, repository):
        DiagnosticModel.objects.create(code="D1", name="Activo", category="PHYSICAL_DISABILITY", is_active=True)
        DiagnosticModel.objects.create(code="D2", name="Inactivo", category="PHYSICAL_DISABILITY", is_active=False)
        
        actives = repository.find_all_active()
        
        assert len(actives) == 1
        assert actives[0].code == "D1"
    
    def test_exists_by_code(self, repository):
        DiagnosticModel.objects.create(code="TEST", name="Test", category="SENSORY_DISABILITY", is_active=True)
        
        assert repository.exists_by_code("TEST") is True
        assert repository.exists_by_code("NOEXISTE") is False
    
    def test_is_any_active(self, repository):
        assert repository.is_any_active() is False
        
        DiagnosticModel.objects.create(code="D1", name="Test", category="PHYSICAL_DISABILITY", is_active=True)
        
        assert repository.is_any_active() is True


@pytest.mark.django_db
class TestDjangoCharacterizationRepository:
    
    @pytest.fixture
    def repository(self):
        return DjangoCharacterizationRepository()
    
    @pytest.fixture
    def diagnostic_model(self):
        return DiagnosticModel.objects.create(
            code="TEST",
            name="Test Diagnostic",
            category="SPECIFIC_LEARNING_DISORDER",
            is_active=True,
        )
    
    def test_save_new_characterization(self, repository, diagnostic_model):
        char = Characterization(
            id=None,
            student_id=1,
            diagnostic_id=diagnostic_model.pk,
            severity_level=SeverityLevel.MODERATE,
            identification_date=date(2026, 5, 1),
            observations="Test observation",
            created_by=5,
            is_active=True,
        )
        
        saved = repository.save(char)
        
        assert saved.id is not None
        assert CharacterizationModel.objects.filter(student_id=1).exists()
    
    def test_find_by_id(self, repository, diagnostic_model):
        model = CharacterizationModel.objects.create(
            student_id=1,
            diagnostic_id=diagnostic_model.pk,
            severity_level="MODERATE",
            identification_date=date.today(),
            is_active=True,
            created_by=1
        )
        
        found = repository.find_by_id(model.pk)
        
        assert found is not None
        assert found.student_id == 1
        assert found.severity_level == SeverityLevel.MODERATE
    
    def test_find_by_student(self, repository, diagnostic_model):
        CharacterizationModel.objects.create(
            student_id=10,
            diagnostic_id=diagnostic_model.pk,
            severity_level="MILD",
            identification_date=date.today(),
            created_by=1
        )
        CharacterizationModel.objects.create(
            student_id=10,
            diagnostic_id=diagnostic_model.pk,
            severity_level="MODERATE",
            identification_date=date.today(),
            created_by=1
        )
        
        chars = repository.find_by_student(student_id=10)
        
        assert len(chars) == 2
    
    def test_find_active_by_student(self, repository, diagnostic_model):
        CharacterizationModel.objects.create(
            student_id=10,
            diagnostic_id=diagnostic_model.pk,
            severity_level="MILD",
            identification_date=date.today(),
            is_active=True,
            created_by=1
        )
        CharacterizationModel.objects.create(
            student_id=10,
            diagnostic_id=diagnostic_model.pk,
            severity_level="MODERATE",
            identification_date=date.today(),
            is_active=False,
            created_by=1
        )
        
        chars = repository.find_active_by_student(student_id=10)
        
        assert len(chars) == 1
        assert chars[0].is_active is True