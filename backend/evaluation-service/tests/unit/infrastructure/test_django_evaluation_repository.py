from datetime import date, datetime, timedelta

import pytest

from src.domain.entities.psychological_evaluation import (
    PsychologicalEvaluation,
    FollowUpFrequency,
)

from src.infrastructure.repositories.django_evaluation_repository import DjangoEvaluationRepository

from datetime import date, datetime, timedelta

from src.domain.entities.psychological_evaluation import (
    PsychologicalEvaluation,
    FollowUpFrequency,
)


class EvaluationFactory:

    @staticmethod
    def build(
        student_id: int = 1,
        psychologist_id: int = 10,
        evaluation_date=None,
        next_evaluation_date=None,
        is_active: bool = True,
        **kwargs
    ) -> PsychologicalEvaluation:

        today = date.today()

        return PsychologicalEvaluation(
            student_id=student_id,
            psychologist_id=psychologist_id,
            evaluation_date=evaluation_date or today,
            instrument_used="WISC-V",
            findings="Hallazgos suficientemente extensos",
            recommendations="Recomendaciones suficientemente extensas",
            cognitive_assessment="Normal",
            emotional_assessment=None,
            behavioral_assessment=None,
            motor_assessment=None,
            social_assessment=None,
            follow_up_frequency=FollowUpFrequency.MONTHLY,
            next_evaluation_date=(
                next_evaluation_date
                or today + timedelta(days=30)
            ),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=is_active,
            **kwargs
        )
    


@pytest.fixture
def evaluation_entity():
    return EvaluationFactory.build()

@pytest.fixture
def repository():
    return DjangoEvaluationRepository()

@pytest.mark.django_db
def test_save_creates_evaluation(
    repository,
    evaluation_entity
):
    result = repository.save(evaluation_entity)

    assert result.id is not None

    assert result.student_id == 1
    assert result.psychologist_id == 10

    assert result.instrument_used == "WISC-V"

@pytest.mark.django_db
def test_save_updates_evaluation(
    repository,
    evaluation_entity
):
    saved = repository.save(evaluation_entity)

    saved.instrument_used = "VINELAND"

    updated = repository.save(saved)

    assert updated.id == saved.id
    assert updated.instrument_used == "VINELAND"

@pytest.mark.django_db
def test_find_by_id_returns_evaluation(
    repository,
    evaluation_entity
):
    saved = repository.save(evaluation_entity)

    result = repository.find_by_id(saved.id)

    assert result is not None
    assert result.id == saved.id

@pytest.mark.django_db
def test_find_by_id_returns_none_when_not_found(
    repository
):
    result = repository.find_by_id(9999)

    assert result is None

@pytest.mark.django_db
def test_find_by_student(
    repository
):
    first = EvaluationFactory.build(evaluation_date=date.today())
    second = EvaluationFactory.build(
        evaluation_date=date.today() - timedelta(days=10),
        next_evaluation_date=date.today() + timedelta(days=60),
    )
    repository.save(first)
    repository.save(second)

    result = repository.find_by_student(1)

    assert len(result) == 2
    assert result[0].evaluation_date > result[1].evaluation_date

@pytest.mark.django_db
def test_find_active_by_student(
    repository,
):
    active = EvaluationFactory.build(is_active=True)

    inactive = EvaluationFactory.build(
        is_active=False,
        evaluation_date=date.today() - timedelta(days=5),
        next_evaluation_date=date.today() + timedelta(days=20),
    )

    repository.save(active)
    repository.save(inactive)

    result = repository.find_active_by_student(1)

    assert len(result) == 1
    assert result[0].is_active is True

@pytest.mark.django_db
def test_find_latest_by_student(
    repository,

):
    old_eval = EvaluationFactory.build(
        evaluation_date=date.today() - timedelta(days=30),
        next_evaluation_date=date.today() + timedelta(days=15),
    )
    latest_eval = EvaluationFactory.build(
        evaluation_date=date.today(),
        next_evaluation_date=date.today() + timedelta(days=60),
    )

    repository.save(old_eval)
    repository.save(latest_eval)

    result = repository.find_latest_by_student(1)

    assert result is not None
    assert result.evaluation_date == date.today()

@pytest.mark.django_db
def test_find_latest_by_student_returns_none(
    repository
):
    result = repository.find_latest_by_student(999)

    assert result is None

@pytest.mark.django_db
def test_has_evaluations_true(
    repository,
    evaluation_entity
):
    repository.save(evaluation_entity)

    assert repository.has_evaluations(1) is True

@pytest.mark.django_db
def test_has_evaluations_false(
    repository
):
    assert repository.has_evaluations(999) is False


