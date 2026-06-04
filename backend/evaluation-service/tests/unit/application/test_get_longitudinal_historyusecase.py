from datetime import date, timedelta
from unittest.mock import Mock

import pytest

from src.application.use_cases.get_longitudinal_history import (
    GetLongitudinalHistoryUseCase
)

from src.domain.dto.student_info import StudentInfoDTO
from src.domain.dto.characterization_info import (
    CharacterizationInfoDTO
)

from src.domain.exceptions import (
    StudentNotFoundError
)

from tests.factories.evaluation_factory import (
    EvaluationFactory
)

from tests.factories.observation_factory import (
    ObservationFactory
)

@pytest.fixture
def evaluation_repository():
    return Mock()


@pytest.fixture
def observation_repository():
    return Mock()


@pytest.fixture
def student_service():
    return Mock()


@pytest.fixture
def characterization_service():
    return Mock()

@pytest.fixture
def use_case(
    evaluation_repository,
    observation_repository,
    student_service,
    characterization_service,
):
    return GetLongitudinalHistoryUseCase(
        evaluation_repository=evaluation_repository,
        observation_repository=observation_repository,
        student_service=student_service,
        characterization_service=characterization_service,
    )

@pytest.fixture
def active_student():
    return StudentInfoDTO(
        id=1,
        first_name="Juan",
        last_name="Pérez",
        document_number="123456",
        is_active=True,
    )

def test_raises_when_student_not_found(
    use_case,
    student_service,
):
    student_service.get_student_info.return_value = None

    with pytest.raises(StudentNotFoundError):
        use_case.execute(
            student_id=1,
            requester_role="ADMIN"
        )

def test_returns_empty_history(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    student_service.get_student_info.return_value = active_student

    evaluation_repository.find_active_by_student.return_value = []
    evaluation_repository.find_latest_by_student.return_value = None

    observation_repository.find_active_by_student.return_value = []

    characterization_service.get_characterizations.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_role="ADMIN"
    )

    assert result.has_records is False

    assert result.total_evaluations == 0
    assert result.total_observations == 0

    assert result.evaluations == []
    assert result.observations == []

def test_returns_complete_history_for_admin(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    evaluation = EvaluationFactory.build()

    observation = ObservationFactory.build()

    characterization = CharacterizationInfoDTO(
        id=1,
        student_id=1,
        diagnostic_id=1,
        diagnostic_name="TDAH",
        nee_category="COGNITIVE",
        severity_level="MEDIUM",
        identification_date="2025-01-01",
        is_active=True,
    )

    student_service.get_student_info.return_value = active_student

    evaluation_repository.find_active_by_student.return_value = [
        evaluation
    ]

    evaluation_repository.find_latest_by_student.return_value = (
        evaluation
    )

    observation_repository.find_active_by_student.return_value = [
        observation
    ]

    characterization_service.get_characterizations.return_value = [
        characterization
    ]

    result = use_case.execute(
        student_id=1,
        requester_role="ADMIN"
    )

    assert result.has_records is True

    assert result.total_evaluations == 1
    assert result.total_observations == 1

    assert len(result.evaluations) == 1
    assert len(result.observations) == 1

    assert result.follow_up_status is not None

def test_teacher_cannot_see_evaluations(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    student_service.get_student_info.return_value = active_student

    evaluation_repository.find_active_by_student.return_value = [
        EvaluationFactory.build()
    ]

    observation_repository.find_active_by_student.return_value = [
        ObservationFactory.build()
    ]

    characterization_service.get_characterizations.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_role="TEACHER"
    )

    assert result.evaluations == []

    assert result.total_evaluations == 0

def test_teacher_cannot_see_follow_up_information(
    use_case,
    active_student,
    student_service,
    observation_repository,
    characterization_service,
):
    student_service.get_student_info.return_value = active_student

    observation_repository.find_active_by_student.return_value = []

    characterization_service.get_characterizations.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_role="TEACHER"
    )

    assert result.follow_up_status is None

    assert result.days_until_next_evaluation is None

