from datetime import date, timedelta

import pytest

from evaluations.serializers import (
    PsychologicalEvaluationRegisterSerializer, 
    PsychologicalEvaluationResponseSerializer,
    AcademicObservationRegisterSerializer,
    AcademicObservationResponseSerializer,
    LongitudinalHistorySerializer
)

from src.domain.entities.academic_observation import Subject

from tests.factories.evaluation_factory import EvaluationFactory
from tests.factories.observation_factory import ObservationFactory

@pytest.fixture
def valid_data():
    return {
        "student_id": 1,
        "evaluation_date": date.today(),
        "instrument_used": "WISC-V",
        "findings": "Hallazgos suficientemente detallados",
        "recommendations": "Recomendaciones suficientemente detalladas",
        "cognitive_assessment": "Evaluación cognitiva adecuada",
        "follow_up_frequency": "MONTHLY",
        "next_evaluation_date": date.today() + timedelta(days=30),
    }

def test_serializer_is_valid_with_correct_data(valid_data):
    serializer = PsychologicalEvaluationRegisterSerializer(
        data=valid_data
    )

    assert serializer.is_valid()

def test_invalid_when_instrument_used_too_short(valid_data):
    valid_data["instrument_used"] = "AB"

    serializer = PsychologicalEvaluationRegisterSerializer(
        data=valid_data
    )

    assert not serializer.is_valid()
    assert "instrument_used" in serializer.errors

def test_invalid_when_findings_too_short(valid_data):
    valid_data["findings"] = "corto"

    serializer = PsychologicalEvaluationRegisterSerializer(
        data=valid_data
    )

    assert not serializer.is_valid()
    assert "findings" in serializer.errors

def test_invalid_when_recommendations_too_short(valid_data):
    valid_data["recommendations"] = "corto"

    serializer = PsychologicalEvaluationRegisterSerializer(
        data=valid_data
    )

    assert not serializer.is_valid()
    assert "recommendations" in serializer.errors

def test_invalid_when_follow_up_frequency_is_invalid(
    valid_data
):
    valid_data["follow_up_frequency"] = "INVALID"

    serializer = PsychologicalEvaluationRegisterSerializer(
        data=valid_data
    )

    assert not serializer.is_valid()
    assert "follow_up_frequency" in serializer.errors

def test_invalid_when_next_date_equals_evaluation_date(
    valid_data
):
    today = date.today()

    valid_data["evaluation_date"] = today
    valid_data["next_evaluation_date"] = today

    serializer = PsychologicalEvaluationRegisterSerializer(
        data=valid_data
    )

    assert not serializer.is_valid()
    assert "next_evaluation_date" in serializer.errors

def test_invalid_when_next_date_before_evaluation_date(
    valid_data
):
    valid_data["evaluation_date"] = date.today()
    valid_data["next_evaluation_date"] = (
        date.today() - timedelta(days=1)
    )

    serializer = PsychologicalEvaluationRegisterSerializer(
        data=valid_data
    )

    assert not serializer.is_valid()
    assert "next_evaluation_date" in serializer.errors

def test_invalid_when_next_date_is_past(
    valid_data
):
    valid_data["next_evaluation_date"] = (
        date.today() - timedelta(days=5)
    )

    serializer = PsychologicalEvaluationRegisterSerializer(
        data=valid_data
    )

    assert not serializer.is_valid()
    assert "next_evaluation_date" in serializer.errors

def test_invalid_when_no_assessment_area_provided(
    valid_data
):
    valid_data.pop("cognitive_assessment")

    serializer = PsychologicalEvaluationRegisterSerializer(
        data=valid_data
    )

    assert not serializer.is_valid()
    assert "assessment" in serializer.errors

def test_invalid_when_assessment_area_is_blank(
    valid_data
):
    valid_data["cognitive_assessment"] = ""

    serializer = PsychologicalEvaluationRegisterSerializer(
        data=valid_data
    )

    assert not serializer.is_valid()
    assert "assessment" in serializer.errors

def test_valid_with_emotional_assessment_only(
    valid_data
):
    valid_data.pop("cognitive_assessment")
    valid_data["emotional_assessment"] = (
        "Evaluación emocional adecuada"
    )

    serializer = PsychologicalEvaluationRegisterSerializer(
        data=valid_data
    )

    assert serializer.is_valid()


def test_evaluation_date_is_required(
    valid_data
):
    valid_data.pop("evaluation_date")

    serializer = PsychologicalEvaluationRegisterSerializer(
        data=valid_data
    )

    assert not serializer.is_valid()
    assert "evaluation_date" in serializer.errors

