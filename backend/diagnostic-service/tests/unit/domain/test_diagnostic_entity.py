"""
Tests unitarios para la entidad Diagnostic del dominio.
Estos tests NO usan base de datos.
"""
import pytest
from datetime import datetime
from django.utils import timezone

from src.domain.entities.diagnostic_catalog import (
    Diagnostic,
    NEECategory
)

class TestNEECategoryEnum:
    
    def test_category_from_string_valid(self):
        assert NEECategory.from_string("PHYSICAL_DISABILITY") == NEECategory.PHYSICAL_DISABILITY
        assert NEECategory.from_string("physical_disability") == NEECategory.PHYSICAL_DISABILITY
        assert NEECategory.from_string("ADHD") == NEECategory.ADHD
        assert NEECategory.from_string("adhd") == NEECategory.ADHD
        assert NEECategory.from_string("Autism_Spectrum") == NEECategory.AUTISM_SPECTRUM
    
    def test_category_from_string_invalid(self):
        with pytest.raises(ValueError, match="Categoría inválida"):
            NEECategory.from_string("INVALID_CATEGORY")
    
    def test_category_to_spanish(self):
        assert NEECategory.PHYSICAL_DISABILITY.to_spanish() == "Discapacidad Física"
        assert NEECategory.SENSORY_VISUAL.to_spanish() == "Discapacidad Sensorial Visual"
        assert NEECategory.ADHD.to_spanish() == "TDAH"
        assert NEECategory.AUTISM_SPECTRUM.to_spanish() == "Trastorno del Espectro Autista (TEA)"
        assert NEECategory.GIFTEDNESS.to_spanish() == "Superdotación"
    
    def test_all_categories_have_spanish_translation(self):
        for category in NEECategory:
            spanish = category.to_spanish()
            assert spanish is not None
            assert len(spanish) > 0
            assert spanish != category.name  # Debe ser diferente al nombre técnico


