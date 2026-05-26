from rest_framework import serializers

from datetime import date
from typing import Any, Union

from src.domain.entities.student import Student

class StudentRegisterSerializer(serializers.Serializer):
    """Serializer for student registration (RF-03)"""
    document_type = serializers.ChoiceField(
        choices=['CC', 'TI', 'CE', 'PA'],
        default='TI'
    )
    document_number = serializers.CharField(max_length=20)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    date_of_birth = serializers.DateField()
    gender = serializers.ChoiceField(choices=['MALE', 'FEMALE'])
    
    grade = serializers.ChoiceField(
        choices=[
            'Preescolar', '1°', '2°', '3°', '4°', '5°',
            '6°', '7°', '8°', '9°', '10°', '11°'
        ]
    )
    section = serializers.CharField(max_length=5, required=False, allow_blank=True)
    
    guardian_name = serializers.CharField(max_length=100)
    guardian_phone = serializers.CharField(max_length=20)
    guardian_email = serializers.EmailField(required=False, allow_blank=True)
    guardian_relationship = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    # Consentimiento (RN-08)
    consent_given = serializers.BooleanField(required=True)
    
    # Opcionales
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    neighborhood = serializers.CharField(max_length=100, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, default='Cartagena')
    socioeconomic_stratum = serializers.IntegerField(required=False, allow_null=True)


class StudentResponseSerializer(serializers.Serializer):
    """
    Serializer for student response
    """
    id = serializers.IntegerField()
    document_type = serializers.CharField()
    document_number = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    date_of_birth = serializers.DateField()
    gender = serializers.SerializerMethodField()
    grade = serializers.CharField()
    section = serializers.CharField(allow_blank=True, allow_null=True)
    
    guardian_name = serializers.CharField()
    guardian_phone = serializers.CharField()
    guardian_email = serializers.EmailField(allow_blank=True, allow_null=True)
    guardian_relationship = serializers.CharField(allow_blank=True, allow_null=True)
    
    consent_given = serializers.BooleanField()
    consent_date = serializers.DateTimeField(allow_null=True)
    
    address = serializers.CharField(allow_blank=True, allow_null=True)
    neighborhood = serializers.CharField(allow_blank=True, allow_null=True)
    city = serializers.CharField(allow_blank=True, allow_null=True)
    socioeconomic_stratum = serializers.IntegerField(allow_null=True)
    
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    # Calculated fields
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    gender_display = serializers.SerializerMethodField()

    #helper
    def _get_value(self, obj: Union[Student, dict], field: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(field, default)
        
        return getattr(obj, field, default)
    
    def get_gender(self, obj: Any) -> str:
        gender = self._get_value(obj, "gender", "")

        if hasattr(gender, "value"):
            return gender.value
        
        return gender
    
    def get_age(self, obj: Any) -> int:
        # Soporta diccionarios o entidades
        if hasattr(obj, "age"):
            return obj.age
        
        dob = self._get_value(obj, "date_of_birth")
        
        if not dob:
            return 0
            
        today = date.today()

        return today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
    
    def get_full_name(self, obj: Any) -> str:
        if hasattr(obj, "full_name"):
            return obj.full_name

        first = self._get_value(obj, "first_name", "")
        last = self._get_value(obj, "last_name", "")

        return f"{first} {last}".strip()
    
    def get_gender_display(self, obj: Any) -> str:
        gender = self._get_value(obj, "gender", "")

        if hasattr(gender, "value"):
            gender = gender.value

        gender = str(gender)
        
        translations = {
            'MALE': 'Masculino',
            'FEMALE': 'Femenino'
        }

        return translations.get(gender, gender)
    
class StudentUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)

    grade = serializers.ChoiceField(
        choices=[
            'Preescolar', '1°', '2°', '3°', '4°', '5°',
            '6°', '7°', '8°', '9°', '10°', '11°'
        ],
        required=False
    )

    section = serializers.CharField(
        max_length=5,
        required=False,
        allow_blank=True
    )

    guardian_name = serializers.CharField(max_length=100, required=False)

    guardian_phone = serializers.CharField(max_length=20, required=False)

    guardian_email = serializers.EmailField(
        required=False,
        allow_blank=True
    )

    guardian_relationship = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True
    )

    address = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )

    neighborhood = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )

    city = serializers.CharField(
        max_length=100,
        required=False
    )

    socioeconomic_stratum = serializers.IntegerField(
        required=False,
        allow_null=True
    )