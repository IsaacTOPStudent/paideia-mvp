import pytest
from django.utils import timezone
from students.models import StudentModel
from src.infrastructure.repositories.django_student_repository import DjangoStudentRepository
from src.domain.entities.student import Student, Gender
from src.domain.exceptions import StudentAlreadyExistsError

@pytest.mark.django_db
class TestDjangoStudentRepository:
    
    @pytest.fixture
    def repository(self):
        return DjangoStudentRepository()
    
    def test_save_new_student(self, repository, valid_student_data):

        student = Student(**valid_student_data)
        
        saved_student = repository.save(student)
        
        assert saved_student.id is not None
        assert StudentModel.objects.filter(document_number='1234567890').exists()
        
        db_student = StudentModel.objects.get(document_number='1234567890')
        assert db_student.first_name == 'Juan'
        assert db_student.last_name == 'Pérez'
        assert db_student.consent_given is True
    
    def test_save_duplicate_document_raises_error(self, repository, valid_student_data):

        student1 = Student(**valid_student_data)
        repository.save(student1)
        
        student2 = Student(**valid_student_data)
        student2.id = None  # Asegurar que es nuevo
        
        with pytest.raises(StudentAlreadyExistsError):
            repository.save(student2)
    
    def test_update_existing_student(self, repository, valid_student_data):

        student = Student(**valid_student_data)
        saved_student = repository.save(student)
        
        saved_student.first_name = 'Pedro'
        saved_student.grade = '6°'
        
        updated_student = repository.save(saved_student)
        
        assert updated_student.first_name == 'Pedro'
        assert updated_student.grade == '6°'
        
        db_student = StudentModel.objects.get(id=saved_student.id)
        assert db_student.first_name == 'Pedro'
        assert db_student.grade == '6°'
    
    def test_find_by_id_existing(self, repository, valid_student_data):

        student = Student(**valid_student_data)
        saved_student = repository.save(student)
        
        found_student = repository.find_by_id(saved_student.id)
        
        assert found_student is not None
        assert found_student.id == saved_student.id
        assert found_student.document_number == '1234567890'
    
    def test_find_by_id_non_existing(self, repository):

        result = repository.find_by_id(999999)
        
        assert result is None
    
    def test_find_by_document_existing(self, repository, valid_student_data):

        # Crear estudiante
        student = Student(**valid_student_data)
        repository.save(student)
        
        # Buscar
        found_student = repository.find_by_document('1234567890')
        
        assert found_student is not None
        assert found_student.document_number == '1234567890'
        assert found_student.first_name == 'Juan'
    
    def test_find_by_document_non_existing(self, repository):

        result = repository.find_by_document('9999999999')
        
        assert result is None
    
    def test_find_all_active_students(self, repository, valid_student_data):

        student1 = Student(**valid_student_data)
        repository.save(student1)
        
        data2 = valid_student_data.copy()
        data2['document_number'] = '9876543210'
        student2 = Student(**data2)
        repository.save(student2)
        
        data3 = valid_student_data.copy()
        data3['document_number'] = '1111111111'
        data3['is_active'] = False
        student3 = Student(**data3)
        repository.save(student3)
        
        active_students = repository.find_all()
        
        assert len(active_students) == 2
        assert all(s.is_active for s in active_students)
    
    def test_find_all_including_inactive(self, repository, valid_student_data):

        student1 = Student(**valid_student_data)
        repository.save(student1)
        
        data2 = valid_student_data.copy()
        data2['document_number'] = '9876543210'
        data2['is_active'] = False
        student2 = Student(**data2)
        repository.save(student2)
        
        all_students = repository.find_all_including_inactive()

        assert len(all_students) == 2
        assert any(not s.is_active for s in all_students)
    
    def test_exists_by_document_true(self, repository, valid_student_data):

        student = Student(**valid_student_data)
        repository.save(student)

        assert repository.exists_by_document('1234567890') is True
    
    def test_exists_by_document_false(self, repository):

        assert repository.exists_by_document('9999999999') is False
    
    def test_entity_to_model_conversion(self, repository, valid_student_data):

        student = Student(**valid_student_data)
        saved_student = repository.save(student)

        db_model = StudentModel.objects.get(id=saved_student.id)

        assert db_model.document_number == student.document_number
        assert db_model.first_name == student.first_name
        assert db_model.gender == student.gender.value
        assert db_model.consent_given == student.consent_given
    
    def test_model_to_entity_conversion(self, repository):

        db_model = StudentModel.objects.create(
            document_type='TI',
            document_number='5555555555',
            first_name='Ana',
            last_name='López',
            date_of_birth='2012-03-20',
            gender='FEMALE',
            grade='3°',
            guardian_name='Carlos López',
            guardian_phone='3009876543',
            consent_given=True,
            consent_date=timezone.now(),
            is_active=True
        )

        student = repository.find_by_id(db_model.id)

        assert isinstance(student.gender, Gender)
        assert student.gender == Gender.FEMALE
        assert student.first_name == 'Ana'
        assert student.is_active is True