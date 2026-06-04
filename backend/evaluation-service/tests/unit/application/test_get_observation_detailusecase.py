import pytest
from unittest.mock import Mock

from src.application.use_cases.observation_detail import (
    GetObservationUseCase,
)

from src.domain.exceptions import (
    ObservationNotFoundError,
    ObservationAccessDeniedError,
)

from tests.factories.observation_factory import (
    ObservationFactory,
)

@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def use_case(repository):
    return GetObservationUseCase(repository)

def test_admin_can_view_observation(
    use_case,
    repository
):
    observation = ObservationFactory.build(
        teacher_id=15
    )

    repository.find_by_id.return_value = observation

    result = use_case.execute(
        observation_id=1,
        requester_id=999,
        requester_role="ADMIN"
    )

    assert result == observation

    repository.find_by_id.assert_called_once_with(1)

def test_psychologist_can_view_observation(
    use_case,
    repository
):
    observation = ObservationFactory.build(
        teacher_id=15
    )

    repository.find_by_id.return_value = observation

    result = use_case.execute(
        observation_id=1,
        requester_id=500,
        requester_role="PSYCHOLOGIST"
    )

    assert result == observation

def test_teacher_can_view_own_observation(
    use_case,
    repository
):
    observation = ObservationFactory.build(
        teacher_id=25
    )

    repository.find_by_id.return_value = observation

    result = use_case.execute(
        observation_id=1,
        requester_id=25,
        requester_role="TEACHER"
    )

    assert result == observation

def test_teacher_cannot_view_other_teacher_observation(
    use_case,
    repository
):
    observation = ObservationFactory.build(
        teacher_id=10
    )

    repository.find_by_id.return_value = observation

    with pytest.raises(
        ObservationAccessDeniedError
    ):
        use_case.execute(
            observation_id=1,
            requester_id=99,
            requester_role="TEACHER"
        )

def test_observation_not_found(
    use_case,
    repository
):
    repository.find_by_id.return_value = None

    with pytest.raises(
        ObservationNotFoundError
    ):
        use_case.execute(
            observation_id=999,
            requester_id=1,
            requester_role="ADMIN"
        )

    repository.find_by_id.assert_called_once_with(999)

def test_not_found_has_priority_over_permissions(
    use_case,
    repository
):
    repository.find_by_id.return_value = None

    with pytest.raises(
        ObservationNotFoundError
    ):
        use_case.execute(
            observation_id=1,
            requester_id=999,
            requester_role="TEACHER"
        )