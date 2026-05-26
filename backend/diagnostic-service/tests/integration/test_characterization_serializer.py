import pytest
from datetime import date

from diagnostics.serializers import CharacterizationSerializer
from src.domain.entities.characterization import (
    Characterization,
    SeverityLevel
)

@pytest.mark.unit
class TestCharacterizationSerializer:

    def test_serializer_returns_severity_level_as_string(self):
        characterization = Characterization(
            id=1,
            student_id=10,
            diagnostic_id=20,
            severity_level=SeverityLevel.MODERATE,
            identification_date=date(2026, 5, 1),
            observations="Observación",
            is_active=True
        )

        serializer = CharacterizationSerializer(characterization)

        assert serializer.data["severity_level"] == "MODERATE"

    def test_serializer_returns_severity_level_display_in_spanish(self):
        characterization = Characterization(
            id=1,
            student_id=10,
            diagnostic_id=20,
            severity_level=SeverityLevel.SEVERE,
            identification_date=date(2026, 5, 1),
            observations="Observación",
            is_active=True
        )

        serializer = CharacterizationSerializer(characterization)

        assert serializer.data["severity_level_display"] == "Severo"

    def test_serializer_accepts_valid_input_data(self):
        data = {
            "student_id": 1,
            "diagnostic_id": 2,
            "severity_level": "MILD",
            "identification_date": "2026-05-20",
            "observations": "Test",
            "is_active": True
        }

        serializer = CharacterizationSerializer(data=data)

        assert serializer.is_valid()

        validated = serializer.validated_data

        assert validated["student_id"] == 1
        assert validated["diagnostic_id"] == 2
        assert validated["severity_level"] == "MILD"

    def test_serializer_rejects_missing_required_fields(self):
        serializer = CharacterizationSerializer(data={})

        assert not serializer.is_valid()

        assert "student_id" in serializer.errors
        assert "diagnostic_id" in serializer.errors
        assert "severity_level" in serializer.errors
        assert "is_active" in serializer.errors

    def test_serializer_returns_original_string_for_invalid_severity_level(self):
        characterization = {
            "id": 1,
            "student_id": 1,
            "diagnostic_id": 2,
            "severity_level": "INVALID_LEVEL",
            "identification_date": "2026-05-20",
            "is_active": True
        }

        serializer = CharacterizationSerializer(characterization)

        assert serializer.data["severity_level_display"] == "INVALID_LEVEL"

    def test_serializer_returns_diagnostic_name_from_flat_field(self):
        characterization = {
            "id": 1,
            "student_id": 1,
            "diagnostic_id": 2,
            "severity_level": "MILD",
            "identification_date": "2026-05-20",
            "diagnostic_name": "Dislexia",
            "is_active": True
        }

        serializer = CharacterizationSerializer(characterization)

        assert serializer.data["diagnostic_name"] == "Dislexia"

    def test_serializer_returns_diagnostic_name_from_nested_dict(self):
        characterization = {
            "id": 1,
            "student_id": 1,
            "diagnostic_id": 2,
            "severity_level": "MILD",
            "identification_date": "2026-05-20",
            "diagnostic": {
                "name": "TDAH"
            },
            "is_active": True
        }

        serializer = CharacterizationSerializer(characterization)

        assert serializer.data["diagnostic_name"] == "TDAH"

    def test_serializer_returns_none_when_diagnostic_does_not_exist(self):
        characterization = {
            "id": 1,
            "student_id": 1,
            "diagnostic_id": 2,
            "severity_level": "MILD",
            "identification_date": "2026-05-20",
            "is_active": True
        }

        serializer = CharacterizationSerializer(characterization)

        assert serializer.data["diagnostic_name"] is None

    def test_serializer_serializes_optional_notes_fields(self):
        characterization = Characterization(
            id=1,
            student_id=10,
            diagnostic_id=20,
            severity_level=SeverityLevel.MILD,
            identification_date=date(2026, 5, 1),
            observations="General",
            cognitive_area_notes="Cognitive",
            communicative_area_notes="Communicative",
            socioemotional_area_notes="Socioemotional",
            motor_area_notes="Motor",
            sensory_area_notes="Sensory",
            academic_area_notes="Academic",
            behavioral_area_notes="Behavioral",
            is_active=True
        )

        serializer = CharacterizationSerializer(characterization)

        data = serializer.data

        assert data["cognitive_area_notes"] == "Cognitive"
        assert data["communicative_area_notes"] == "Communicative"
        assert data["socioemotional_area_notes"] == "Socioemotional"
        assert data["motor_area_notes"] == "Motor"
        assert data["sensory_area_notes"] == "Sensory"
        assert data["academic_area_notes"] == "Academic"
        assert data["behavioral_area_notes"] == "Behavioral"

    def test_serializer_serializes_basic_fields_correctly(self):
        characterization = Characterization(
            id=99,
            student_id=15,
            diagnostic_id=30,
            severity_level=SeverityLevel.MODERATE,
            identification_date=date(2026, 5, 10),
            observations="Observación clínica",
            is_active=False
        )

        serializer = CharacterizationSerializer(characterization)

        data = serializer.data

        assert data["id"] == 99
        assert data["student_id"] == 15
        assert data["diagnostic_id"] == 30
        assert data["severity_level"] == "MODERATE"
        assert data["observations"] == "Observación clínica"
        assert data["is_active"] is False