
import pytest
from unittest.mock import Mock
from rest_framework.test import APIClient
from rest_framework import status

from diagnostics.models import DiagnosticModel


@pytest.mark.django_db
class TestCreateDiagnosticView:
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    @pytest.fixture
    def mock_admin_user(self):
        user = Mock()
        user.is_authenticated = True
        user.id = 1
        user.role = "ADMIN"
        user.status = "ACTIVE"
        return user
    
    @pytest.fixture
    def mock_psychologist_user(self):
        user = Mock()
        user.is_authenticated = True
        user.id = 5
        user.role = "PSYCHOLOGIST"
        user.status = "ACTIVE"
        return user
    
    @pytest.fixture
    def authenticated_admin_client(self, api_client, mock_admin_user):
        api_client.force_authenticate(
            user=mock_admin_user,
            token={'role': 'ADMIN', 'status': 'ACTIVE'}
        )
        return api_client
    
    @pytest.fixture
    def authenticated_psychologist_client(self, api_client, mock_psychologist_user):
        api_client.force_authenticate(
            user=mock_psychologist_user,
            token={'role': 'PSYCHOLOGIST', 'status': 'ACTIVE'}
        )
        return api_client
    
    @pytest.fixture
    def valid_diagnostic_data(self):
        return {
            "code": "DSL001",
            "name": "Dislexia",
            "category": "SPECIFIC_LEARNING_DISORDER",
            "description": "Dificultad específica en lectoescritura",
            "normative_reference": "Decreto 1421/2017",
            "is_active": True
        }
    
    def test_create_diagnostic_success(
        self,
        authenticated_admin_client,
        valid_diagnostic_data
    ):

        response = authenticated_admin_client.post(
            '/api/diagnostic/catalog/',
            data=valid_diagnostic_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Diagnóstico agregado al catálogo exitosamente'
        assert 'data' in response.data
        
        assert DiagnosticModel.objects.filter(code="DSL001").exists()
        
        data = response.data['data']
        assert data['code'] == "DSL001"
        assert data['name'] == "Dislexia"
        assert data['category'] == "SPECIFIC_LEARNING_DISORDER"
        assert data['category_display'] == "Trastorno Específico del Aprendizaje"
        assert data['is_active'] is True
    
    def test_create_diagnostic_normalizes_code_to_uppercase(
        self,
        authenticated_admin_client
    ):

        data = {
            "code": "dsl002",
            "name": "Test",
            "category": "ADHD",
            "description": "Test description",
            "is_active": True
        }
        
        response = authenticated_admin_client.post(
            '/api/diagnostic/catalog/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['code'] == "DSL002"
        
        diagnostic = DiagnosticModel.objects.get(code="DSL002")
        assert diagnostic.code == "DSL002"
    
    def test_create_diagnostic_with_all_categories(
        self,
        authenticated_admin_client
    ):
        categories = [
            "PHYSICAL_DISABILITY",
            "SENSORY_VISUAL",
            "SENSORY_AUDITORY",
            "COGNITIVE_DISABILITY",
            "PSYCHOSOCIAL_DISABILITY",
            "MULTIPLE_DISABILITY",
            "SPECIFIC_LEARNING_DISORDER",
            "ADHD",
            "AUTISM_SPECTRUM",
            "GIFTEDNESS",
        ]
        
        for idx, category in enumerate(categories):
            data = {
                "code": f"CAT{idx:03d}",
                "name": f"Test {category}",
                "category": category,
                "description": f"Test for {category}",
                "is_active": True
            }
            
            response = authenticated_admin_client.post(
                '/api/diagnostic/catalog/',
                data=data,
                format='json'
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data['data']['category'] == category
        
    def test_create_diagnostic_fails_missing_code(
        self,
        authenticated_admin_client
    ):
        data = {
            "name": "Test",
            "category": "ADHD",
            "description": "Test",
            "is_active": True
        }
        
        response = authenticated_admin_client.post(
            '/api/diagnostic/catalog/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_create_diagnostic_fails_missing_name(
        self,
        authenticated_admin_client
    ):
        data = {
            "code": "TEST001",
            # "name": falta
            "category": "ADHD",
            "description": "Test",
            "is_active": True
        }
        
        response = authenticated_admin_client.post(
            '/api/diagnostic/catalog/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_diagnostic_fails_invalid_category(
        self,
        authenticated_admin_client
    ):
        data = {
            "code": "TEST001",
            "name": "Test",
            "category": "INVALID_CATEGORY",
            "description": "Test",
            "is_active": True
        }
        
        response = authenticated_admin_client.post(
            '/api/diagnostic/catalog/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Categoría no válida' in response.data['error']
    
    def test_create_diagnostic_fails_duplicate_code(
        self,
        authenticated_admin_client
    ):
        DiagnosticModel.objects.create(
            code="DUP001",
            name="Duplicado",
            category="ADHD",
            description="Test",
            is_active=True
        )
        
        data = {
            "code": "DUP001",
            "name": "Otro nombre",
            "category": "ADHD",
            "description": "Test",
            "is_active": True
        }
        
        response = authenticated_admin_client.post(
            '/api/diagnostic/catalog/',
            data=data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert 'Ya existe un diagnóstico' in response.data['error']

    def test_create_diagnostic_forbidden_for_psychologist(
        self,
        authenticated_psychologist_client,
        valid_diagnostic_data
    ):

        response = authenticated_psychologist_client.post(
            '/api/diagnostic/catalog/',
            data=valid_diagnostic_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_diagnostic_forbidden_unauthenticated(
        self,
        api_client,
        valid_diagnostic_data
    ):
        response = api_client.post(
            '/api/diagnostic/catalog/',
            data=valid_diagnostic_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_diagnostic_forbidden_inactive_admin(
        self,
        api_client,
        valid_diagnostic_data
    ):
        user = Mock()
        user.is_authenticated = True
        user.id = 1
        user.role = "ADMIN"
        user.status = "INACTIVE"
        
        api_client.force_authenticate(
            user=user,
            token={'role': 'ADMIN', 'status': 'INACTIVE'}
        )
        
        response = api_client.post(
            '/api/diagnostic/catalog/',
            data=valid_diagnostic_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestListDiagnosticsView:
    
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
    def mock_admin_user(self):
        user = Mock()
        user.is_authenticated = True
        user.id = 1
        user.role = "ADMIN"
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
    def authenticated_psychologist_client(self, api_client, mock_psychologist_user):
        api_client.force_authenticate(
            user=mock_psychologist_user,
            token={'role': 'PSYCHOLOGIST', 'status': 'ACTIVE'}
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
    def sample_diagnostics(self):
        DiagnosticModel.objects.create(
            code="DSL001",
            name="Dislexia",
            category="SPECIFIC_LEARNING_DISORDER",
            description="Dificultad en lectoescritura",
            is_active=True
        )
        DiagnosticModel.objects.create(
            code="TDAH001",
            name="TDAH",
            category="ADHD",
            description="Déficit de atención",
            is_active=True
        )
        DiagnosticModel.objects.create(
            code="OLD001",
            name="Obsoleto",
            category="COGNITIVE_DISABILITY",
            description="Ya no se usa",
            is_active=False
        )
    
    def test_list_diagnostics_returns_only_active_by_default(
        self,
        authenticated_psychologist_client,
        sample_diagnostics
    ):
        response = authenticated_psychologist_client.get(
            '/api/diagnostics/catalog/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
        # Verificar que todos son activos
        for diagnostic in response.data['data']:
            assert diagnostic['is_active'] is True
    
    def test_list_diagnostics_includes_inactive_when_requested(
        self,
        authenticated_admin_client,
        sample_diagnostics
    ):
        response = authenticated_admin_client.get(
            '/api/diagnostics/catalog/?include_inactive=true'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        
        active_count = sum(1 for d in response.data['data'] if d['is_active'])
        inactive_count = sum(1 for d in response.data['data'] if not d['is_active'])
        
        assert active_count == 2
        assert inactive_count == 1
    
    def test_list_diagnostics_empty_catalog(
        self,
        authenticated_psychologist_client
    ):
        response = authenticated_psychologist_client.get(
            '/api/diagnostics/catalog/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['data'] == []
    
    def test_list_diagnostics_includes_category_display(
        self,
        authenticated_psychologist_client,
        sample_diagnostics
    ):
        response = authenticated_psychologist_client.get(
            '/api/diagnostics/catalog/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        for diagnostic in response.data['data']:
            assert 'category_display' in diagnostic
            assert diagnostic['category_display'] in [
                'Discapacidad Física',
                'Discapacidad Sensorial Visual',
                'Discapacidad Sensorial Auditiva',
                'Discapacidad Cognitiva',
                'Discapacidad Psicosocial',
                'Discapacidad Múltiple',
                'Trastorno Específico del Aprendizaje',
                'TDAH',
                'Trastorno del Espectro Autista (TEA)',
                'Superdotación',
            ]
    
    def test_list_diagnostics_structure(
        self,
        authenticated_psychologist_client,
        sample_diagnostics
    ):
        response = authenticated_psychologist_client.get(
            '/api/diagnostics/catalog/'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'data' in response.data
        
        diagnostic = response.data['data'][0]
        assert 'id' in diagnostic
        assert 'code' in diagnostic
        assert 'name' in diagnostic
        assert 'category' in diagnostic
        assert 'category_display' in diagnostic
        assert 'description' in diagnostic
        assert 'is_active' in diagnostic
    
    def test_list_diagnostics_allowed_for_psychologist(
        self,
        authenticated_psychologist_client,
        sample_diagnostics
    ):
        response = authenticated_psychologist_client.get(
            '/api/diagnostics/catalog/'
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_diagnostics_allowed_for_admin(
        self,
        authenticated_admin_client,
        sample_diagnostics
    ):
        response = authenticated_admin_client.get(
            '/api/diagnostics/catalog/'
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_diagnostics_forbidden_for_teacher(
        self,
        api_client,
        mock_teacher_user,
        sample_diagnostics
    ):
        api_client.force_authenticate(
            user=mock_teacher_user,
            token={'role': 'TEACHER', 'status': 'ACTIVE'}
        )
        
        response = api_client.get('/api/diagnostics/catalog/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_diagnostics_forbidden_unauthenticated(
        self,
        api_client,
        sample_diagnostics
    ):
        response = api_client.get('/api/diagnostics/catalog/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test update diagnostic

    def test_update_diagnostic_success(
        self,
        authenticated_admin_client
    ):

        diagnostic = DiagnosticModel.objects.create(
            code="ADHD001",
            name="TDAH",
            category="ADHD",
            description="Inicial",
            is_active=True
        )

        data = {
            "code": "AUT001",
            "name": "Autismo",
            "category": "AUTISM_SPECTRUM",
            "description": "Actualizado"
        }

        response = authenticated_admin_client.patch(
            f"/api/diagnostics/catalog/{diagnostic.id}/",
            data=data,
            format="json"
        )

        assert response.status_code == status.HTTP_200_OK

        body = response.data

        assert body["data"]["code"] == "AUT001"
        assert body["data"]["name"] == "Autismo"
        assert body["data"]["category"] == "AUTISM_SPECTRUM"

    def test_update_diagnostic_not_found(
        self,
        authenticated_admin_client
    ):

        data = {
            "code": "AUT001",
            "name": "Autismo",
            "category": "AUTISM_SPECTRUM",
            "description": "Actualizado"
        }

        response = authenticated_admin_client.patch(
            "/api/diagnostics/catalog/999/",
            data=data,
            format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_diagnostic_invalid_data(
        self,
        authenticated_admin_client
    ):

        diagnostic = DiagnosticModel.objects.create(
            code="ADHD001",
            name="TDAH",
            category="ADHD",
            description="Inicial",
            is_active=True
        )

        data = {
            "code": "",
            "name": "",
            "category": "",
            "description": ""
        }

        response = authenticated_admin_client.patch(
            f"/api/diagnostics/catalog/{diagnostic.id}/",
            data=data,
            format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_diagnostic_duplicate_code(
        self,
        authenticated_admin_client
    ):

        DiagnosticModel.objects.create(
            code="AUT001",
            name="Autismo",
            category="AUTISM_SPECTRUM",
            description="Test",
            is_active=True
        )

        diagnostic = DiagnosticModel.objects.create(
            code="ADHD001",
            name="TDAH",
            category="ADHD",
            description="Inicial",
            is_active=True
        )

        data = {
            "code": "AUT001",
            "name": "Nuevo",
            "category": "ADHD",
            "description": "Actualizado"
        }

        response = authenticated_admin_client.patch(
            f"/api/diagnostics/catalog/{diagnostic.id}/",
            data=data,
            format="json"
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    # Deactivate diagnostic

    def test_deactivate_diagnostic_success(
        self,
        authenticated_admin_client
    ):

        diagnostic = DiagnosticModel.objects.create(
            code="ADHD001",
            name="TDAH",
            category="ADHD",
            description="Inicial",
            is_active=True
        )

        response = authenticated_admin_client.patch(
            f"/api/diagnostics/catalog/{diagnostic.id}/deactivate/"
        )

        assert response.status_code == status.HTTP_200_OK

        diagnostic.refresh_from_db()

        assert diagnostic.is_active is False

    def test_deactivate_diagnostic_not_found(
        self,
        authenticated_admin_client
    ):

        response = authenticated_admin_client.patch(
            "/api/diagnostics/catalog/999/deactivate/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_deactivate_diagnostic_forbidden_for_non_admin(
        self,
        authenticated_psychologist_client
    ):

        diagnostic = DiagnosticModel.objects.create(
            code="ADHD001",
            name="TDAH",
            category="ADHD",
            description="Inicial",
            is_active=True
        )

        response = authenticated_psychologist_client.patch(
            f"/api/diagnostics/catalog/{diagnostic.id}/deactivate/"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN