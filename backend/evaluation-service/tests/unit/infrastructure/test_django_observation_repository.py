
import pytest
from datetime import date, datetime, timedelta

from src.domain.entities.academic_observation import (
    AcademicObservation,
    Subject,
)
from src.infrastructure.repositories.django_observation_repository import DjangoObservationRepository

class ObservationFactory:

    @staticmethod
    def build(
        student_id: int = 1,
        teacher_id: int = 10,
        observation_date=None,
        subject: Subject = Subject.MATH,
        is_active: bool = True,
        **kwargs
    ) -> AcademicObservation:

        return AcademicObservation(
            student_id=student_id,
            teacher_id=teacher_id,
            observation_date=observation_date or date.today(),
            subject=subject,
            performance_description="Desempeño académico adecuado",
            behavioral_notes="Comportamiento adecuado en clase",
            pedagogical_adjustments_applied="Apoyo visual",
            recommendations="Continuar seguimiento",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=is_active,
            **kwargs
        )
    
@pytest.fixture
def repository():
    return DjangoObservationRepository()

@pytest.mark.django_db
def test_save_creates_observation(repository):

    observation = ObservationFactory.build()

    result = repository.save(observation)

    assert result.id is not None
    assert result.student_id == 1
    assert result.teacher_id == 10
    assert result.subject == Subject.MATH

@pytest.mark.django_db
def test_save_updates_observation(repository):

    observation = ObservationFactory.build()

    saved = repository.save(observation)

    saved.performance_description = "Nuevo desempeño"

    updated = repository.save(saved)

    assert updated.id == saved.id
    assert updated.performance_description == "Nuevo desempeño"

@pytest.mark.django_db
def test_find_by_id_returns_observation(repository):

    saved = repository.save(
        ObservationFactory.build()
    )

    result = repository.find_by_id(saved.id)

    assert result is not None
    assert result.id == saved.id

@pytest.mark.django_db
def test_find_by_id_returns_none(repository):

    result = repository.find_by_id(9999)

    assert result is None

@pytest.mark.django_db
def test_find_by_student(repository):

    repository.save(
        ObservationFactory.build(
            observation_date=date.today()
        )
    )

    repository.save(
        ObservationFactory.build(
            observation_date=date.today() - timedelta(days=10)
        )
    )

    result = repository.find_by_student(1)

    assert len(result) == 2

    assert result[0].observation_date == date.today()
    assert result[1].observation_date == (
        date.today() - timedelta(days=10)
    )

@pytest.mark.django_db
def test_find_active_by_student(repository):

    repository.save(
        ObservationFactory.build(
            is_active=True
        )
    )

    repository.save(
        ObservationFactory.build(
            is_active=False,
            observation_date=date.today() - timedelta(days=5)
        )
    )

    result = repository.find_active_by_student(1)

    assert len(result) == 1
    assert result[0].is_active is True

@pytest.mark.django_db
def test_find_by_student_and_teacher(repository):

    repository.save(
        ObservationFactory.build(
            student_id=1,
            teacher_id=10
        )
    )

    repository.save(
        ObservationFactory.build(
            student_id=1,
            teacher_id=20
        )
    )

    result = repository.find_by_student_and_teacher(
        student_id=1,
        teacher_id=10
    )

    assert len(result) == 1
    assert result[0].teacher_id == 10

@pytest.mark.django_db
def test_find_by_student_and_teacher_only_active(repository):

    repository.save(
        ObservationFactory.build(
            teacher_id=10,
            is_active=True
        )
    )

    repository.save(
        ObservationFactory.build(
            teacher_id=10,
            is_active=False,
            observation_date=date.today() - timedelta(days=1)
        )
    )

    result = repository.find_by_student_and_teacher(
        student_id=1,
        teacher_id=10
    )

    assert len(result) == 1
    assert result[0].is_active is True