@pytest.fixture
def evaluation():
    return EvaluationFactory.build(
        follow_up_frequency="MONTHLY",
        next_evaluation_date=date.today() + timedelta(days=30),
    )

def test_serializer_returns_basic_fields(
    evaluation
):
    serializer = PsychologicalEvaluationResponseSerializer(
        evaluation
    )

    data = serializer.data

    assert data["student_id"] == evaluation.student_id
    assert data["psychologist_id"] == evaluation.psychologist_id
    assert data["instrument_used"] == evaluation.instrument_used
    assert data["findings"] == evaluation.findings

def test_serializer_returns_frequency_value(
    evaluation
):
    serializer = PsychologicalEvaluationResponseSerializer(
        evaluation
    )

    assert (
        serializer.data["follow_up_frequency"]
        == "MONTHLY"
    )

def test_serializer_returns_frequency_display(
    evaluation
):
    serializer = PsychologicalEvaluationResponseSerializer(
        evaluation
    )

    assert (
        serializer.data["follow_up_frequency_display"]
        == "Mensual"
    )

def test_serializer_returns_up_to_date_status():
    evaluation = EvaluationFactory.build(
        next_evaluation_date=date.today() + timedelta(days=30)
    )

    serializer = PsychologicalEvaluationResponseSerializer(
        evaluation
    )

    data = serializer.data

    assert data["follow_up_status"] == "UP_TO_DATE"
    assert data["follow_up_status_display"] == "Al día"
    assert data["is_overdue"] is False

def test_serializer_returns_pending_status():
    evaluation = EvaluationFactory.build(
        next_evaluation_date=date.today() - timedelta(days=1)
    )

    serializer = PsychologicalEvaluationResponseSerializer(
        evaluation
    )

    data = serializer.data

    assert data["follow_up_status"] == "PENDING"
    assert (
        data["follow_up_status_display"]
        == "Pendiente de actualización"
    )
    assert data["is_overdue"] is True

def test_serializer_returns_days_until_next_evaluation():
    evaluation = EvaluationFactory.build(
        next_evaluation_date=date.today() + timedelta(days=15)
    )

    serializer = PsychologicalEvaluationResponseSerializer(
        evaluation
    )

    assert (
        serializer.data["days_until_next_evaluation"]
        == 15
    )

def test_serializer_handles_optional_fields():
    evaluation = EvaluationFactory.build(
        cognitive_assessment=None,
        emotional_assessment=None,
        behavioral_assessment=None,
        motor_assessment=None,
        social_assessment=None,
    )

    serializer = PsychologicalEvaluationResponseSerializer(
        evaluation
    )

    data = serializer.data

    assert data["cognitive_assessment"] is None
    assert data["emotional_assessment"] is None
    assert data["behavioral_assessment"] is None
    assert data["motor_assessment"] is None
    assert data["social_assessment"] is None

def test_serializer_supports_dict_objects():
    data = {
        "student_id": 1,
        "psychologist_id": 10,
        "evaluation_date": date.today(),
        "instrument_used": "WISC-V",
        "findings": "Hallazgos suficientemente extensos",
        "recommendations": "Recomendaciones suficientemente extensas",
        "follow_up_frequency": "MONTHLY",
        "next_evaluation_date": (
            date.today() + timedelta(days=30)
        ),
    }

    serializer = PsychologicalEvaluationResponseSerializer(
        data
    )

    result = serializer.data

    assert result["follow_up_frequency"] == "MONTHLY"
    assert result["follow_up_frequency_display"] == "Mensual"
    assert result["follow_up_status"] == "UP_TO_DATE"

def test_serializer_supports_overdue_dict():
    data = {
        "student_id": 1,
        "psychologist_id": 10,
        "evaluation_date": date.today(),
        "instrument_used": "WISC-V",
        "findings": "Hallazgos suficientemente extensos",
        "recommendations": "Recomendaciones suficientemente extensas",
        "follow_up_frequency": "MONTHLY",
        "next_evaluation_date": (
            date.today() - timedelta(days=5)
        ),
    }

    serializer = PsychologicalEvaluationResponseSerializer(
        data
    )

    result = serializer.data

    assert result["follow_up_status"] == "PENDING"
    assert result["is_overdue"] is True

@pytest.fixture
def valid_data_():
    return {
        "student_id": 1,
        "observation_date": date.today(),
        "subject": "MATH",
        "performance_description":
            "Desempeño académico adecuado durante la clase",
        "behavioral_notes":
            "Comportamiento apropiado durante la jornada",
        "pedagogical_adjustments_applied":
            "Apoyo visual",
        "recommendations":
            "Continuar seguimiento",
    }

