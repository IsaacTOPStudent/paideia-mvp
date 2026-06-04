from django.utils import timezone
from typing import Optional
from src.domain.entities.student import Student
from src.domain.ports.student_repository import StudentRepository
from src.domain.exceptions import (
    InvalidStudentDataError, 
    StudentAlreadyExistsError
)

class RegisterStudentUseCase:

    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self, data: dict) -> Student:

        if self.repository.exists_by_document(data.get('document_number', '')):
            raise StudentAlreadyExistsError(data['document_number'])
        
        if not data.get('consent_given'):
            raise InvalidStudentDataError(
                "Debe confirmar el consentimiento informado del acudiente para continuar"
            )
        
        student = Student(
            id=None,
            document_number=data.get('document_number', '').strip(),
            document_type=data.get('document_type', 'TI'),
            first_name=data.get('first_name', '').strip(),
            last_name=data.get('last_name', '').strip(),
            date_of_birth=data.get('date_of_birth', ''),
            gender=data.get('gender', ''),
            grade=data.get('grade', ''),
            section=data.get('section'),
            guardian_name=data.get('guardian_name', '').strip(),
            guardian_phone=data.get('guardian_phone', '').strip(),
            guardian_email=data.get('guardian_email'),
            guardian_relationship=data.get('guardian_relationship'),
            consent_given=data.get('consent_given', False),
            consent_date=timezone.now(),
            address=data.get('address'),
            neighborhood=data.get('neighborhood'),
            city=data.get('city'),
            socioeconomic_stratum=data.get('socioeconomic_stratum'),
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_active=True
        )

        is_valid, missing = student.validate_for_registration()
        if not is_valid:
            raise InvalidStudentDataError(
                f"Campos obligatorios faltantes: {', '.join(missing)}"
            )
        
        return self.repository.save(student)