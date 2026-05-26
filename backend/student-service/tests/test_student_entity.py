import pytest 
from datetime import date, datetime
from src.domain.entities.student import Student, Gender
# from src.domain.exceptions import InvalidStudentDataError

class TestStudentEntity:
    def test_create_valid_student(self, valid_student_data):

        student = Student(**valid_student_data)
        
        assert student.document_number == '1234567890'
        assert student.first_name == 'Juan'
        assert student.last_name == 'Pérez'
        assert student.gender == Gender.MALE
        assert student.consent_given is True
        assert student.is_active is True

    def test_student_gender_from_string(self, valid_student_data):

        data = valid_student_data.copy()
        data['gender'] = 'MALE'  # String
        
        student = Student(**data)
        
        assert isinstance(student.gender, Gender)
        assert student.gender == Gender.MALE

    def test_student_gender_invalid_raises_error(self, valid_student_data):

        data = valid_student_data.copy()
        data['gender'] = 'INVALID'
        
        with pytest.raises(ValueError, match="Genero inválido"):
            Student(**data)

    def test_student_gender_empty_raises_error(self, valid_student_data):

        data = valid_student_data.copy()
        data['gender'] = ''
        
        with pytest.raises(ValueError, match="Genero requerido"):
            Student(**data)

    def test_full_name_property(self, student_entity):

        assert student_entity.full_name == "Juan Pérez"

    def test_age_calculation(self, valid_student_data):

        data = valid_student_data.copy()
        data['date_of_birth'] = date(2010, 1, 1)
        
        student = Student(**data)
        
        expected_age = date.today().year - 2010
        assert student.age in [expected_age, expected_age - 1]

    def test_is_minor_property(self, student_entity):

        assert student_entity.is_minor is True

    def test_has_valid_consent(self, student_entity):

        assert student_entity.has_valid_consent() is True

    def test_has_valid_consent_without_date(self, valid_student_data):
        """
        Test: Consentimiento sin fecha es inválido
        Requisito: RN-08
        """
        data = valid_student_data.copy()
        data['consent_given'] = True
        data['consent_date'] = None
        
        student = Student(**data)
        
        assert student.has_valid_consent() is False

    def test_validate_for_registration_success(self, student_entity):

        is_valid, missing = student_entity.validate_for_registration()
        
        assert is_valid is True
        assert missing == []

    def test_validate_for_registration_missing_fields(self, student_missing_required_fields):
        """
        Test: Validación falla con campos obligatorios faltantes
        Requisito: RN-17
        """
        student = Student(**student_missing_required_fields)
        
        is_valid, missing = student.validate_for_registration()
        
        assert is_valid is False
        assert 'first_name' in missing
        assert 'guardian_phone' in missing

    def test_validate_for_registration_missing_consent(self, student_without_consent):

        student = Student(**student_without_consent)
        
        is_valid, missing = student.validate_for_registration()
        
        assert is_valid is False
        assert 'consent_given' in missing

    def test_validate_for_characterization_active_student(self, student_entity):

        assert student_entity.validate_for_characterization() is True

    def test_validate_for_characterization_inactive_student(self, inactive_student_entity):

        assert inactive_student_entity.validate_for_characterization() is False

    def test_deactivate_student(self, student_entity):

        assert student_entity.is_active is True
        
        student_entity.deactivate()
        
        assert student_entity.is_active is False

    def test_student_str_representation(self, student_entity):

        str_repr = str(student_entity)
        
        assert '1234567890' in str_repr
        assert 'Juan Pérez' in str_repr
        assert '5°' in str_repr

    def test_update_data_success(self):
        student = Student(
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

        student.update_data(
            first_name="Carlos",
            last_name="Lopez",
            grade="6°",
            section="B",
            guardian_name="Ana Lopez",
            guardian_phone="3011111111",
            guardian_email="ana@test.com",
            guardian_relationship="Madre",
            address="Nueva direccion",
            neighborhood="Nuevo barrio",
            city="Bogotá",
            socioeconomic_stratum=3
        )

        assert student.first_name == "Carlos"
        assert student.last_name == "Lopez"
        assert student.grade == "6°"
        assert student.section == "B"
        assert student.guardian_name == "Ana Lopez"
        assert student.guardian_phone == "3011111111"
        assert student.city == "Bogotá"
        assert student.socioeconomic_stratum == 3


class TestGenderEnum:

    def test_gender_enum_values(self):
        assert Gender.MALE.value == "MALE"
        assert Gender.FEMALE.value == "FEMALE"
    
    def test_gender_from_string_valid(self):
        assert Gender.from_string('MALE') == Gender.MALE
        assert Gender.from_string('male') == Gender.MALE
        assert Gender.from_string('Male') == Gender.MALE
    
    def test_gender_from_string_invalid(self):
        with pytest.raises(ValueError, match="Genero inválido"):
            Gender.from_string('INVALID')
    
    def test_gender_from_string_empty(self):
        with pytest.raises(ValueError, match="Genero requerido"):
            Gender.from_string('')