def test_teacher_receives_restricted_characterizations(
    use_case,
    active_student,
    student_service,
    observation_repository,
    characterization_service,
):
    characterization_service.get_characterizations.return_value = [
        CharacterizationInfoDTO(
            id=1,
            student_id=1,
            diagnostic_id=1,
            diagnostic_name="TDAH",
            nee_category="COGNITIVE",
            severity_level="MEDIUM",
            identification_date="2025-01-01",
            is_active=True,
        )
    ]

    student_service.get_student_info.return_value = active_student

    observation_repository.find_active_by_student.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_role="TEACHER"
    )

    assert result.characterizations == [
        {
            "nee_category": "COGNITIVE",
            "diagnostic_name": "TDAH",
        }
    ]

def test_admin_receives_complete_characterizations(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    characterization_service.get_characterizations.return_value = [
        CharacterizationInfoDTO(
            id=1,
            student_id=1,
            diagnostic_id=1,
            diagnostic_name="TDAH",
            nee_category="COGNITIVE",
            severity_level="MEDIUM",
            identification_date="2025-01-01",
            is_active=True,
        )
    ]

    student_service.get_student_info.return_value = active_student

    evaluation_repository.find_active_by_student.return_value = []

    evaluation_repository.find_latest_by_student.return_value = None

    observation_repository.find_active_by_student.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_role="ADMIN"
    )

    assert result.characterizations[0]["id"] == 1

    assert (
        result.characterizations[0]["severity_level"]
        == "MEDIUM"
    )

def test_filters_observations_by_date_range(
    use_case,
    active_student,
    student_service,
    observation_repository,
    characterization_service,
):
    recent = ObservationFactory.build(
        observation_date=date.today()
    )

    old = ObservationFactory.build(
        observation_date=date.today() - timedelta(days=120)
    )

    student_service.get_student_info.return_value = active_student

    observation_repository.find_active_by_student.return_value = [
        recent,
        old,
    ]

    characterization_service.get_characterizations.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_role="TEACHER",
        start_date=date.today() - timedelta(days=30),
        end_date=date.today(),
    )

    assert len(result.observations) == 1

def test_filters_evaluations_by_date_range(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    recent = EvaluationFactory.build(
        evaluation_date=date.today()
    )

    old = EvaluationFactory.build(
        evaluation_date=date.today() - timedelta(days=200)
    )

    student_service.get_student_info.return_value = active_student

    evaluation_repository.find_active_by_student.return_value = [
        recent,
        old,
    ]

    evaluation_repository.find_latest_by_student.return_value = recent

    observation_repository.find_active_by_student.return_value = []

    characterization_service.get_characterizations.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_role="ADMIN",
        start_date=date.today() - timedelta(days=30),
        end_date=date.today(),
    )

    assert len(result.evaluations) == 1

def test_builds_student_info_correctly(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    student_service.get_student_info.return_value = active_student

    evaluation_repository.find_active_by_student.return_value = []
    evaluation_repository.find_latest_by_student.return_value = None
    observation_repository.find_active_by_student.return_value = []
    characterization_service.get_characterizations.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_role="ADMIN"
    )

    assert result.student_info == {
        "id": 1,
        "full_name": "Juan Pérez"
    }