def test_serializer_is_valid(valid_data_):
    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert serializer.is_valid()

def test_student_id_is_required(valid_data_):
    valid_data_.pop("student_id")

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert not serializer.is_valid()
    assert "student_id" in serializer.errors

def test_observation_date_is_required(valid_data_):
    valid_data_.pop("observation_date")

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert not serializer.is_valid()
    assert "observation_date" in serializer.errors

def test_subject_is_required(valid_data_):
    valid_data_.pop("subject")

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert not serializer.is_valid()
    assert "subject" in serializer.errors

def test_subject_must_be_valid_choice(valid_data_):
    valid_data_["subject"] = "HISTORY"

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert not serializer.is_valid()
    assert "subject" in serializer.errors

def test_performance_description_too_short(
    valid_data_
):
    valid_data_["performance_description"] = "corto"

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert not serializer.is_valid()
    assert "performance_description" in serializer.errors

def test_behavioral_notes_too_short(
    valid_data_
):
    valid_data_["behavioral_notes"] = "corto"

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert not serializer.is_valid()
    assert "behavioral_notes" in serializer.errors

def test_pedagogical_adjustments_too_short(
    valid_data_
):
    valid_data_["pedagogical_adjustments_applied"] = "abc"

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert not serializer.is_valid()
    assert (
        "pedagogical_adjustments_applied"
        in serializer.errors
    )

def test_recommendations_too_short(
    valid_data_
):
    valid_data_["recommendations"] = "abc"

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert not serializer.is_valid()
    assert "recommendations" in serializer.errors

def test_pedagogical_adjustments_can_be_null(
    valid_data_
):
    valid_data_["pedagogical_adjustments_applied"] = None

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert serializer.is_valid()

def test_recommendations_can_be_null(
    valid_data_
):
    valid_data_["recommendations"] = None

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert serializer.is_valid()

def test_pedagogical_adjustments_can_be_blank(
    valid_data_
):
    valid_data_["pedagogical_adjustments_applied"] = ""

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert serializer.is_valid()

def test_recommendations_can_be_blank(
    valid_data_
):
    valid_data_["recommendations"] = ""

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert serializer.is_valid()

def test_observation_date_cannot_be_future(
    valid_data_
):
    valid_data_["observation_date"] = (
        date.today() + timedelta(days=1)
    )

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert not serializer.is_valid()
    assert "observation_date" in serializer.errors

def test_today_is_valid_observation_date(
    valid_data_
):
    valid_data_["observation_date"] = date.today()

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert serializer.is_valid()

def test_past_date_is_valid_observation_date(
    valid_data_
):
    valid_data_["observation_date"] = (
        date.today() - timedelta(days=30)
    )

    serializer = AcademicObservationRegisterSerializer(
        data=valid_data_
    )

    assert serializer.is_valid()


@pytest.fixture
def observation():
    return ObservationFactory.build(
        subject=Subject.MATH
    )

def test_serializer_returns_basic_fields(
    observation
):
    serializer = AcademicObservationResponseSerializer(
        observation
    )

    data = serializer.data

    assert data["student_id"] == observation.student_id
    assert data["teacher_id"] == observation.teacher_id

    assert (
        data["performance_description"]
        == observation.performance_description
    )

    assert (
        data["behavioral_notes"]
        == observation.behavioral_notes
    )

def test_serializer_returns_subject_value(
    observation
):
    serializer = AcademicObservationResponseSerializer(
        observation
    )

    assert serializer.data["subject"] == "MATH"

def test_serializer_returns_subject_display(
    observation
):
    serializer = AcademicObservationResponseSerializer(
        observation
    )

    assert (
        serializer.data["subject_display"]
        == "Matemáticas"
    )

def test_serializer_returns_spanish_subject_name():
    observation = ObservationFactory.build(
        subject=Subject.ENGLISH
    )

    serializer = AcademicObservationResponseSerializer(
        observation
    )

    assert (
        serializer.data["subject_display"]
        == "Inglés"
    )

def test_serializer_handles_optional_fields():
    observation = ObservationFactory.build(
        pedagogical_adjustments_applied=None,
        recommendations=None,
    )

    serializer = AcademicObservationResponseSerializer(
        observation
    )

    data = serializer.data

    assert (
        data["pedagogical_adjustments_applied"]
        is None
    )

    assert data["recommendations"] is None

