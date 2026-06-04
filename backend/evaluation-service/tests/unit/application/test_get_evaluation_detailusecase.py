import pytest
from unittest.mock import Mock

from src.application.use_cases.evaluation_detail import (
    GetEvaluationUseCase,
)

from src.domain.exceptions import (
    EvaluationNotFoundError,
)

from tests.factories.evaluation_factory import (
    EvaluationFactory,
)

@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def use_case(repository):
    return GetEvaluationUseCase(repository)

def test_get_evaluation_success(
    use_case,
    repository
):
    evaluation = EvaluationFactory.build()

    repository.find_by_id.return_value = evaluation

    result = use_case.execute(1)

    assert result == evaluation

    assert result.student_id == evaluation.student_id
    assert result.psychologist_id == evaluation.psychologist_id
    assert result.instrument_used == evaluation.instrument_used
    assert result.follow_up_frequency == evaluation.follow_up_frequency

    repository.find_by_id.assert_called_once_with(1)

def test_get_evaluation_not_found(
    use_case,
    repository
):
    repository.find_by_id.return_value = None

    with pytest.raises(EvaluationNotFoundError):
        use_case.execute(999)

    repository.find_by_id.assert_called_once_with(999)
