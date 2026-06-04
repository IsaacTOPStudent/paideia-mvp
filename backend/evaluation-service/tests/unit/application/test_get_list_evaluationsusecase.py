import pytest
from unittest.mock import Mock

from src.application.use_cases.list_evaluations import (
    ListEvaluationsUseCase,
)

from src.domain.exceptions import (
    StudentNotFoundError,
)

from tests.factories.evaluation_factory import (
    EvaluationFactory,
)

from tests.factories.student_factory import (
    StudentFactory,
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
    return ListEvaluationsUseCase(
        repository,
        student_service
    )

def test_list_active_evaluations_success(
    use_case,
    repository,
    student_service
):
    student_service.get_student_info.return_value = (
        StudentFactory.build()
    )

    evaluations = [
        EvaluationFactory.build(),
        EvaluationFactory.build(),
    ]

    repository.find_active_by_student.return_value = evaluations

    result = use_case.execute(1)

    assert result == evaluations

    repository.find_active_by_student.assert_called_once_with(1)
    repository.find_by_student.assert_not_called()

def test_list_all_evaluations_success(
    use_case,
    repository,
    student_service
):
    student_service.get_student_info.return_value = (
        StudentFactory.build()
    )

    evaluations = [
        EvaluationFactory.build(),
        EvaluationFactory.build(),
    ]

    repository.find_by_student.return_value = evaluations

    result = use_case.execute(
        student_id=1,
        is_active=False
    )

    assert result == evaluations

    repository.find_by_student.assert_called_once_with(1)
    repository.find_active_by_student.assert_not_called()

def test_student_not_found(
    use_case,
    student_service
):
    student_service.get_student_info.return_value = None

    with pytest.raises(StudentNotFoundError):
        use_case.execute(999)

def test_inactive_student_raises_error(
    use_case,
    student_service
):
    student = StudentFactory.build(
        is_active=False
    )

    student_service.get_student_info.return_value = student

    with pytest.raises(StudentNotFoundError):
        use_case.execute(1)

def test_returns_empty_list_when_no_active_evaluations(
    use_case,
    repository,
    student_service
):
    student_service.get_student_info.return_value = (
        StudentFactory.build()
    )

    repository.find_active_by_student.return_value = []

    result = use_case.execute(1)

    assert result == []

def test_returns_empty_list_when_no_evaluations(
    use_case,
    repository,
    student_service
):
    student_service.get_student_info.return_value = (
        StudentFactory.build()
    )

    repository.find_by_student.return_value = []

    result = use_case.execute(
        student_id=1,
        is_active=False
    )

    assert result == []

def test_repository_is_not_called_when_student_not_found(
    use_case,
    repository,
    student_service
):
    student_service.get_student_info.return_value = None

    with pytest.raises(StudentNotFoundError):
        use_case.execute(1)

    repository.find_active_by_student.assert_not_called()
    repository.find_by_student.assert_not_called()

