import pytest
from datetime import date
from unittest.mock import Mock
from rest_framework.test import APIClient
from rest_framework import status

from diagnostics.models import DiagnosticModel, CharacterizationModel


@pytest.mark.django_db
class TestCharacterizeStudentView:
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def mock_psychologist_user(self):
        user = Mock()
        user.is_authenticated = True
        user.id = 5
        user.role = "PSYCHOLOGIST"
        user.status = "ACTIVE"
        return user
    
    @pytest.fixture
    def mock_teacher_user(self):
        user = Mock()
        user.is_authenticated = True
        user.id = 10
        user.role = "TEACHER"
        user.status = "ACTIVE"
        return user
    
    @pytest.fixture
    def mock_admin_user(self):
        user = Mock()
        user.is_authenticated = True
        user.id = 1
        user.role = "ADMIN"
        user.status = "ACTIVE"
        return user
    
    @pytest.fixture
    def authenticated_psychologist_client(self, api_client, mock_psychologist_user):
        api_client.force_authenticate(
            user=mock_psychologist_user,
            token={
                'user_id': 5,
                'role': 'PSYCHOLOGIST',
                'status': 'ACTIVE'
            }
        )
        return api_client
    
    @pytest.fixture
    def authenticated_teacher_client(self, api_client, mock_teacher_user):
        api_client.force_authenticate(
            user=mock_teacher_user,
            token={
                'user_id': 10,
                'role': 'TEACHER',
                'status': 'ACTIVE'
            }
        )
        return api_client
    
    @pytest.fixture
    def active_diagnostic(self):
        return DiagnosticModel.objects.create(
            code="DSL001",
            name="Dislexia",
            category="SPECIFIC_LEARNING_DISORDER",
            description="Dificultad en lectoescritura",
            is_active=True
        )
    
    @pytest.fixture
    def inactive_diagnostic(self):
        return DiagnosticModel.objects.create(
            code="TDAH001",
            name="TDAH",
            category="ADHD",
            description="Trastorno por déficit de atención",
            is_active=False
        )
    
    @pytest.fixture
    def valid_characterization_data(self, active_diagnostic):
        return {
            "student_id": 100,
            "diagnostic_id": active_diagnostic.pk,
            "severity_level": "MODERATE",
            "identification_date": "2026-05-01",
            "observations": "Requiere apoyo en lectura",
            "cognitive_area_notes": "Dificultad en comprensión lectora",
            "is_active": True
        }
    
    
    def test_characterize_student_success(
        self, 
        authenticated_psychologist_client, 
        valid_characterization_data
    ):
        response = authenticated_psychologist_client.post(
            '/api/diagnostics/characterizations/',
            data=valid_characterization_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Estudiante caracterizado exitosamente'
        assert 'data' in response.data
        
        assert CharacterizationModel.objects.filter(student_id=100).exists()
        
        data = response.data['data']
        assert data['student_id'] == 100
        assert data['severity_level'] == "MODERATE"
        assert data['severity_level_display'] == "Moderado"
        assert data['is_active'] is True
        assert data['created_by'] == 5  # ID del psicólogo
    
    def test_characterize_student_creates_all_fields(
        self,
        authenticated_psychologist_client,
        active_diagnostic
    ):
        full_data = {
            "student_id": 200,
            "diagnostic_id": active_diagnostic.pk,
            "severity_level": "SEVERE",
            "identification_date": "2026-05-10",
            "observations": "Observación general",
            "cognitive_area_notes": "Notas cognitivas",
            "communicative_area_notes": "Notas comunicativas",
            "socioemotional_area_notes": "Notas socioemocionales",
            "motor_area_notes": "Notas motoras",
            "sensory_area_notes": "Notas sensoriales",
            "academic_area_notes": "Notas académicas",
            "behavioral_area_notes": "Notas conductuales",
            "is_active": True
        }
        
        response = authenticated_psychologist_client.post(
            '/api/diagnostics/characterizations/',
            data=full_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        char = CharacterizationModel.objects.get(student_id=200)
        assert char.cognitive_area_notes == "Notas cognitivas"
        assert char.communicative_area_notes == "Notas comunicativas"
        assert char.motor_area_notes == "Notas motoras"
        assert char.severity_level == "SEVERE"
    
    def test_characterize_student_multiple_diagnoses_for_same_student(
        self,
        authenticated_psychologist_client,
        active_diagnostic
    ):

        diagnostic2 = DiagnosticModel.objects.create(
            code="TDAH002",
            name="TDAH",
            category="ADHD",
            is_active=True
        )
        
        data1 = {
            "student_id": 300,
            "diagnostic_id": active_diagnostic.pk,
            "severity_level": "MILD",
            "identification_date": "2026-05-01",
            "is_active": True
        }
        
        response1 = authenticated_psychologist_client.post(
            '/api/diagnostics/characterizations/',
            data=data1,
            format='json'
        )
        
        data2 = {
            "student_id": 300,
            "diagnostic_id": diagnostic2.pk,
            "severity_level": "MODERATE",
            "identification_date": "2026-05-02",
            "is_active": True
        }
        
        response2 = authenticated_psychologist_client.post(
            '/api/diagnostics/characterizations/',
            data=data2,
            format='json'
        )
        
        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        
        chars = CharacterizationModel.objects.filter(student_id=300)
        assert chars.count() == 2
    
    
    def test_characterize_fails_missing_student_id(
        self,
        authenticated_psychologist_client,
        active_diagnostic
    ):
        data = {
            "diagnostic_id": active_diagnostic.pk,
            "severity_level": "MODERATE",
            "identification_date": "2026-05-01",
            "is_active": True
        }
        
        response = authenticated_psychologist_client.post(
            '/api/diagnostics/characterizations/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'details' in response.data
    
    def test_characterize_fails_missing_diagnostic_id(
        self,
        authenticated_psychologist_client
    ):
        data = {
            "student_id": 100,
            "severity_level": "MODERATE",
            "identification_date": "2026-05-01",
            "is_active": True
        }
        
        response = authenticated_psychologist_client.post(
            '/api/diagnostics/characterizations/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_characterize_fails_invalid_severity_level(
        self,
        authenticated_psychologist_client,
        active_diagnostic
    ):
        data = {
            "student_id": 100,
            "diagnostic_id": active_diagnostic.pk,
            "severity_level": "INVALID_LEVEL",
            "identification_date": "2026-05-01",
            "is_active": True
        }
        
        response = authenticated_psychologist_client.post(
            '/api/diagnostics/characterizations/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'Nivel de severidad inválido' in response.data['error']
    
    def test_characterize_fails_inactive_diagnostic(
        self,
        authenticated_psychologist_client,
        inactive_diagnostic
    ):

        data = {
            "student_id": 100,
            "diagnostic_id": inactive_diagnostic.pk,
            "severity_level": "MODERATE",
            "identification_date": "2026-05-01",
            "is_active": True
        }
        
        response = authenticated_psychologist_client.post(
            '/api/diagnostics/characterizations/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'El catálogo de diagnósticos no está configurado. Contacte al Administrador' in response.data['error']
    
    def test_characterize_fails_empty_catalog(
        self,
        authenticated_psychologist_client
    ):

        DiagnosticModel.objects.all().update(is_active=False)
        
        data = {
            "student_id": 100,
            "diagnostic_id": 999,
            "severity_level": "MODERATE",
            "identification_date": "2026-05-01",
            "is_active": True
        }
        
        response = authenticated_psychologist_client.post(
            '/api/diagnostics/characterizations/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'catálogo de diagnósticos no está configurado' in response.data['error']
    
    
    def test_characterize_forbidden_for_teacher(
        self,
        authenticated_teacher_client,
        valid_characterization_data
    ):

        response = authenticated_teacher_client.post(
            '/api/diagnostics/characterizations/',
            data=valid_characterization_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_characterize_forbidden_for_unauthenticated(
        self,
        api_client,
        valid_characterization_data
    ):
        response = api_client.post(
            '/api/diagnostics/characterizations/',
            data=valid_characterization_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_characterize_forbidden_inactive_user(
        self,
        api_client,
        valid_characterization_data
    ):

        user = Mock()
        user.is_authenticated = True
        user.id = 5
        user.role = "PSYCHOLOGIST"
        user.status = "INACTIVE"  
        
        api_client.force_authenticate(
            user=user,
            token={
                'user_id': 5,
                'role': 'PSYCHOLOGIST',
                'status': 'INACTIVE'
            }
        )
        
        response = api_client.post(
            '/api/diagnostics/characterizations/',
            data=valid_characterization_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_characterize_forbidden_without_token_claims(
        self,
        api_client,
        valid_characterization_data
    ):
        user = Mock()
        user.is_authenticated = True
        user.id = 5
        user.role = "PSYCHOLOGIST"
        
        api_client.force_authenticate(user=user)
        
        response = api_client.post(
            '/api/diagnostics/characterizations/',
            data=valid_characterization_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCharacterizationsByStudentView:
    """ GET /api/diagnostics/student/{id}/characterizations/"""
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def mock_psychologist_user(self):
        user = Mock()
        user.is_authenticated = True
        user.id = 5
        user.role = "PSYCHOLOGIST"
        user.status = "ACTIVE"
        return user
    
    @pytest.fixture
    def mock_teacher_user(self):
        user = Mock()
        user.is_authenticated = True
        user.id = 10
        user.role = "TEACHER"
        user.status = "ACTIVE"
        return user
    
    @pytest.fixture
    def mock_admin_user(self):
        user = Mock()
        user.is_authenticated = True
        user.id = 1
        user.role = "ADMIN"
        user.status = "ACTIVE"
        return user
    
    @pytest.fixture
    def mock_secretary_user(self):
        user = Mock()
        user.is_authenticated = True
        user.id = 20
        user.role = "SECRETARY"
        user.status = "ACTIVE"
        return user
    
    @pytest.fixture
    def authenticated_psychologist_client(self, api_client, mock_psychologist_user):
        api_client.force_authenticate(
            user=mock_psychologist_user,
            token={'role': 'PSYCHOLOGIST', 'status': 'ACTIVE'}
        )
        return api_client
    
    @pytest.fixture
    def authenticated_teacher_client(self, api_client, mock_teacher_user):
        api_client.force_authenticate(
            user=mock_teacher_user,
            token={'role': 'TEACHER', 'status': 'ACTIVE'}
        )
        return api_client
    
    @pytest.fixture
    def authenticated_admin_client(self, api_client, mock_admin_user):
        api_client.force_authenticate(
            user=mock_admin_user,
            token={'role': 'ADMIN', 'status': 'ACTIVE'}
        )
        return api_client
    
    @pytest.fixture
    def authenticated_secretary_client(self, api_client, mock_secretary_user):
        api_client.force_authenticate(
            user=mock_secretary_user,
            token={'role': 'SECRETARY', 'status': 'ACTIVE'}
        )
        return api_client
    
    @pytest.fixture
    def diagnostic(self):
        return DiagnosticModel.objects.create(
            code="TEST001",
            name="Test Diagnostic",
            category="SPECIFIC_LEARNING_DISORDER",
            is_active=True
        )
    
    @pytest.fixture
    def student_characterizations(self, diagnostic):
        CharacterizationModel.objects.create(
            student_id=500,
            diagnostic=diagnostic,
            severity_level="MILD",
            identification_date=date(2026, 5, 1),
            observations="Primera caracterización",
            cognitive_area_notes="Notas cognitivas confidenciales",
            is_active=True,
            created_by=5
        )
        
        CharacterizationModel.objects.create(
            student_id=500,
            diagnostic=diagnostic,
            severity_level="MODERATE",
            identification_date=date(2026, 5, 15),
            observations="Segunda caracterización",
            is_active=True,
            created_by=5
        )
        

        CharacterizationModel.objects.create(
            student_id=500,
            diagnostic=diagnostic,
            severity_level="SEVERE",
            identification_date=date(2026, 4, 1),
            is_active=False,  # Inactiva
            created_by=5
        )
    
    
    def test_psychologist_gets_full_characterizations(
        self,
        authenticated_psychologist_client,
        student_characterizations
    ):

        response = authenticated_psychologist_client.get(
            '/api/diagnostics/student/500/characterizations/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2  # Solo las activas
        
        data = response.data['data'][0]
        assert 'id' in data
        assert 'student_id' in data
        assert 'severity_level' in data
        assert 'severity_level_display' in data
        assert 'observations' in data
        assert 'cognitive_area_notes' in data  # Psicólogo ve datos clínicos
    
    def test_admin_gets_full_characterizations(
        self,
        authenticated_admin_client,
        student_characterizations
    ):
        response = authenticated_admin_client.get(
            '/api/diagnostics/student/500/characterizations/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        data = response.data['data'][0]
        assert 'cognitive_area_notes' in data
        assert 'observations' in data
    
    def test_teacher_gets_limited_characterizations(
        self,
        authenticated_teacher_client,
        student_characterizations
    ):

        response = authenticated_teacher_client.get(
            '/api/diagnostics/student/500/characterizations/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        data = response.data['data'][0]
        assert 'id' in data
        assert 'severity_level' in data
        
        assert 'observations' not in data
        assert 'cognitive_area_notes' not in data
        assert 'communicative_area_notes' not in data
    
    def test_get_characterizations_empty_list(
        self,
        authenticated_psychologist_client
    ):
        response = authenticated_psychologist_client.get(
            '/api/diagnostics/student/999/characterizations/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['data'] == []
    
    def test_get_characterizations_only_active(
        self,
        authenticated_psychologist_client,
        student_characterizations
    ):
        response = authenticated_psychologist_client.get(
            '/api/diagnostics/student/500/characterizations/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        for char in response.data['data']:
            assert char['is_active'] is True

    
    def test_secretary_forbidden_to_view_characterizations(
        self,
        authenticated_secretary_client,
        student_characterizations
    ):

        response = authenticated_secretary_client.get(
            '/api/diagnostics/student/500/characterizations/'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.data
        assert 'No tienes autorización' in response.data['error']
    
    def test_unauthenticated_user_forbidden(
        self,
        api_client,
        student_characterizations
    ):

        response = api_client.get(
            '/api/diagnostics/student/500/characterizations/'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_inactive_user_forbidden(
        self,
        api_client,
        student_characterizations
    ):

        user = Mock()
        user.is_authenticated = True
        user.id = 5
        user.role = "PSYCHOLOGIST"
        user.status = "INACTIVE"
        
        api_client.force_authenticate(
            user=user,
            token={'role': 'PSYCHOLOGIST', 'status': 'INACTIVE'}
        )
        
        response = api_client.get(
            '/api/diagnostics/student/500/characterizations/'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    
    def test_response_includes_severity_display(
        self,
        authenticated_psychologist_client,
        student_characterizations
    ):
        response = authenticated_psychologist_client.get(
            '/api/diagnostics/student/500/characterizations/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.data['data'][0]
        assert 'severity_level_display' in data
        assert data['severity_level_display'] in ['Leve', 'Moderado', 'Severo']
    
    def test_teacher_response_format(
        self,
        authenticated_teacher_client,
        student_characterizations
    ):

        response = authenticated_teacher_client.get(
            '/api/diagnostics/student/500/characterizations/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.data['data'][0]
        
        assert set(data.keys()) == {'id', 'severity_level'}
        
        assert data['severity_level'] in ['Leve', 'Moderado', 'Severo']