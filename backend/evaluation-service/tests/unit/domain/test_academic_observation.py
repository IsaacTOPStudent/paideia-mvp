import pytest
from datetime import datetime, date, timedelta
from src.domain.entities.academic_observation import Subject, AcademicObservation


class TestSubject:

    def test_from_string_valid(self):
        result = Subject.from_string("math")

        assert result == Subject.MATH

    def test_from_string_invalid(self):
        with pytest.raises(ValueError):
            Subject.from_string("HISTORY")

    def test_from_string_empty(self):
        with pytest.raises(ValueError):
            Subject.from_string("")

    def test_to_spanish(self):
        assert Subject.MATH.to_spanish() == "Matemáticas"
        assert Subject.ENGLISH.to_spanish() == "Inglés"

class TestObservationEntity:
    @pytest.fixture
    def create_observation(self):

        now = datetime.now()

        return AcademicObservation(
            student_id=1,
            teacher_id=10,
            observation_date=date.today(),
            subject=Subject.MATH,
            performance_description="Buen desempeño académico",
            behavioral_notes="Participa activamente en clase",
            pedagogical_adjustments_applied="Apoyo visual",
            recommendations="Continuar seguimiento",
            created_at=now,
            updated_at=now,
        )


    def test_validate_valid_observation(self, create_observation):

        observation = create_observation

        is_valid, errors = observation.validate()

        assert is_valid is True
        assert errors == []

    def test_validate_future_date(self, create_observation):

        observation = create_observation

        observation.observation_date = (
            date.today() + timedelta(days=1)
        )

        is_valid, errors = observation.validate()

        assert is_valid is False

        assert (
            "La fecha de observación no puede ser futura."
            in errors
        )

    def test_validate_empty_performance_description(self, create_observation):

        observation = create_observation

        observation.performance_description = ""

        is_valid, errors = observation.validate()

        assert is_valid is False
        assert "performance_description" in errors

    def test_validate_behavioral_notes_required(self, create_observation):

        observation = create_observation

        observation.behavioral_notes = ""

        is_valid, errors = observation.validate()

        assert is_valid is False

        assert (
            "Las observaciones conductuales son obligatorias."
            in errors
        )

    def test_deactivate(self, create_observation):

        observation = create_observation

        observation.deactivate()

        assert observation.is_active is False 

    def test_can_be_deleted(self, create_observation):

        observation = create_observation

        assert observation.can_be_deleted() is False

    def test_string_representation(self, create_observation):

        observation = create_observation

        result = str(observation)

        assert "AcademicObservation" in result
        assert "Matemáticas" in result
