import pytest
from unittest.mock import Mock
from datetime import date

from src.application.use_cases.register_observation import (
    RegisterObservationUseCase
)
from src.domain.exceptions import InvalidObservationDataError, StudentNotFoundError

@pytest.fixture
def repository():
    return Mock()

@pytest.fixture
def student_service():
    return Mock()

@pytest.fixture
def characterization_service():
    return Mock()

@pytest.fixture
def use_case(
    repository,
    student_service,
    characterization_service
):
    return RegisterObservationUseCase(
        repository,
        student_service,
        characterization_service
    )

@pytest.fixture
def valid_data():
    return {
        "student_id": 1,
        "observation_date": date.today(),
        "subject": "MATH",
        "performance_description":
            "Desempeño adecuado durante la clase",
        "behavioral_notes":
            "Comportamiento apropiado durante la jornada",
        "pedagogical_adjustments_applied":
            "Apoyo visual",
        "recommendations":
            "Continuar seguimiento",
    }

def test_register_observation_success(
    use_case,
    repository,
    student_service,
    characterization_service,
    valid_data
):
    student_service.get_student_info.return_value = Mock(
        id=1,
        is_active=True
    )

    characterization_service.get_characterizations.return_value = [
        Mock()
    ]

    repository.save.side_effect = lambda obs: obs

    observation, warning = use_case.execute(
        data=valid_data,
        teacher_id=10,
        requester_role="TEACHER"
    )

    assert observation.student_id == 1
    assert observation.teacher_id == 10
    assert warning is None

    repository.save.assert_called_once()

def test_register_observation_without_characterizations_returns_warning(
    use_case,
    repository,
    student_service,
    characterization_service,
    valid_data
):
    student_service.get_student_info.return_value = Mock(
        id=1,
        is_active=True
    )

    characterization_service.get_characterizations.return_value = []

    repository.save.side_effect = lambda obs: obs

    _, warning = use_case.execute(
        data=valid_data,
        teacher_id=10,
        requester_role="TEACHER"
    )

    assert warning is not None

def test_register_observation_rejects_non_teacher(
    use_case,
    valid_data
):
    with pytest.raises(
        InvalidObservationDataError
    ):
        use_case.execute(
            data=valid_data,
            teacher_id=10,
            requester_role="PSYCHOLOGIST"
        )

def test_register_observation_requires_student_id(
    use_case,
):
    with pytest.raises(
        InvalidObservationDataError
    ):
        use_case.execute(
            data={},
            teacher_id=10,
            requester_role="TEACHER"
        )

def test_register_observation_student_not_found(
    use_case,
    student_service,
    valid_data
):
    student_service.get_student_info.return_value = None

    with pytest.raises(StudentNotFoundError):
        use_case.execute(
            data=valid_data,
            teacher_id=10,
            requester_role="TEACHER"
        )

def test_register_observation_student_inactive(
    use_case,
    student_service,
    valid_data
):
    student_service.get_student_info.return_value = Mock(
        id=1,
        is_active=False
    )

    with pytest.raises(StudentNotFoundError):
        use_case.execute(
            data=valid_data,
            teacher_id=10,
            requester_role="TEACHER"
        )

def test_register_observation_requires_date(
    use_case,
    student_service,
    valid_data
):
    student_service.get_student_info.return_value = Mock(
        id=1,
        is_active=True
    )

    valid_data.pop("observation_date")

    with pytest.raises(
        InvalidObservationDataError
    ):
        use_case.execute(
            data=valid_data,
            teacher_id=10,
            requester_role="TEACHER"
        )

def test_register_observation_invalid_subject(
    use_case,
    student_service,
    valid_data
):
    student_service.get_student_info.return_value = Mock(
        id=1,
        is_active=True
    )

    valid_data["subject"] = "INVALID"

    with pytest.raises(
        InvalidObservationDataError
    ):
        use_case.execute(
            data=valid_data,
            teacher_id=10,
            requester_role="TEACHER"
        )

def test_register_observation_entity_validation_error(
    use_case,
    repository,
    student_service,
    characterization_service,
    valid_data
):
    student_service.get_student_info.return_value = Mock(
        id=1,
        is_active=True
    )

    characterization_service.get_characterizations.return_value = []

    valid_data["performance_description"] = "abc"

    with pytest.raises(
        InvalidObservationDataError
    ):
        use_case.execute(
            data=valid_data,
            teacher_id=10,
            requester_role="TEACHER"
        )