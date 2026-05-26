import pytest

from types import SimpleNamespace
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from students.models import StudentModel


@pytest.mark.django_db
class TestStudentViews:

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def secretary_user(self):
        return SimpleNamespace(
            is_authenticated=True,
            role='SECRETARY',
            status='ACTIVE',
            id=1
        )

    @pytest.fixture
    def normal_user(self):
        return SimpleNamespace(
            is_authenticated=True,
            role='PSYCHOLOGIST',
            status='ACTIVE',
            id=2
        )

    @pytest.fixture
    def authenticated_secretary_client(
        self,
        api_client,
        secretary_user
    ):
        token_payload = {
            'role': 'SECRETARY',
            'status': 'ACTIVE'
        }

        api_client.force_authenticate(user=secretary_user, token=token_payload)

        return api_client

    @pytest.fixture
    def authenticated_user_client(
        self,
        api_client,
        normal_user
    ):
        token_payload = {
            'role': 'PSYCHOLOGIST',
            'status': 'ACTIVE'
        }
        api_client.force_authenticate(user=normal_user, token=token_payload)
        return api_client

    @pytest.fixture
    def student(self):
        return StudentModel.objects.create(
            document_type='TI',
            document_number='1234567890',
            first_name='Juan',
            last_name='Pérez',
            date_of_birth='2010-05-15',
            gender='MALE',
            grade='5°',
            section='A',
            guardian_name='Carlos Pérez',
            guardian_phone='3001234567',
            guardian_email='carlos@example.com',
            guardian_relationship='Padre',
            consent_given=True,
            city='Cartagena',
            is_active=True
        )

    def test_student_register_success(
        self,
        authenticated_secretary_client,
        valid_student_data
    ):
        url = reverse('student-register')

        response = authenticated_secretary_client.post(
            url,
            valid_student_data,
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()

        assert data['message'] == 'Estudiante registrado exitosamente'
        assert data['data']['first_name'] == 'Juan'
        assert data['data']['document_number'] == '1234567890'

        assert StudentModel.objects.filter(
            document_number='1234567890'
        ).exists()

    def test_student_register_duplicate_document(
        self,
        authenticated_secretary_client,
        valid_student_data
    ):
        StudentModel.objects.create(
            document_type='TI',
            document_number='1234567890',
            first_name='Juan',
            last_name='Pérez',
            date_of_birth='2010-05-15',
            gender='MALE',
            grade='5°',
            guardian_name='Carlos Pérez',
            guardian_phone='3001234567',
            consent_given=True
        )

        url = reverse('student-register')

        response = authenticated_secretary_client.post(
            url,
            valid_student_data,
            format='json'
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert 'error' in response.json()

    def test_student_register_invalid_data(
        self,
        authenticated_secretary_client
    ):
        invalid_data = {
            'first_name': 'Juan'
        }

        url = reverse('student-register')

        response = authenticated_secretary_client.post(
            url,
            invalid_data,
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data = response.json()

        assert data['error'] == 'Datos inválidos'
        assert 'details' in data

    def test_student_register_requires_authentication(
        self,
        api_client,
        valid_student_data
    ):
        url = reverse('student-register')

        response = api_client.post(
            url,
            valid_student_data,
            format='json'
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_student_register_requires_secretary_role(
        self,
        authenticated_user_client,
        valid_student_data
    ):
        url = reverse('student-register')

        response = authenticated_user_client.post(
            url,
            valid_student_data,
            format='json'
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_student_list_success(
        self,
        authenticated_user_client
    ):
        StudentModel.objects.create(
            document_type='TI',
            document_number='1234567890',
            first_name='Juan',
            last_name='Pérez',
            date_of_birth='2010-05-15',
            gender='MALE',
            grade='5°',
            guardian_name='Carlos Pérez',
            guardian_phone='3001234567',
            consent_given=True
        )

        url = reverse('student-list')

        response = authenticated_user_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data['count'] == 1
        assert len(data['data']) == 1
        assert data['data'][0]['first_name'] == 'Juan'

    def test_student_list_requires_authentication(
        self,
        api_client
    ):
        url = reverse('student-list')

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_student_detail_success(
        self,
        authenticated_user_client
    ):
        student = StudentModel.objects.create(
            document_type='TI',
            document_number='1234567890',
            first_name='Juan',
            last_name='Pérez',
            date_of_birth='2010-05-15',
            gender='MALE',
            grade='5°',
            guardian_name='Carlos Pérez',
            guardian_phone='3001234567',
            consent_given=True
        )

        url = reverse(
            'student-detail',
            kwargs={'student_id': student.id}
        )

        response = authenticated_user_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data['id'] == student.id
        assert data['first_name'] == 'Juan'
        assert data['document_number'] == '1234567890'

    def test_student_detail_not_found(
        self,
        authenticated_user_client
    ):
        url = reverse(
            'student-detail',
            kwargs={'student_id': 999999}
        )

        response = authenticated_user_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

        data = response.json()

        assert data['error'] == 'Estudiante no encontrado'

    def test_student_detail_requires_authentication(
        self,
        api_client
    ):
        url = reverse(
            'student-detail',
            kwargs={'student_id': 1}
        )

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    #Update student

    def test_update_student_success(
        self,
        authenticated_secretary_client,
        student
    ):
        url = reverse(
            'update-student',
            kwargs={'student_id': student.id}
        )

        payload = {
            'first_name': 'Carlos',
            'grade': '6°',
            'section': 'B'
        }

        response = authenticated_secretary_client.patch(
            url,
            payload,
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert (
            data['message']
            == 'Estudiante actualizado exitosamente'
        )

        assert data['data']['first_name'] == 'Carlos'
        assert data['data']['grade'] == '6°'
        assert data['data']['section'] == 'B'

        student.refresh_from_db()

        assert student.first_name == 'Carlos'
        assert student.grade == '6°'
        assert student.section == 'B'

    def test_update_student_invalid_data(
        self,
        authenticated_secretary_client,
        student
    ):
        url = reverse(
            'update-student',
            kwargs={'student_id': student.id}
        )

        payload = {
            'guardian_email': 'correo-invalido'
        }

        response = authenticated_secretary_client.patch(
            url,
            payload,
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data = response.json()

        assert data['error'] == 'Datos inválidos'
        assert 'guardian_email' in data['details']

    def test_update_student_not_found(
        self,
        authenticated_secretary_client
    ):
        url = reverse(
            'update-student',
            kwargs={'student_id': 999999}
        )

        response = authenticated_secretary_client.patch(
            url,
            {
                'first_name': 'Carlos'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        data = response.json()

        assert 'error' in data

    def test_update_student_requires_authentication(
        self,
        api_client,
        student
    ):
        url = reverse(
            'update-student',
            kwargs={'student_id': student.id}
        )

        response = api_client.patch(
            url,
            {
                'first_name': 'Carlos'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_student_requires_secretary_role(
        self,
        authenticated_user_client,
        student
    ):
        url = reverse(
            'update-student',
            kwargs={'student_id': student.id}
        )

        response = authenticated_user_client.patch(
            url,
            {
                'first_name': 'Carlos'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    # Deactivate Student

    def test_deactivate_student_success(
        self,
        authenticated_secretary_client,
        student
    ):
        url = reverse(
            'deactivate-student',
            kwargs={'student_id': student.id}
        )

        response = authenticated_secretary_client.patch(url)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert (
            data['message']
            == 'Estudiante desactivado exitosamente'
        )

        assert data['student_id'] == student.id
        assert data['is_active'] is False

        student.refresh_from_db()

        assert student.is_active is False

    def test_deactivate_student_not_found(
        self,
        authenticated_secretary_client
    ):
        url = reverse(
            'deactivate-student',
            kwargs={'student_id': 999999}
        )

        response = authenticated_secretary_client.patch(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

        data = response.json()

        assert 'error' in data

    def test_deactivate_student_requires_authentication(
        self,
        api_client,
        student
    ):
        url = reverse(
            'deactivate-student',
            kwargs={'student_id': student.id}
        )

        response = api_client.patch(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_deactivate_student_requires_secretary_role(
        self,
        authenticated_user_client,
        student
    ):
        url = reverse(
            'deactivate-student',
            kwargs={'student_id': student.id}
        )

        response = authenticated_user_client.patch(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

        