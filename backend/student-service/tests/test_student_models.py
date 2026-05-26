import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from students.models import StudentModel

@pytest.mark.django_db
class TestStudentModel:
    
    def test_create_valid_student_model(self):

        student = StudentModel.objects.create(
            document_type='TI',
            document_number='1234567890',
            first_name='Juan',
            last_name='Pérez',
            date_of_birth='2010-05-15',
            gender='MALE',
            grade='5°',
            guardian_name='María García',
            guardian_phone='3001234567',
            consent_given=True,
            consent_date=timezone.now()
        )
        
        assert student.id is not None
        assert student.document_number == '1234567890'
        assert str(student) == 'Juan Pérez (1234567890)'

    def test_document_number_unique_constraint(self):

        StudentModel.objects.create(
            document_type='TI',
            document_number='1234567890',
            first_name='Juan',
            last_name='Pérez',
            date_of_birth='2010-05-15',
            gender='MALE',
            grade='5°',
            guardian_name='María',
            guardian_phone='3001234567',
            consent_given=True
        )
        
        with pytest.raises(IntegrityError):
            StudentModel.objects.create(
                document_type='TI',
                document_number='1234567890',  
                first_name='Pedro',
                last_name='González',
                date_of_birth='2011-03-20',
                gender='MALE',
                grade='4°',
                guardian_name='Ana',
                guardian_phone='3009876543',
                consent_given=True
            )

    def test_default_values(self):

        student = StudentModel.objects.create(
            document_type='TI',
            document_number='9999999999',
            first_name='Test',
            last_name='User',
            date_of_birth='2010-01-01',
            gender='MALE',
            grade='1°',
            guardian_name='Guardian',
            guardian_phone='3000000000'
        )
        
        assert student.consent_given is False
        assert student.is_active is True
        assert student.created_at is not None
        assert student.updated_at is not None

    def test_optional_fields_can_be_null(self):

        student = StudentModel.objects.create(
            document_type='TI',
            document_number='8888888888',
            first_name='Test',
            last_name='User',
            date_of_birth='2010-01-01',
            gender='MALE',
            grade='1°',
            guardian_name='Guardian',
            guardian_phone='3000000000',
            consent_given=True,

            section=None,
            guardian_email=None,
            address=None,
            city=None
        )
        
        assert student.section is None
        assert student.guardian_email is None
        assert student.address is None