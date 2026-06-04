import pytest

from datetime import date, datetime, timedelta
from src.domain.entities.psychological_evaluation import (
    FollowUpFrequency,
    PsychologicalEvaluation,
    FollowUpStatus
)


class TestFollowUpFrequency:

    def test_from_string_valid(self):
        result = FollowUpFrequency.from_string("monthly")

        assert result == FollowUpFrequency.MONTHLY

    def test_from_string_invalid(self):
        with pytest.raises(ValueError):
            FollowUpFrequency.from_string("weekly")

    def test_from_string_empty(self):
        with pytest.raises(ValueError):
            FollowUpFrequency.from_string("")

    def test_to_spanish(self):
        assert (
            FollowUpFrequency.MONTHLY.to_spanish()
            == "Mensual"
        )

        assert (
            FollowUpFrequency.BIANNUAL.to_spanish()
            == "Semestral"
        )

class TestPsychologicalEvaluationEntity:
    @pytest.fixture
    def create_evaluation(self):

        now = datetime.now()

        return PsychologicalEvaluation(
            student_id=1,
            psychologist_id=99,
            evaluation_date=date.today(),
            instrument_used="WISC-V",
            findings="Hallazgos clínicos adecuados",
            recommendations="Seguimiento psicológico",
            cognitive_assessment="Adecuado",
            emotional_assessment=None,
            behavioral_assessment=None,
            motor_assessment=None,
            social_assessment=None,
            follow_up_frequency=FollowUpFrequency.MONTHLY,
            next_evaluation_date=date.today() + timedelta(days=30),
            created_at=now,
            updated_at=now,
        )

    def test_validate_valid_evaluation(self, create_evaluation):

        evaluation = create_evaluation

        is_valid, errors = evaluation.validate()

        assert is_valid is True
        assert errors == []

    def test_validate_requires_assessment_area(self, create_evaluation):

        evaluation = create_evaluation

        evaluation.cognitive_assessment = None
        evaluation.emotional_assessment = None
        evaluation.behavioral_assessment = None
        evaluation.motor_assessment = None
        evaluation.social_assessment = None

        is_valid, errors = evaluation.validate()

        assert is_valid is False

        assert (
            "Debe registrar al menos un área evaluada."
            in errors
        )

    def test_validate_next_date_must_be_after_evaluation(self, create_evaluation):

        evaluation = create_evaluation

        evaluation.next_evaluation_date = (
            evaluation.evaluation_date
        )

        is_valid, errors = evaluation.validate()

        assert is_valid is False

        assert (
            "La próxima fecha de evaluación debe ser posterior."
            in errors
        )

    def test_follow_up_status_pending(self, create_evaluation):

        evaluation = create_evaluation

        evaluation.next_evaluation_date = (
            date.today() - timedelta(days=1)
        )

        assert (
            evaluation.follow_up_status
            == FollowUpStatus.PENDING
        )

    def test_is_overdue(self, create_evaluation):

        evaluation = create_evaluation

        evaluation.next_evaluation_date = (
            date.today() - timedelta(days=1)
        )

        assert evaluation.is_overdue is True

    def test_days_until_next_evaluation(self, create_evaluation):

        evaluation = create_evaluation

        evaluation.next_evaluation_date = (
            date.today() + timedelta(days=15)
        )

        assert (
            evaluation.days_until_next_evaluation
            == 15
        )

    def test_deactivate(self, create_evaluation):

        evaluation = create_evaluation

        evaluation.deactivate()

        assert evaluation.is_active is False

    def test_can_be_deleted(self, create_evaluation):

        evaluation = create_evaluation

        assert evaluation.can_be_deleted() is False