def test_calls_student_service(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    student_service.get_student_info.return_value = active_student

    evaluation_repository.find_active_by_student.return_value = []
    evaluation_repository.find_latest_by_student.return_value = None
    observation_repository.find_active_by_student.return_value = []
    characterization_service.get_characterizations.return_value = []

    use_case.execute(
        student_id=5,
        requester_role="ADMIN"
    )

    student_service.get_student_info.assert_called_once_with(5)

def test_teacher_does_not_query_latest_evaluation(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    student_service.get_student_info.return_value = active_student

    observation_repository.find_active_by_student.return_value = []

    characterization_service.get_characterizations.return_value = []

    use_case.execute(
        student_id=1,
        requester_role="TEACHER"
    )

    evaluation_repository.find_latest_by_student.assert_not_called()

def test_teacher_does_not_query_evaluations(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    student_service.get_student_info.return_value = active_student

    observation_repository.find_active_by_student.return_value = []

    characterization_service.get_characterizations.return_value = []

    use_case.execute(
        student_id=1,
        requester_role="TEACHER"
    )

    evaluation_repository.find_active_by_student.assert_not_called()

def test_uses_latest_evaluation_for_follow_up_status(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    latest = EvaluationFactory.build()

    student_service.get_student_info.return_value = active_student

    evaluation_repository.find_active_by_student.return_value = [
        latest
    ]

    evaluation_repository.find_latest_by_student.return_value = (
        latest
    )

    observation_repository.find_active_by_student.return_value = []

    characterization_service.get_characterizations.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_role="ADMIN"
    )

    assert (
        result.follow_up_status
        == latest.follow_up_status.to_spanish()
    )

def test_returns_days_until_next_evaluation(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    evaluation = EvaluationFactory.build(
        next_evaluation_date=date.today() + timedelta(days=20)
    )

    student_service.get_student_info.return_value = active_student

    evaluation_repository.find_active_by_student.return_value = [
        evaluation
    ]

    evaluation_repository.find_latest_by_student.return_value = (
        evaluation
    )

    observation_repository.find_active_by_student.return_value = []

    characterization_service.get_characterizations.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_role="ADMIN"
    )

    assert result.days_until_next_evaluation == 20

def test_has_records_true_when_only_observations_exist(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    student_service.get_student_info.return_value = active_student

    evaluation_repository.find_active_by_student.return_value = []
    evaluation_repository.find_latest_by_student.return_value = None

    observation_repository.find_active_by_student.return_value = [
        ObservationFactory.build()
    ]

    characterization_service.get_characterizations.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_role="ADMIN"
    )

    assert result.has_records is True

def test_has_records_true_when_only_evaluations_exist(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    student_service.get_student_info.return_value = active_student

    evaluation_repository.find_active_by_student.return_value = [
        EvaluationFactory.build()
    ]

    evaluation_repository.find_latest_by_student.return_value = (
        EvaluationFactory.build()
    )

    observation_repository.find_active_by_student.return_value = []

    characterization_service.get_characterizations.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_role="ADMIN"
    )

    assert result.has_records is True

def test_has_records_true_when_only_characterizations_exist(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    student_service.get_student_info.return_value = active_student

    evaluation_repository.find_active_by_student.return_value = []
    evaluation_repository.find_latest_by_student.return_value = None

    observation_repository.find_active_by_student.return_value = []

    characterization_service.get_characterizations.return_value = [
        CharacterizationInfoDTO(
            id=1,
            student_id=1,
            diagnostic_id=1,
            diagnostic_name="TDAH",
            nee_category="COGNITIVE",
            severity_level="MEDIUM",
            identification_date="2025-01-01",
            is_active=True,
        )
    ]

    result = use_case.execute(
        student_id=1,
        requester_role="ADMIN"
    )

    assert result.has_records is True

def test_calculates_totals_correctly(
    use_case,
    active_student,
    student_service,
    evaluation_repository,
    observation_repository,
    characterization_service,
):
    student_service.get_student_info.return_value = active_student

    evaluation_repository.find_active_by_student.return_value = [
        EvaluationFactory.build(),
        EvaluationFactory.build(),
    ]

    evaluation_repository.find_latest_by_student.return_value = (
        EvaluationFactory.build()
    )

    observation_repository.find_active_by_student.return_value = [
        ObservationFactory.build(),
        ObservationFactory.build(),
        ObservationFactory.build(),
    ]

    characterization_service.get_characterizations.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_role="ADMIN"
    )

    assert result.total_evaluations == 2
    assert result.total_observations == 3