import pytest 
from datetime import date, datetime
from django.utils import timezone
from django.conf import settings
from typing import Dict, Any
from unittest.mock import Mock

from rest_framework.test import APIClient

from src.domain.entities.student import Student
from src.domain.ports.student_repository import StudentRepository

#Test data fixtures
@pytest.fixture
def valid_student_data() -> Dict[str, Any]:

    return {
        'document_type': 'TI',
        'document_number': '1234567890',
        'first_name': 'Juan',
        'last_name': 'Pérez',
        'date_of_birth': date(2010, 5, 15),
        'gender': 'MALE',
        'grade': '5°',
        'section': 'A',
        'guardian_name': 'María García',
        'guardian_phone': '3001234567',
        'guardian_email': 'maria@example.com',
        'guardian_relationship': 'Madre',
        'consent_given': True,
        'consent_date': timezone.now(),
        'address': 'Calle 123 #45-67',
        'neighborhood': 'El Bosque',
        'city': 'Cartagena',
        'socioeconomic_stratum': 3,
        'created_at': timezone.now(),
        'updated_at': timezone.now(),
        'is_active': True
    }

@pytest.fixture
def student_without_consent(valid_student_data) -> Dict[str, Any]:
    data = valid_student_data.copy()
    data['consent_given'] = False
    return data

@pytest.fixture
def student_missing_required_fields(valid_student_data) -> Dict[str, Any]:
    data = valid_student_data.copy()
    data['first_name'] = ''
    data['guardian_phone'] = ''
    return data

@pytest.fixture
def student_duplicate_document(valid_student_data) -> Dict[str, Any]:
    return valid_student_data.copy()

#Fixtures from Domain Entities
@pytest.fixture
def student_entity(valid_student_data):
    return Student(**valid_student_data)

@pytest.fixture
def inactive_student_entity(valid_student_data):
    data = valid_student_data.copy()
    data['is_active'] = False
    return Student(**data)

# Mock repository fixtures
@pytest.fixture
def mock_student_repository():
    return Mock(spec=StudentRepository)

# @pytest.fixture(scope='session')
# def django_db_setup():
#     settings.DATABASES['default'] = {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': ':memory:',
#     }

@pytest.fixture
def api_client():
    return APIClient()



