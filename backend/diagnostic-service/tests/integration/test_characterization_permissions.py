
import pytest
from unittest.mock import Mock
from rest_framework.test import APIClient
from rest_framework import status
from diagnostics.models import CharacterizationModel
from datetime import date

from diagnostics.models import DiagnosticModel


@pytest.mark.django_db
class TestCharacterizationPermissions:
    """Tests de permisos para operaciones de caracterización"""
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def active_diagnostic(self):
        return DiagnosticModel.objects.create(
            code="PERM001",
            name="Test Permission",
            category="SPECIFIC_LEARNING_DISORDER",
            is_active=True
        )
    
    @pytest.fixture
    def valid_data(self, active_diagnostic):
        return {
            "student_id": 1000,
            "diagnostic_id": active_diagnostic.pk,
            "severity_level": "MODERATE",
            "identification_date": "2026-05-01",
            "is_active": True
        }

    
    @pytest.mark.parametrize("role,should_succeed", [
        ("PSYCHOLOGIST", True),
        ("ADMIN", False),
        ("TEACHER", False),
        ("SECRETARY", False),
    ])
    def test_characterize_permission_by_role(
        self,
        api_client,
        valid_data,
        role,
        should_succeed
    ):

        user = Mock()
        user.is_authenticated = True
        user.id = 100
        user.role = role
        user.status = "ACTIVE"
        
        api_client.force_authenticate(
            user=user,
            token={'role': role, 'status': 'ACTIVE'}
        )
        
        response = api_client.post(
            '/api/diagnostics/characterizations/',
            data=valid_data,
            format='json'
        )
        
        if should_succeed:
            assert response.status_code == status.HTTP_201_CREATED
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.parametrize("role,can_view", [
        ("PSYCHOLOGIST", True),
        ("ADMIN", True),
        ("TEACHER", True),
        ("SECRETARY", False),
    ])
    def test_view_characterizations_permission_by_role(
        self,
        api_client,
        role,
        can_view
    ):

        user = Mock()
        user.is_authenticated = True
        user.id = 100
        user.role = role
        user.status = "ACTIVE"
        
        api_client.force_authenticate(
            user=user,
            token={'role': role, 'status': 'ACTIVE'}
        )
        
        response = api_client.get(
            '/api/diagnostics/student/1000/characterizations/'
        )
        
        if can_view:
            assert response.status_code == status.HTTP_200_OK
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    
    @pytest.mark.parametrize("status_value,should_succeed", [
        ("ACTIVE", True),
        ("INACTIVE", False)
    ])
    def test_characterize_permission_by_status(
        self,
        api_client,
        valid_data,
        status_value,
        should_succeed
    ):

        user = Mock()
        user.is_authenticated = True
        user.id = 100
        user.role = "PSYCHOLOGIST"
        user.status = status_value
        
        api_client.force_authenticate(
            user=user,
            token={'role': 'PSYCHOLOGIST', 'status': status_value}
        )
        
        response = api_client.post(
            '/api/diagnostics/characterizations/',
            data=valid_data,
            format='json'
        )
        
        if should_succeed:
            assert response.status_code == status.HTTP_201_CREATED
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    
    def test_characterize_fails_without_jwt_token(
        self,
        api_client,
        valid_data
    ):

        user = Mock()
        user.is_authenticated = True
        user.id = 100
        user.role = "PSYCHOLOGIST"
        

        api_client.force_authenticate(user=user)
        
        response = api_client.post(
            '/api/diagnostics/characterizations/',
            data=valid_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_characterize_fails_with_corrupted_jwt_claims(
        self,
        api_client,
        valid_data
    ):

        user = Mock()
        user.is_authenticated = True
        user.id = 100
        user.role = "PSYCHOLOGIST"
        user.status = "ACTIVE"
        
        api_client.force_authenticate(
            user=user,
            token={}  
        )
        
        response = api_client.post(
            '/api/diagnostics/characterizations/',
            data=valid_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_characterize_fails_jwt_role_mismatch(
        self,
        api_client,
        valid_data
    ):
        user = Mock()
        user.is_authenticated = True
        user.id = 100
        user.role = "PSYCHOLOGIST"
        user.status = "ACTIVE"
        
        api_client.force_authenticate(
            user=user,
            token={'role': 'TEACHER', 'status': 'ACTIVE'}  # Rol diferente
        )
        
        response = api_client.post(
            '/api/diagnostics/characterizations/',
            data=valid_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestTeacherRestrictedView:

    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def teacher_user(self):
        user = Mock()
        user.is_authenticated = True
        user.id = 10
        user.role = "TEACHER"
        user.status = "ACTIVE"
        return user
    
    @pytest.fixture
    def authenticated_teacher(self, api_client, teacher_user):
        api_client.force_authenticate(
            user=teacher_user,
            token={'role': 'TEACHER', 'status': 'ACTIVE'}
        )
        return api_client
    
    def test_teacher_cannot_see_clinical_data(
        self,
        authenticated_teacher
    ):

        diagnostic = DiagnosticModel.objects.create(
            code="CLIN001",
            name="Clinical Test",
            category="SPECIFIC_LEARNING_DISORDER",
            is_active=True
        )
        
        CharacterizationModel.objects.create(
            student_id=2000,
            diagnostic=diagnostic,
            severity_level="MODERATE",
            identification_date=date.today(),
            observations="Observaciones confidenciales del psicólogo",
            cognitive_area_notes="Datos clínicos cognitivos",
            communicative_area_notes="Datos clínicos comunicativos",
            is_active=True,
            created_by=5
        )
        
        response = authenticated_teacher.get(
            '/api/diagnostics/student/2000/characterizations/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.data['data'][0]
        
        assert 'observations' not in data
        assert 'cognitive_area_notes' not in data
        assert 'communicative_area_notes' not in data
        assert 'socioemotional_area_notes' not in data
        
        assert 'id' in data
        assert 'severity_level' in data