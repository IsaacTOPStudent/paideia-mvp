import pytest
from datetime import date, datetime
from unittest.mock import Mock

from src.application.use_cases.update_student import UpdateStudentUseCase
from src.domain.entities.student import Student, Gender
from src.domain.exceptions import (
    StudentNotFoundError,
    InvalidStudentDataError
)


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


class TestUpdateStudentUseCase:

    def test_update_student_success(
        self,
        mock_repository,
        sample_student
    ):
        mock_repository.find_by_id.return_value = sample_student
        mock_repository.save.return_value = sample_student

        use_case = UpdateStudentUseCase(mock_repository)

        data = {
            "first_name": "Carlos",
            "grade": "6°",
            "guardian_phone": "3019999999"
        }

        result = use_case.execute(1, data)

        assert result.first_name == "Carlos"
        assert result.grade == "6°"
        assert result.guardian_phone == "3019999999"

        mock_repository.find_by_id.assert_called_once_with(1)
        mock_repository.save.assert_called_once()

    def test_update_student_not_found(self, mock_repository):
        mock_repository.find_by_id.return_value = None

        use_case = UpdateStudentUseCase(mock_repository)

        with pytest.raises(StudentNotFoundError):
            use_case.execute(999, {})

    def test_update_student_inactive(
        self,
        mock_repository,
        sample_student
    ):
        sample_student.is_active = False

        mock_repository.find_by_id.return_value = sample_student

        use_case = UpdateStudentUseCase(mock_repository)

        with pytest.raises(InvalidStudentDataError):
            use_case.execute(1, {"first_name": "Carlos"})

    def test_update_student_invalid_required_fields(
        self,
        mock_repository,
        sample_student
    ):
        mock_repository.find_by_id.return_value = sample_student

        use_case = UpdateStudentUseCase(mock_repository)

        with pytest.raises(InvalidStudentDataError):
            use_case.execute(
                1,
                {
                    "first_name": "",
                    "guardian_name": ""
                }
            )