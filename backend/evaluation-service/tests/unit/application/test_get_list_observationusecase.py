import pytest
from unittest.mock import Mock

from src.application.use_cases.list_observations import (
    ListObservationsUseCase,
)

from src.domain.exceptions import (
    StudentNotFoundError,
    InvalidObservationDataError,
)

from tests.factories.student_factory import (
    StudentFactory,
)

from tests.factories.observation_factory import (
    ObservationFactory,
)

@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def student_service():
    return Mock()


@pytest.fixture
def use_case(
    repository,
    student_service
):
    return ListObservationsUseCase(
        repository,
        student_service
    )

def test_invalid_student_id_raises_error(
    use_case
):
    with pytest.raises(
        InvalidObservationDataError
    ):
        use_case.execute(
            student_id=0,
            requester_id=1,
            requester_role="ADMIN"
        )

def test_student_not_found(
    use_case,
    student_service
):
    student_service.get_student_info.return_value = None

    with pytest.raises(
        StudentNotFoundError
    ):
        use_case.execute(
            student_id=999,
            requester_id=1,
            requester_role="ADMIN"
        )

def test_inactive_student_raises_error(
    use_case,
    student_service
):
    student_service.get_student_info.return_value = (
        StudentFactory.build(
            is_active=False
        )
    )

    with pytest.raises(
        StudentNotFoundError
    ):
        use_case.execute(
            student_id=1,
            requester_id=1,
            requester_role="ADMIN"
        )

def test_teacher_lists_own_observations(
    use_case,
    repository,
    student_service
):
    student_service.get_student_info.return_value = (
        StudentFactory.build()
    )

    observations = [
        ObservationFactory.build(),
        ObservationFactory.build(),
    ]

    repository.find_by_student_and_teacher.return_value = observations

    result = use_case.execute(
        student_id=1,
        requester_id=15,
        requester_role="TEACHER"
    )

    assert result == observations

    repository.find_by_student_and_teacher.assert_called_once_with(
        student_id=1,
        teacher_id=15
    )

    repository.find_active_by_student.assert_not_called()
    repository.find_by_student.assert_not_called()

def test_admin_lists_active_observations(
    use_case,
    repository,
    student_service
):
    student_service.get_student_info.return_value = (
        StudentFactory.build()
    )

    observations = [
        ObservationFactory.build(),
        ObservationFactory.build(),
    ]

    repository.find_active_by_student.return_value = observations

    result = use_case.execute(
        student_id=1,
        requester_id=99,
        requester_role="ADMIN"
    )

    assert result == observations

    repository.find_active_by_student.assert_called_once_with(1)

def test_psychologist_lists_active_observations(
    use_case,
    repository,
    student_service
):
    student_service.get_student_info.return_value = (
        StudentFactory.build()
    )

    observations = [
        ObservationFactory.build()
    ]

    repository.find_active_by_student.return_value = observations

    result = use_case.execute(
        student_id=1,
        requester_id=50,
        requester_role="PSYCHOLOGIST"
    )

    assert result == observations

def test_admin_lists_all_observations(
    use_case,
    repository,
    student_service
):
    student_service.get_student_info.return_value = (
        StudentFactory.build()
    )

    observations = [
        ObservationFactory.build(),
        ObservationFactory.build(),
    ]

    repository.find_by_student.return_value = observations

    result = use_case.execute(
        student_id=1,
        requester_id=99,
        requester_role="ADMIN",
        only_active=False
    )

    assert result == observations

    repository.find_by_student.assert_called_once_with(1)

def test_teacher_returns_empty_list(
    use_case,
    repository,
    student_service
):
    student_service.get_student_info.return_value = (
        StudentFactory.build()
    )

    repository.find_by_student_and_teacher.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_id=15,
        requester_role="TEACHER"
    )

    assert result == []

def test_admin_returns_empty_list(
    use_case,
    repository,
    student_service
):
    student_service.get_student_info.return_value = (
        StudentFactory.build()
    )

    repository.find_active_by_student.return_value = []

    result = use_case.execute(
        student_id=1,
        requester_id=1,
        requester_role="ADMIN"
    )

    assert result == []

def test_repository_not_called_when_student_not_found(
    use_case,
    repository,
    student_service
):
    student_service.get_student_info.return_value = None

    with pytest.raises(
        StudentNotFoundError
    ):
        use_case.execute(
            student_id=1,
            requester_id=1,
            requester_role="ADMIN"
        )

    repository.find_active_by_student.assert_not_called()
    repository.find_by_student.assert_not_called()
    repository.find_by_student_and_teacher.assert_not_called()

def test_teacher_only_sees_own_observations(
    use_case,
    repository,
    student_service
):
    student_service.get_student_info.return_value = StudentFactory.build()

    own_observation = ObservationFactory.build(teacher_id=15)
    other_observation = ObservationFactory.build(teacher_id=99)

    repository.find_by_student_and_teacher.return_value = [own_observation]

    result = use_case.execute(
        student_id=1,
        requester_id=15,
        requester_role="TEACHER"
    )

    assert result == [own_observation]
    assert other_observation not in result

    repository.find_by_student_and_teacher.assert_called_once_with(
        student_id=1,
        teacher_id=15
    )
    repository.find_active_by_student.assert_not_called()
    repository.find_by_student.assert_not_called()