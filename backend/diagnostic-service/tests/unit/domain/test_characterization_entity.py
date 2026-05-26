
import pytest
from datetime import date, datetime
from django.utils import timezone

from src.domain.entities.characterization import (
    Characterization,
    SeverityLevel

)

class TestSeverityLevelEnum:
    
    def test_severity_level_from_string_valid(self):
        assert SeverityLevel.from_string("MILD") == SeverityLevel.MILD
        assert SeverityLevel.from_string("mild") == SeverityLevel.MILD
        assert SeverityLevel.from_string("Moderate") == SeverityLevel.MODERATE
        assert SeverityLevel.from_string("SEVERE") == SeverityLevel.SEVERE
    
    def test_severity_level_from_string_invalid(self):
        with pytest.raises(ValueError, match="Nivel de severidad inválido"):
            SeverityLevel.from_string("INVALID")
    
    def test_severity_level_to_spanish(self):
        assert SeverityLevel.MILD.to_spanish() == "Leve"
        assert SeverityLevel.MODERATE.to_spanish() == "Moderado"
        assert SeverityLevel.SEVERE.to_spanish() == "Severo"


class TestCharacterizationEntity:
    
    @pytest.fixture
    def valid_characterization_data(self):
        return {
            "id": None,
            "student_id": 1,
            "diagnostic_id": 10,
            "severity_level": SeverityLevel.MODERATE,
            "identification_date": date(2026, 5, 1),
            "observations": "Requiere apoyo en lectura",
            "cognitive_area_notes": "Dificultad en comprensión lectora",
            "is_active": True,
            "created_by": 5,
        }
    
    def test_create_characterization_with_enum(self, valid_characterization_data):
        char = Characterization(**valid_characterization_data)
        
        assert char.student_id == 1
        assert char.diagnostic_id == 10
        assert char.severity_level == SeverityLevel.MODERATE
        assert char.is_active is True
    
    def test_create_characterization_with_string_severity(self, valid_characterization_data):
        valid_characterization_data["severity_level"] = "MILD"
        
        char = Characterization(**valid_characterization_data)
        
        assert char.severity_level == SeverityLevel.MILD
        assert isinstance(char.severity_level, SeverityLevel)
    
    def test_post_init_sets_timestamps(self):
        char = Characterization(
            id=None,
            student_id=1,
            diagnostic_id=10,
            severity_level=SeverityLevel.MILD,
            identification_date=date.today(),
        )
        
        assert char.created_at is not None
        assert char.updated_at is not None
        assert isinstance(char.created_at, datetime)
    
    def test_post_init_strips_observations(self):
        char = Characterization(
            id=None,
            student_id=1,
            diagnostic_id=10,
            severity_level=SeverityLevel.MILD,
            identification_date=date.today(),
            observations="  Texto con espacios  ",
        )
        
        assert char.observations == "Texto con espacios"
    
    def test_validate_returns_true_with_valid_data(self, valid_characterization_data):
        char = Characterization(**valid_characterization_data)
        
        is_valid, errors = char.validate()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_returns_false_missing_student_id(self, valid_characterization_data):
        valid_characterization_data["student_id"] = None
        char = Characterization(**valid_characterization_data)
        
        is_valid, errors = char.validate()
        
        assert is_valid is False
        assert "student_id" in errors
    
    def test_validate_returns_false_missing_diagnostic_id(self, valid_characterization_data):
        valid_characterization_data["diagnostic_id"] = None
        char = Characterization(**valid_characterization_data)
        
        is_valid, errors = char.validate()
        
        assert is_valid is False
        assert "diagnostic_id" in errors
    
    def test_validate_returns_false_missing_identification_date(self, valid_characterization_data):
        valid_characterization_data["identification_date"] = None
        char = Characterization(**valid_characterization_data)
        
        is_valid, errors = char.validate()
        
        assert is_valid is False
        assert "identification_date" in errors
    
    def test_validate_multiple_errors(self):
        char = Characterization(
            id=None,
            student_id=None,
            diagnostic_id=None,
            severity_level=SeverityLevel.MILD,
            identification_date=None,
        )
        
        is_valid, errors = char.validate()
        
        assert is_valid is False
        assert len(errors) == 3
        assert "student_id" in errors
        assert "diagnostic_id" in errors
        assert "identification_date" in errors


class TestCharacterizationBusinessRules:
    
    @pytest.fixture
    def active_characterization(self):
        return Characterization(
            id=1,
            student_id=10,
            diagnostic_id=5,
            severity_level=SeverityLevel.MODERATE,
            identification_date=date.today(),
            is_active=True,
            created_by=1,
        )
    
    def test_can_be_used_when_active(self, active_characterization):
        assert active_characterization.can_be_used() is True
    
    def test_can_be_used_when_inactive(self, active_characterization):
        active_characterization.is_active = False
        
        assert active_characterization.can_be_used() is False
    
    def test_can_be_deleted_always_false(self, active_characterization):
        assert active_characterization.can_be_deleted() is False
    
    def test_mark_as_inactive_by_admin(self, active_characterization):
        admin_id = 99
        
        active_characterization.mark_as_inactive(admin_id)
        
        assert active_characterization.is_active is False
        assert active_characterization.updated_by == admin_id
        assert active_characterization.updated_at is not None
    
    def test_reactivate_by_admin(self, active_characterization):
        admin_id = 99
        active_characterization.is_active = False
        
        active_characterization.reactivate(admin_id)
        
        assert active_characterization.is_active is True
        assert active_characterization.updated_by == admin_id
    
    def test_severity_in_spanish_property(self, active_characterization):
        active_characterization.severity_level = SeverityLevel.MILD
        
        assert active_characterization.severity_in_spanish == "Leve"