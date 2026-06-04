from typing import Optional, List
from datetime import datetime 
from students.models import StudentModel
from src.domain.entities.student import Student, Gender
from src.domain.ports.student_repository import StudentRepository
from src.domain.exceptions import StudentAlreadyExistsError

class DjangoStudentRepository(StudentRepository):
    """
       Adapter: Student repository using Django ORM 
    """

    def save(self, student: Student) -> Student:
        """Save or update student"""
        try:
            if student.id:
                # Actualizar
                obj = StudentModel.objects.get(id=student.id)
                obj.document_number = student.document_number
                obj.document_type = student.document_type
                obj.first_name = student.first_name
                obj.last_name = student.last_name
                obj.date_of_birth = student.date_of_birth
                obj.gender = student.gender.value
                obj.grade = student.grade
                obj.section = student.section
                obj.guardian_name = student.guardian_name
                obj.guardian_phone = student.guardian_phone
                obj.guardian_email = student.guardian_email
                obj.guardian_relationship = student.guardian_relationship
                obj.consent_given = student.consent_given
                obj.consent_date = student.consent_date
                obj.address = student.address
                obj.neighborhood = student.neighborhood
                obj.city = student.city
                obj.socioeconomic_stratum = student.socioeconomic_stratum
                obj.is_active = student.is_active
                obj.updated_at = student.updated_at
                obj.save()
            else:
                # Crear
                obj = StudentModel.objects.create(
                    document_number=student.document_number,
                    document_type=student.document_type,
                    first_name=student.first_name,
                    last_name=student.last_name,
                    date_of_birth=student.date_of_birth,
                    gender=student.gender.value,
                    grade=student.grade,
                    section=student.section,
                    guardian_name=student.guardian_name,
                    guardian_phone=student.guardian_phone,
                    guardian_email=student.guardian_email,
                    guardian_relationship=student.guardian_relationship,
                    consent_given=student.consent_given,
                    consent_date=student.consent_date,
                    address=student.address,
                    neighborhood=student.neighborhood,
                    city=student.city,
                    socioeconomic_stratum=student.socioeconomic_stratum,
                    is_active=student.is_active
                )
                student.id = obj.pk
            
            return student
        
        except Exception as e:
            if 'unique constraint' in str(e).lower():
                raise StudentAlreadyExistsError(student.document_number)
            raise 

    def find_by_id(self, student_id: int) -> Optional[Student]:
        try:
            obj = StudentModel.objects.get(id=student_id)
            return self._to_entity(obj)
        except StudentModel.DoesNotExist:
            return None
        
    def find_by_document(self, document: str) -> Optional[Student]:
        """Buscar por documento (RN-02)"""
        try:
            obj = StudentModel.objects.get(document_number=document)
            return self._to_entity(obj)
        except StudentModel.DoesNotExist:
            return None
        
    def find_all(self) -> List[Student]:
        """Listar activos"""
        return [self._to_entity(obj) for obj in StudentModel.objects.filter(is_active=True)]
    
    def find_all_including_inactive(self) -> List[Student]:
        """Listar todos"""
        return [self._to_entity(obj) for obj in StudentModel.objects.all()]
    
    def exists_by_document(self, document: str) -> bool:
        return StudentModel.objects.filter(document_number=document).exists()
    
    
    @staticmethod
    def _to_entity(model: StudentModel) -> Student:
        """Convert model to entity"""
        return Student(
            id=model.pk,
            document_number=model.document_number,
            document_type=model.document_type,
            first_name=model.first_name,
            last_name=model.last_name,
            date_of_birth=model.date_of_birth,
            gender=Gender.from_string(model.gender),
            grade=model.grade,
            section=model.section,
            guardian_name=model.guardian_name,
            guardian_phone=model.guardian_phone,
            guardian_email=model.guardian_email,
            guardian_relationship=model.guardian_relationship,
            consent_given=model.consent_given,
            consent_date=model.consent_date,
            address=model.address,
            neighborhood=model.neighborhood,
            city=model.city,
            socioeconomic_stratum=model.socioeconomic_stratum,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_active=model.is_active
        )

    
    