class TestDiagnosticEntity:
    
    @pytest.fixture
    def valid_diagnostic_data(self):
        return {
            "id": None,
            "code": "DSL001",
            "name": "Dislexia",
            "category": NEECategory.SPECIFIC_LEARNING_DISORDER,
            "description": "Dificultad específica en lectoescritura",
            "normative_reference": "Decreto 1421/2017",
            "is_active": True,
        }
    
    def test_create_diagnostic_with_enum(self, valid_diagnostic_data):
        diagnostic = Diagnostic(**valid_diagnostic_data)
        
        assert diagnostic.code == "DSL001"
        assert diagnostic.name == "Dislexia"
        assert diagnostic.category == NEECategory.SPECIFIC_LEARNING_DISORDER
        assert diagnostic.is_active is True
        assert diagnostic.description == "Dificultad específica en lectoescritura"
    
    def test_create_diagnostic_with_string_category(self, valid_diagnostic_data):
        valid_diagnostic_data["category"] = "ADHD"
        
        diagnostic = Diagnostic(**valid_diagnostic_data)
        
        assert diagnostic.category == NEECategory.ADHD
        assert isinstance(diagnostic.category, NEECategory)
    
    def test_post_init_normalizes_code_to_uppercase(self):
        diagnostic = Diagnostic(
            id=None,
            code="dsl001",
            name="Dislexia",
            category=NEECategory.SPECIFIC_LEARNING_DISORDER,
            description="Test",
            is_active=True
        )
        
        assert diagnostic.code == "DSL001"
    
    def test_post_init_strips_code_whitespace(self):
        diagnostic = Diagnostic(
            id=None,
            code="  DSL001  ",
            name="Dislexia",
            category=NEECategory.SPECIFIC_LEARNING_DISORDER,
            description="Test",
            is_active=True
        )
        
        assert diagnostic.code == "DSL001"
    
    def test_post_init_strips_name_whitespace(self):
        diagnostic = Diagnostic(
            id=None,
            code="DSL001",
            name="  Dislexia  ",
            category=NEECategory.SPECIFIC_LEARNING_DISORDER,
            description="Test",
            is_active=True
        )
        
        assert diagnostic.name == "Dislexia"
    
    def test_post_init_sets_timestamps(self):
        diagnostic = Diagnostic(
            id=None,
            code="DSL001",
            name="Dislexia",
            category=NEECategory.SPECIFIC_LEARNING_DISORDER,
            description="Test",
            is_active=True
        )
        
        assert diagnostic.created_at is not None
        assert diagnostic.updated_at is not None
        assert isinstance(diagnostic.created_at, datetime)
        assert isinstance(diagnostic.updated_at, datetime)
    
    def test_validate_returns_true_with_valid_data(self, valid_diagnostic_data):
        diagnostic = Diagnostic(**valid_diagnostic_data)
        
        is_valid, errors = diagnostic.validate()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_returns_false_missing_code(self, valid_diagnostic_data):
        valid_diagnostic_data["code"] = ""
        diagnostic = Diagnostic(**valid_diagnostic_data)
        
        is_valid, errors = diagnostic.validate()
        
        assert is_valid is False
        assert "code" in errors
    
    def test_validate_returns_false_missing_name(self, valid_diagnostic_data):
        valid_diagnostic_data["name"] = ""
        diagnostic = Diagnostic(**valid_diagnostic_data)
        
        is_valid, errors = diagnostic.validate()
        
        assert is_valid is False
        assert "name" in errors
    
    def test_validate_returns_false_missing_description(self, valid_diagnostic_data):
        valid_diagnostic_data["description"] = ""
        diagnostic = Diagnostic(**valid_diagnostic_data)
        
        is_valid, errors = diagnostic.validate()
        
        assert is_valid is False
        assert "description" in errors
    
    def test_validate_returns_false_whitespace_description(self, valid_diagnostic_data):
        valid_diagnostic_data["description"] = "   "
        diagnostic = Diagnostic(**valid_diagnostic_data)
        
        is_valid, errors = diagnostic.validate()
        
        assert is_valid is False
        assert "description" in errors
    
    def test_validate_multiple_errors(self):
        diagnostic = Diagnostic(
            id=None,
            code="",
            name="",
            category=NEECategory.ADHD,
            description="",
            is_active=True
        )
        
        is_valid, errors = diagnostic.validate()
        
        assert is_valid is False
        assert len(errors) == 3
        assert "code" in errors
        assert "name" in errors
        assert "description" in errors


class TestDiagnosticBusinessRules:
    
    @pytest.fixture
    def active_diagnostic(self):
        return Diagnostic(
            id=1,
            code="DSL001",
            name="Dislexia",
            category=NEECategory.SPECIFIC_LEARNING_DISORDER,
            description="Test",
            is_active=True
        )
    
    def test_can_be_used_when_active(self, active_diagnostic):
        assert active_diagnostic.can_be_used() is True
    
    def test_can_be_used_when_inactive(self, active_diagnostic):
        active_diagnostic.is_active = False
        
        assert active_diagnostic.can_be_used() is False
    
    def test_deactivate_sets_inactive(self, active_diagnostic):
        active_diagnostic.deactivate()
        
        assert active_diagnostic.is_active is False
        assert active_diagnostic.updated_at is not None
    
    def test_reactivate_sets_active(self, active_diagnostic):
        active_diagnostic.is_active = False
        
        active_diagnostic.reactivate()
        
        assert active_diagnostic.is_active is True
        assert active_diagnostic.updated_at is not None
    
    def test_deactivate_updates_timestamp(self, active_diagnostic):
        old_timestamp = active_diagnostic.updated_at
        
        active_diagnostic.deactivate()
        
        assert active_diagnostic.updated_at > old_timestamp
    
    def test_str_representation(self, active_diagnostic):
        result = str(active_diagnostic)
        
        assert "DSL001" in result
        assert "Dislexia" in result
        assert "SPECIFIC_LEARNING_DISORDER" in result
        assert "active=True" in result