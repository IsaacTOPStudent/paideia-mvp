import pytest
from datetime import date, datetime
from unittest.mock import Mock

from src.application.use_cases.deactivate_student import (
    DeactivateStudentUseCase
)

from src.domain.entities.student import Student, Gender
from src.domain.exceptions import StudentNotFoundError


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def sample_student():
    return Student(
        id=1,
        document_type="TI",
        document_number="123456",
        first_name="Juan",
        last_name="Perez",
        date_of_birth=date(2010, 5, 20),
        gender=Gender.MALE,
        grade="5°",
        section="A",
        guardian_name="Maria Perez",
        guardian_phone="3001234567",
        guardian_email="maria@test.com",
        guardian_relationship="Madre",
        consent_given=True,
        consent_date=datetime.now(),
        address="Calle 1",
        neighborhood="Centro",
        city="Cartagena",
        socioeconomic_stratum=2,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True
    )


class TestDeactivateStudentUseCase:

    def test_deactivate_student_success(
        self,
        mock_repository,
        sample_student
    ):
        mock_repository.find_by_id.return_value = sample_student
        mock_repository.save.return_value = sample_student

        use_case = DeactivateStudentUseCase(mock_repository)

        result = use_case.execute(1)

        assert result.is_active is False

        mock_repository.find_by_id.assert_called_once_with(1)
        mock_repository.save.assert_called_once()

    def test_deactivate_student_not_found(
        self,
        mock_repository
    ):
        mock_repository.find_by_id.return_value = None

        use_case = DeactivateStudentUseCase(mock_repository)

        with pytest.raises(StudentNotFoundError):
            use_case.execute(999)