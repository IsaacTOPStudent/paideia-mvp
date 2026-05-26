import pytest
from datetime import date

from students.serializers import (
    StudentRegisterSerializer,
    StudentResponseSerializer,
    StudentUpdateSerializer
)
from src.domain.entities.student import Gender


class TestStudentRegisterSerializer:

    def test_valid_serializer_data(self, valid_student_data):
        serializer = StudentRegisterSerializer(data=valid_student_data)

        assert serializer.is_valid()
        assert serializer.validated_data["first_name"] == "Juan"
        assert serializer.validated_data["document_number"] == "1234567890"

    def test_missing_required_fields(self):
        data = {
            "first_name": "Juan"
        }

        serializer = StudentRegisterSerializer(data=data)

        assert not serializer.is_valid()

        required_fields = [
            "document_number",
            "last_name",
            "date_of_birth",
            "gender",
            "grade",
            "guardian_name",
            "guardian_phone",
            "consent_given"
        ]

        for field in required_fields:
            assert field in serializer.errors

    def test_invalid_gender(self, valid_student_data):
        data = valid_student_data.copy()
        data["gender"] = "OTHER"

        serializer = StudentRegisterSerializer(data=data)

        assert not serializer.is_valid()
        assert "gender" in serializer.errors

    def test_invalid_document_type(self, valid_student_data):
        data = valid_student_data.copy()
        data["document_type"] = "XYZ"

        serializer = StudentRegisterSerializer(data=data)

        assert not serializer.is_valid()
        assert "document_type" in serializer.errors

    def test_invalid_grade(self, valid_student_data):
        data = valid_student_data.copy()
        data["grade"] = "Universidad"

        serializer = StudentRegisterSerializer(data=data)

        assert not serializer.is_valid()
        assert "grade" in serializer.errors

    def test_invalid_email(self, valid_student_data):
        data = valid_student_data.copy()
        data["guardian_email"] = "correo-invalido"

        serializer = StudentRegisterSerializer(data=data)

        assert not serializer.is_valid()
        assert "guardian_email" in serializer.errors

    def test_default_document_type(self, valid_student_data):
        data = valid_student_data.copy()
        data.pop("document_type", None)

        serializer = StudentRegisterSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["document_type"] == "TI"

    def test_default_city(self, valid_student_data):
        data = valid_student_data.copy()
        data.pop("city", None)

        serializer = StudentRegisterSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["city"] == "Cartagena"

    def test_optional_fields_can_be_empty(self, valid_student_data):
        data = valid_student_data.copy()

        data["section"] = ""
        data["guardian_email"] = ""
        data["guardian_relationship"] = ""
        data["address"] = ""
        data["neighborhood"] = ""

        serializer = StudentRegisterSerializer(data=data)

        assert serializer.is_valid()


class TestStudentResponseSerializer:
    """Tests para StudentResponseSerializer"""

    def test_serialize_student_entity(self, student_entity):
        serializer = StudentResponseSerializer(student_entity)

        data = serializer.data

        assert data["first_name"] == "Juan"
        assert data["last_name"] == "Pérez"
        assert data["full_name"] == "Juan Pérez"
        assert data["gender"] == "MALE"
        assert data["gender_display"] == "Masculino"
        assert "age" in data

    def test_serialize_dict_object(self, valid_student_data):
        data = valid_student_data.copy()

        data.update({
            "id": 1,
            "created_at": "2026-05-23T10:00:00Z",
            "updated_at": "2026-05-23T10:00:00Z"
        })

        serializer = StudentResponseSerializer(data)

        result = serializer.data

        assert result["first_name"] == "Juan"
        assert result["full_name"] == "Juan Pérez"
        assert result["gender_display"] == "Masculino"

    def test_get_age_calculation(self, student_entity):
        serializer = StudentResponseSerializer()

        age = serializer.get_age(student_entity)

        expected_age = (
            date.today().year
            - student_entity.date_of_birth.year
            - (
                (date.today().month, date.today().day)
                < (
                    student_entity.date_of_birth.month,
                    student_entity.date_of_birth.day
                )
            )
        )

        assert age == expected_age

    def test_get_full_name(self, student_entity):
        serializer = StudentResponseSerializer()

        full_name = serializer.get_full_name(student_entity)

        assert full_name == "Juan Pérez"

    def test_get_gender_display_male(self, student_entity):
        serializer = StudentResponseSerializer()

        result = serializer.get_gender_display(student_entity)

        assert result == "Masculino"

    def test_get_gender_display_female(self, student_entity):
        student_entity.gender = Gender.FEMALE

        serializer = StudentResponseSerializer()

        result = serializer.get_gender_display(student_entity)

        assert result == "Femenino"

    def test_get_age_without_birthdate_returns_zero(self):
        serializer = StudentResponseSerializer()

        obj = {
            "date_of_birth": None
        }

        assert serializer.get_age(obj) == 0

    # Test update serializer
    def test_valid_partial_data(self):
        data = {
            "first_name": "Juan",
            "grade": "5°",
            "guardian_email": "juan@example.com"
        }

        serializer = StudentUpdateSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["first_name"] == "Juan"
        assert serializer.validated_data["grade"] == "5°"

    def test_empty_data_is_valid(self):
        serializer = StudentUpdateSerializer(data={})

        assert serializer.is_valid()

    def test_invalid_grade(self):
        data = {
            "grade": "Universidad"
        }

        serializer = StudentUpdateSerializer(data=data)

        assert not serializer.is_valid()
        assert "grade" in serializer.errors

    def test_invalid_email(self):
        data = {
            "guardian_email": "correo-invalido"
        }

        serializer = StudentUpdateSerializer(data=data)

        assert not serializer.is_valid()
        assert "guardian_email" in serializer.errors

    def test_allow_blank_fields(self):
        data = {
            "section": "",
            "guardian_relationship": "",
            "address": "",
            "neighborhood": ""
        }

        serializer = StudentUpdateSerializer(data=data)

        assert serializer.is_valid()

    def test_allow_null_socioeconomic_stratum(self):
        data = {
            "socioeconomic_stratum": None
        }

        serializer = StudentUpdateSerializer(data=data)

        assert serializer.is_valid()

    def test_invalid_socioeconomic_stratum_type(self):
        data = {
            "socioeconomic_stratum": "alto"
        }

        serializer = StudentUpdateSerializer(data=data)

        assert not serializer.is_valid()
        assert "socioeconomic_stratum" in serializer.errors

    def test_max_length_validation(self):
        data = {
            "first_name": "a" * 101
        }

        serializer = StudentUpdateSerializer(data=data)

        assert not serializer.is_valid()
        assert "first_name" in serializer.errors