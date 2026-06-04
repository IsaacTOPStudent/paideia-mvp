from datetime import date, timedelta
from unittest.mock import Mock

import pytest

from src.application.use_cases.register_evaluation import (
    RegisterEvaluationUseCase
)

from src.domain.dto.student_info import StudentInfoDTO
from src.domain.dto.characterization_info import (
    CharacterizationInfoDTO
)

from src.domain.entities.psychological_evaluation import (
    PsychologicalEvaluation
)

from src.domain.exceptions import (
    InvalidEvaluationDataError,
    StudentNotFoundError,
    StudentNotCharacterizedError,
)

@pytest.fixture
def repository():
    repo = Mock()
    repo.save.side_effect = lambda evaluation: evaluation
    return repo


@pytest.fixture
def student_service():
    service = Mock()

    service.get_student_info.return_value = StudentInfoDTO(
        id=1,
        first_name="Juan",
        last_name="Pérez",
        document_number="123456",
        is_active=True,
    )

    return service


@pytest.fixture
def characterization_service():
    service = Mock()

    service.get_characterizations.return_value = [
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

    return service


@pytest.fixture
def use_case(
    repository,
    student_service,
    characterization_service,
):
    return RegisterEvaluationUseCase(
        repository=repository,
        student_service=student_service,
        characterization_service=characterization_service,
    )

@pytest.fixture
def valid_data():
    return {
        "student_id": 1,
        "evaluation_date": date.today(),
        "instrument_used": "WISC-V",
        "findings": "Hallazgos suficientemente detallados",
        "recommendations": "Recomendaciones suficientemente detalladas",
        "cognitive_assessment": "Área cognitiva normal",
        "emotional_assessment": None,
        "behavioral_assessment": None,
        "motor_assessment": None,
        "social_assessment": None,
        "follow_up_frequency": "MONTHLY",
        "next_evaluation_date": date.today() + timedelta(days=30),
    }

def test_register_evaluation_success(
    use_case,
    repository,
    valid_data,
):
    result = use_case.execute(
        data=valid_data,
        psychologist_id=10,
        requester_role="PSYCHOLOGIST",
    )

    assert isinstance(
        result,
        PsychologicalEvaluation
    )

    repository.save.assert_called_once()

def test_fails_when_user_is_not_psychologist(
    use_case,
    valid_data,
):
    with pytest.raises(
        InvalidEvaluationDataError,
        match="No tiene permisos"
    ):
        use_case.execute(
            data=valid_data,
            psychologist_id=10,
            requester_role="ADMIN",
        )

def test_fails_when_student_id_missing(
    use_case,
    valid_data,
):
    valid_data.pop("student_id")

    with pytest.raises(
        InvalidEvaluationDataError,
        match="El estudiante es obligatorio"
    ):
        use_case.execute(
            data=valid_data,
            psychologist_id=10,
            requester_role="PSYCHOLOGIST",
        )

def test_fails_when_evaluation_date_missing(
    use_case,
    valid_data,
):
    valid_data.pop("evaluation_date")

    with pytest.raises(
        InvalidEvaluationDataError,
        match="La fecha de evaluación es obligatoria"
    ):
        use_case.execute(
            data=valid_data,
            psychologist_id=10,
            requester_role="PSYCHOLOGIST",
        )

def test_fails_when_next_evaluation_date_missing(
    use_case,
    valid_data,
):
    valid_data.pop("next_evaluation_date")

    with pytest.raises(
        InvalidEvaluationDataError,
        match="proxima evaluación"
    ):
        use_case.execute(
            data=valid_data,
            psychologist_id=10,
            requester_role="PSYCHOLOGIST",
        )

def test_fails_when_student_not_found(
    use_case,
    student_service,
    valid_data,
):
    student_service.get_student_info.return_value = None

    with pytest.raises(StudentNotFoundError):
        use_case.execute(
            data=valid_data,
            psychologist_id=10,
            requester_role="PSYCHOLOGIST",
        )

def test_fails_when_student_inactive(
    use_case,
    student_service,
    valid_data,
):
    student_service.get_student_info.return_value = (
        StudentInfoDTO(
            id=1,
            first_name="Juan",
            last_name="Pérez",
            document_number="123456",
            is_active=False,
        )
    )

    with pytest.raises(StudentNotFoundError):
        use_case.execute(
            data=valid_data,
            psychologist_id=10,
            requester_role="PSYCHOLOGIST",
        )

def test_fails_when_student_has_no_characterization(
    use_case,
    characterization_service,
    valid_data,
):
    characterization_service.get_characterizations.return_value = []

    with pytest.raises(StudentNotCharacterizedError):
        use_case.execute(
            data=valid_data,
            psychologist_id=10,
            requester_role="PSYCHOLOGIST",
        )

def test_fails_when_frequency_invalid(
    use_case,
    valid_data,
):
    valid_data["follow_up_frequency"] = "INVALID"

    with pytest.raises(
        InvalidEvaluationDataError,
        match="Frecuencia inválida"
    ):
        use_case.execute(
            data=valid_data,
            psychologist_id=10,
            requester_role="PSYCHOLOGIST",
        )

def test_fails_when_entity_validation_fails(
    use_case,
    valid_data,
):
    valid_data["instrument_used"] = "AB"

    with pytest.raises(
        InvalidEvaluationDataError
    ):
        use_case.execute(
            data=valid_data,
            psychologist_id=10,
            requester_role="PSYCHOLOGIST",
        )

def test_saved_evaluation_contains_expected_data(
    use_case,
    repository,
    valid_data,
):
    use_case.execute(
        data=valid_data,
        psychologist_id=99,
        requester_role="PSYCHOLOGIST",
    )

    saved_evaluation = repository.save.call_args[0][0]

    assert saved_evaluation.student_id == 1
    assert saved_evaluation.psychologist_id == 99

    assert saved_evaluation.instrument_used == "WISC-V"

    assert (
        saved_evaluation.follow_up_frequency.value
        == "MONTHLY"
    )