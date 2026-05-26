from django.utils import timezone

from ...domain.entities.student import Student
from ...domain.ports.student_repository import StudentRepository
from ...domain.exceptions import (
    StudentNotFoundError,
    InvalidStudentDataError
)

class UpdateStudentUseCase:

    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self, student_id: int, data: dict) -> Student:

        student = self.repository.find_by_id(student_id)

        if not student:
            raise StudentNotFoundError(str(student_id))
        
        if not student.is_active:
            raise InvalidStudentDataError(
                "No se puede actualizar un estudiante inactivo"
            )
        
        student.update_data(
            first_name=data.get('first_name', student.first_name),
            last_name=data.get('last_name', student.last_name),
            grade=data.get('grade', student.grade),
            section=data.get('section', student.section),
            guardian_name=data.get(
                'guardian_name',
                student.guardian_name
            ),
            guardian_phone=data.get(
                'guardian_phone',
                student.guardian_phone
            ),
            guardian_email=data.get(
                'guardian_email',
                student.guardian_email
            ),
            guardian_relationship=data.get(
                'guardian_relationship',
                student.guardian_relationship
            ),
            address=data.get('address', student.address),
            neighborhood=data.get(
                'neighborhood',
                student.neighborhood
            ),
            city=data.get('city', student.city),
            socioeconomic_stratum=data.get(
                'socioeconomic_stratum',
                student.socioeconomic_stratum
            )
        )

        student.updated_at = timezone.now()

        is_valid, missing = student.validate_for_registration()

        if not is_valid:
            raise InvalidStudentDataError(
                f"Campos obligatorios faltantes: {', '.join(missing)}"
            )
        
        return self.repository.save(student)