def test_serializer_supports_dict_objects():
    observation = {
        "id": 1,
        "student_id": 1,
        "teacher_id": 10,
        "subject": "MATH",
        "observation_date": "2026-06-03",
        "performance_description":
            "Desempeño académico adecuado",
        "behavioral_notes":
            "Comportamiento apropiado",
        "is_active": True,
    }

    serializer = AcademicObservationResponseSerializer(
        observation
    )

    assert serializer.data["subject"] == "MATH"

    assert (
        serializer.data["subject_display"]
        == "Matemáticas"
    )

def test_serializer_returns_original_subject_when_invalid():
    observation = {
        "id": 1,
        "student_id": 1,
        "teacher_id": 10,
        "subject": "UNKNOWN_SUBJECT",
        "observation_date": "2026-06-03",
        "performance_description":
            "Desempeño académico adecuado",
        "behavioral_notes":
            "Comportamiento apropiado",
        "is_active": True,
    }

    serializer = AcademicObservationResponseSerializer(
        observation
    )

    assert (
        serializer.data["subject_display"]
        == "UNKNOWN_SUBJECT"
    )

def test_serializer_returns_string_representation_for_unknown_type():
    observation = {
        "id": 1,
        "student_id": 1,
        "teacher_id": 10,
        "subject": 123,
        "observation_date": "2026-06-03",
        "performance_description":
            "Desempeño académico adecuado",
        "behavioral_notes":
            "Comportamiento apropiado",
        "is_active": True,
    }

    serializer = AcademicObservationResponseSerializer(
        observation
    )

    assert (
        serializer.data["subject_display"]
        == "123"
    )

@pytest.fixture
def history_data():
    return {
        "student_id": 1,
        "student_info": {
            "id": 1,
            "full_name": "Juan Pérez"
        },
        "characterizations": [
            {
                "diagnostic_name": "TEA",
                "nee_category": "Comunicación"
            }
        ],
        "has_records": True,
        "follow_up_status": "Al día",
        "days_until_next_evaluation": 30,
        "evaluations": [
            EvaluationFactory.build()
        ],
        "observations": [
            ObservationFactory.build()
        ],
        "total_evaluations": 1,
        "total_observations": 1,
    }

def test_serializer_returns_basic_fields(
    history_data
):
    serializer = LongitudinalHistorySerializer(
        history_data
    )

    data = serializer.data

    assert data["student_id"] == 1

    assert data["student_info"]["full_name"] == (
        "Juan Pérez"
    )

    assert data["has_records"] is True

    assert data["total_evaluations"] == 1
    assert data["total_observations"] == 1

def test_serializer_serializes_evaluations(
    history_data
):
    serializer = LongitudinalHistorySerializer(
        history_data
    )

    data = serializer.data

    assert len(data["evaluations"]) == 1

    evaluation = data["evaluations"][0]

    assert "instrument_used" in evaluation
    assert "follow_up_status" in evaluation
    assert "follow_up_frequency" in evaluation

def test_serializer_serializes_observations(
    history_data
):
    serializer = LongitudinalHistorySerializer(
        history_data
    )

    data = serializer.data

    assert len(data["observations"]) == 1

    observation = data["observations"][0]

    assert "subject" in observation
    assert "subject_display" in observation
    assert "performance_description" in observation

def test_serializer_handles_empty_evaluations(
    history_data
):
    history_data["evaluations"] = []
    history_data["total_evaluations"] = 0

    serializer = LongitudinalHistorySerializer(
        history_data
    )

    assert serializer.data["evaluations"] == []

def test_serializer_handles_empty_observations(
    history_data
):
    history_data["observations"] = []
    history_data["total_observations"] = 0

    serializer = LongitudinalHistorySerializer(
        history_data
    )

    assert serializer.data["observations"] == []

def test_serializer_handles_no_records():
    serializer = LongitudinalHistorySerializer({
        "student_id": 1,
        "student_info": {
            "id": 1,
            "full_name": "Juan Pérez"
        },
        "characterizations": [],
        "has_records": False,
        "follow_up_status": None,
        "days_until_next_evaluation": None,
        "evaluations": [],
        "observations": [],
        "total_evaluations": 0,
        "total_observations": 0,
    })

    data = serializer.data

    assert data["has_records"] is False
    assert data["evaluations"] == []
    assert data["observations"] == []

def test_serializer_returns_characterizations(
    history_data
):
    serializer = LongitudinalHistorySerializer(
        history_data
    )

    data = serializer.data

    assert len(data["characterizations"]) == 1

    assert (
        data["characterizations"][0]["diagnostic_name"]
        == "TEA"
    )

def test_serializer_returns_follow_up_fields(
    history_data
):
    serializer = LongitudinalHistorySerializer(
        history_data
    )

    data = serializer.data

    assert data["follow_up_status"] == "Al día"
    assert data["days_until_next_evaluation"] == 30

